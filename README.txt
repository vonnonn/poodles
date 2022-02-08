source code found at -

https://github.com/chambbj/pdal-notebook/blob/9195838a14f88a543bbe2a8dacf3649cadc66eae/notebooks/DMP.ipynb


The tweeks..

Parameters: (these settings were optimized with a Poisson filter at Radius = 1. I would also suggest setting hres to 1)

	s= 20
	k= 0
	n= 0.1
	b= -0.2

I also stacked a default PMF filter and a cell to write out the final ground points.

*note - It was crucial on my tequitor for processing time to keep the point density around 1pts/m^2 (Yes, my CPU is a burrito).
