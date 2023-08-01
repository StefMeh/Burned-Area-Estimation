# ************************************************************************************************************************************************************************************* #
# This script extracts burned area from dNBR outputs downloaded from the user's Google Drive, using ArcGIS Pro arcpy python environment. The script genererates an output shapefile
# (BurnedAreaAtlas.shp) of extracted burned areas with an individual identifier, approximated start- and end dates, and duration.
# The user needs/ can adjust the script where recommended (# <--).
# ************************************************************************************************************************************************************************************* #

import os
os.chdir(r'C:\Users\user\...\dNBR_Outputs') # <-- Specify working directory here!!!

import arcpy
from arcpy.sa import *
import os
import numpy as np
import pandas as pd

arcpy.env.overwriteOutput = True

for file in os.listdir(os.getcwd()):
    if file.startswith('dNBR') & file.endswith('.tif'):

        clusterId = file.split('_')[-1].split('.')[0]

        ### Total BA ###
        reclass_dnbr = Reclassify((os.path.join(os.getcwd(), file)), "Value", RemapRange([[-1500,100,0],[100,1500,1]]))
        if arcpy.sa.Raster(reclass_dnbr).maximum > 0:
             extract_dnbr = ExtractByAttributes(reclass_dnbr, "Value > 0")
             extract_dnbr.save((os.path.join(os.getcwd(), 'BA'+clusterId+'.tif')))

             arcpy.conversion.RasterToPolygon((os.path.join(os.getcwd(), 'BA'+clusterId+'.tif')), (os.path.join(os.getcwd(), 'BA'+clusterId+'.shp')), 'NO_SIMPLIFY', 'Value', 'MULTIPLE_OUTER_PART')

             arcpy.management.AddField((os.path.join(os.getcwd(), 'BA'+clusterId+'.shp')), 'ClusterID', 'LONG')

             with arcpy.da.UpdateCursor(os.path.join(os.getcwd(), 'BA'+clusterId+'.shp'), ['ClusterID']) as cursor:
                 for row in cursor:
                     row[0] = int(clusterId)
                     cursor.updateRow(row)


area_layer_list = []

for file in os.listdir(os.getcwd()):
    if file.startswith('BA') & file.endswith('.shp'):
        area_layer_list.append(file)

print(area_layer_list)

arcpy.management.Merge(area_layer_list, (os.path.join(os.getcwd(), 'BurnedAreaAtlas.shp')))

arcpy.management.CalculateGeometryAttributes(os.path.join(os.getcwd(), 'BurnedAreaAtlas.shp'), "AREA AREA_GEODESIC", '', "SQUARE_KILOMETERS", None, "SAME_AS_INPUT")

stdbscan_file = r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\updatedMFRdbscan\GEEFile(EPSG4326).shp'

arcpy.management.JoinField(os.path.join(os.getcwd(), 'BurnedAreaAtlas.shp'), 'ClusterID', stdbscan_file, 'CLUSTER_ID', ['START_TIME', 'END_TIME'])
