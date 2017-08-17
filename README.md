# arcpy_climate
Process climate data using the arcpy package in python.

This spatial aggregation problem takes pixel-level climate variables (e.g. temperature) and aggregates to the U.S.-county level. That is, the temperature in a particular county is the weighted average of the pixels contained within the county's boundary. The variables are weighted by forest cover to reduce measurement error.

The desired output is a Nx2 matrix that stores the county identifier and climate value where N is the number of counties with forest cover. There are three inputs: the climate data in netcdf (.cdf) format, the county boundary in shapefile (.shp) format, and a forest cover layer in raster format (.tif).
