source code found at -

https://github.com/chambbj/pdal-notebook/blob/9195838a14f88a543bbe2a8dacf3649cadc66eae/notebooks/DMP.ipynb


The tweaks..

Parameters: (these settings were optimized with a Poisson filter at Radius = 1. I would also suggest setting hres to 1)

	s= 20
	k= 0
	n= 0.1
	b= -0.2

I also stacked a default PMF filter and a cell to write out the final ground points.

*note - It was critical for my tequitor's processing time to keep the point density around 1pts/m^2 (Yes, my CPU is a burrito).

# Setup

If you have a Debian or Ubuntu environment, there's a setup script that stands a decent chance of getting you going with a local Python environment.

_Note: using Conda instead of python-venv, because the PDAL developers provide their latest packages directly to the Conda Forge repos, but putting the environment in a subdirectory within the project directory, which maybe keeps things cleaner._

Clone this repo, cd into it, and type
```
script/setup.sh
```

If you don't have a Conda environment, it's going to try to install one, which might require a sudo password.

Once it's done, you need to activate the environment with

```
conda activate ./envs
```

At which point you can probably start filtering point cloud files in .laz format with

```
python3 app/dtm_filter.py <inputfile>
```

If you know what the various parameters mean, you can set them like so:

```
python3 app/dtm_filter.py <inputfile> -S 10 -k 0.0 -n 0.5 -b -0.2 -hres 1.0
```

(those are actually the default values, which will be used if you don't specify any parameters at all).
