#created by Josh von Nonn
#built from source code provided by Brad Chmambers - based off Mungus et al.,2014.


### Optimized for removing pesky outliers from
### Bali dataset (Villa Batu Belig Sidemen)
### This level of outlier scrubbing is most likely
### not necessary for most datasets. There may be an
### issue that it removes small patches
### of ground points as well. -- needs further assessment

from scipy import ndimage, signal, spatial
from scipy.ndimage import morphology
import numpy as np
import pandas as pd
import pdal

import argparse

def idw(data):
    # Find indices of the ground returns,
    # i.e., anything that is not a nan, and create a KD-tree.
    # We will search this tree when looking for nearest
    # neighbors to perform the interpolation.
    valid = np.argwhere(~np.isnan(data))
    tree = spatial.cKDTree(valid)
    
    # Now find indices of the non-ground returns,
    # as indicated by nan values. We will interpolate
    # at these locations.
    nans = np.argwhere(np.isnan(data))    
    for row in nans:
        d, idx = tree.query(row, k=12) #k = number of nearest neighbors
        d = np.power(d, -2) #each item in d raised to its reciprocated power (basis of idw) the value "r" also defines the smoothness of the interpolation
        v = data[valid[idx, 0], valid[idx, 1]] 
        data[row[0], row[1]] = np.inner(v, d)/np.sum(d) #nans are replaced with the result of (v * d)/sum(d)
        
    return data

def dmpdtm(inputfile,
           the_S, the_k, the_n, the_b, horizontal_resolution): 
    # read in in full res .las , subsampled with
    # Poisson, change radius to reach desired resolution
    p = (pdal.Reader.las(inputfile).pipeline() |
         pdal.Filter.sample(radius=1).pipeline() |
         pdal.Filter.outlier(mean_k=17,multiplier=0.35).pipeline() |
         pdal.Filter.range(limits="Classification[0:6]").pipeline())
    p.execute()

    # create a one dimensional array from the
    # "Classification" column
    cls = p.arrays[0]['Classification']
    # set the array to all ones
    cls.fill(1)

    # convert X,Y, and Z data to a pandas dataframe
    df3D = pd.DataFrame(p.arrays[0], columns=['X','Y','Z'])

    # define variables (if we keep k = 0, then I'll clean
    # up the code, remove gstar?)

    S = the_S
    k = the_k
    n = the_n
    b = the_b
    hres = horizontal_resolution

    # np.ogrid "open-grid", creates a way to index
    # the matrix (access pixels/pts) hres is the step
    xi = np.ogrid[p.arrays[0]['X'].min():p.arrays[0]['X'].max():hres]
    yi = np.ogrid[p.arrays[0]['Y'].min():p.arrays[0]['Y'].max():hres]

    # np.digitize allocates points to bins and
    # then bins are grouped in the df
    bins = df3D.groupby([np.digitize(p.arrays[0]['X'], xi), np.digitize(p.arrays[0]['Y'], yi)])

    zmins = bins.Z.min() #collects the lowest point in each bin
    cz = np.empty((yi.size, xi.size)) 
    cz.fill(np.nan) 
    for name, val in zmins.iteritems():
        cz[name[1]-1, name[0]-1] = val #adding coordinates to lowest points only

    cz = idw(cz)

    ### STARTING MORPOLOGICAL GRADIENTS

    erosions = []
    granulometry = []
    erosions.append(morphology.grey_erosion(cz, size=3))
    for scale in range(1, S):
        erosions.append(morphology.grey_erosion(
            erosions[scale-1], size=3))
    for scale in range(1, S+1):
        granulometry.append(
            morphology.grey_dilation(erosions[scale-1],
                                     size=2*scale+1))

    out = []
    for i in range(1, len(granulometry)):
        out.append(granulometry[i-1]-granulometry[i])

    gprime = np.maximum.reduce(out)
  
    Sg = gprime < n

    F = cz.copy()
    F[np.where(Sg==0)] = np.nan

    G = idw(F)

    struct = ndimage.iterate_structure(
        ndimage.generate_binary_structure(2, 1), 1).astype(int)
    gradDTM = morphology.grey_dilation(G, structure=struct)

    xbins = np.digitize(df3D.X, xi)
    ybins = np.digitize(df3D.Y, yi)
    nonground = np.where(df3D.Z >= gradDTM[ybins-1, xbins-1]+b)
    ground = np.where(df3D.Z < gradDTM[ybins-1, xbins-1]+b)

    cls[ground] = 2 #set ground points to 2

    output = p.arrays[0]
    output['Classification'] =cls

    p = pdal.Filter.range(
        limits="Classification[2:2]").pipeline(output)
    p.execute()

    # default Progressive morphological filter stacked
    # to catch stragglers (haven't tested with alt parameters)
    # need to test with alt smrf --compare computation time
    pmf_arr = p.arrays[0]
    p = (pdal.Filter.outlier().pipeline(pmf_arr) |
         pdal.Filter.pmf().pipeline() |
         pdal.Filter.range(limits="Classification[2:2]").pipeline())
    p.execute()

    # writeout las file with ground points only 
    outputfile = inputfile.replace(".laz","_dtm.las")
    final_out = p.arrays[0]
    p = pdal.Writer.las(filename = outputfile).pipeline(final_out)
    p.execute()

if __name__ == '__main__':
    """
    Takes a point cloud in .laz format as main argument,
    And some numerical parameters as optional flag arguments.
    """
    p = argparse.ArgumentParser()
    
    p.add_argument('infile',
                   help = "Input file, a point cloud in .laz format")
    p.add_argument('-S', '--the_S', type = int,
                   default = 10, help =
                   'a parameter called S')
    p.add_argument('-k', '--the_k', type = float,
                   default = 0.0, help =
                   'a parameter called k')
    p.add_argument('-n', '--the_n', type = float,
                   default = 0.5, help =
                   'a parameter called n')
    p.add_argument('-b', '--the_b', type = float,
                   default = -0.2, help =
                   'a parameter called b')
    p.add_argument('-hres', '--horizontal_resolution',
                   type = float, default = 1.0, help =
                   'The desired horizontal resolution of the '\
                   'output file in meters')
    
    args = p.parse_args()
    dmpdtm(args.infile, args.the_S, args.the_k, args.the_n,
           args.the_b, args.horizontal_resolution)
