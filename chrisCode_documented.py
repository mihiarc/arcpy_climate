# Import arcpy module
import arcpy
import os # access operating system
import shutil # dumps unnecessary files from arcpy
import re # regular expression
from datetime import datetime
arcpy.env.overwriteOutput = True

# set parameters and variables

varScenario = "tasmin\\rcp85\\" # folder w/netcdf's of interest

## Declare inputs for netcdf function
climate_model = "IPSL_CM5B_LR" # folder name for output labeling 
x_dimension = "lon" 
y_dimension = "lat"
band_dimension = ""
valueSelectionMethod = "BY_VALUE" 

## netcdf is a three-dimensional object (could be more), need to declare dimension we want to access
dimension = "time" # what we are going to loop over

## declaring files for extraction 
counties = "D:\GroupWork\Climate Data\Spatial Files\Census Boundaries\conus_county.shp" # shapefile for aggregation 
directory = "D:\\GroupWork\\Climate Data\\Forest Climate\\MACA Forest Climate\\IPSL_CM5B_LR\\" # directory shortcut (can't set working directory like in other programs)
forest_cover = "D:\\GroupWork\\Climate Data\\Spatial Files\\forest_cover_by_fortyp.tif" # weighting measure, weighting climate variable by forest cover; essentially a clip to be fed to an aggregation
# (I'll be able to skip forst_cover since mine is a finer spatial scale)


for fn in os.listdir(directory + varScenario): # loops over the files in the declared folder and makes a list of them, then loop over the list 
    climate_variable = re.search('_(.+?)_', fn).group(1) # pulls apart the file name to give parameters from MACA
    if climate_variable == 'tasmax' or climate_variable == 'tasmin': # if file name is.... 
        variable = 'air_temperature' # variable will be air temp
    if climate_variable == 'pr': # if file name is ... 
            variable = 'precipitation' # variable is precipitation 
    scenario = re.search('r1i1p1_(.+?)_',fn).group(1) # pull apart file name for scenario 
    inNetCDF = directory + varScenario + fn # raw netcdf filename and location 
    
    nc_FP = arcpy.NetCDFFileProperties(inNetCDF) # gives netcdf metadata 
    nc_Dim = nc_FP.getDimensions() # dimensions of netcdf from metadata, we will be looping over these dimensions 

    for dimension in nc_Dim: # looping over dimensions 
        if dimension == "time": # only want to loop over time 
            top = nc_FP.getDimensionSize(dimension) # highest dimension (ex: netcdf with 1 year of monthly observations, top = 12)
            for i in range(0, top): # looping over every time unit 
                dimension_values = nc_FP.getDimensionValue(dimension, i) # time unit w/in range of time dimension
                nowDate = datetime.strftime(datetime.strptime(dimension_values, '%x'),'%m%Y') # formats i to month/year 

                arcpy.MakeNetCDFRasterLayer_md(inNetCDF, variable, x_dimension, y_dimension, nowDate, band_dimension, [[dimension, dimension_values]], valueSelectionMethod) # extract netcdf to raster

                os.makedirs(directory + "temp\\") # make teporary directory for all files, temp directory allows for easy dumping of intermediate files 
                outFile = directory + "temp\\" + nowDate # name format of output files (table)

                arcpy.CopyRaster_management(nowDate, outFile + ".tif", "", "", "", "NONE", "NONE", "") # fix datum problem? 
                
                climate_raster = outFile + ".tif" # name for saved raster 
                county_output = directory + "arcpy_output\\" + climate_variable + "_" + climate_model + "_" + scenario + "_" + nowDate + ".dbf" # output name (currently creating this folder manually)
                extract = directory + "temp\\extract.tif" # extraction file for weighting (specific to Chris' processing)

                arcpy.CheckOutExtension('Spatial')
                arcpy.gp.ExtractByMask_sa(climate_raster,forest_cover,extract) # extract by forest cover, creates another raster (I may skip?) 
                arcpy.gp.ZonalStatisticsAsTable_sa(counties,"GEOID",climate_raster,county_output,"DATA","ALL") # extraction by spatial unit, two dimensional table 
                arcpy.CheckInExtension('Spatial') # make sure to do this, otherwise creates conflics with other users, and yourself :)... because arcpy is stupid as fuck


                shutil.move(directory + "arcpy_output\\" + climate_variable + "_" + climate_model + "_" + scenario + "_" + nowDate + ".cpg",
                        directory + "temp\\" + climate_variable + climate_model + scenario + nowDate + ".cpg") # moves .cpg to temp folder for delete
                shutil.move(directory + "arcpy_output\\" + climate_variable + "_" + climate_model + "_" + scenario + "_" + nowDate + ".dbf.xml",
                        directory + "temp\\" + climate_variable + "_" + climate_model + "_" + scenario + "_" + nowDate + ".dbf.xml") # moves .dbf.xml to temp folder for delete 
                shutil.rmtree(directory + "temp\\") # deletes temp folder 

            
                print "success " + nowDate + " " + climate_variable + " " + climate_model + " " + scenario #YAY YOU DID IT!!! 
