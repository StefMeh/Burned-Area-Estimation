import os
os.chdir(r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\updatedMFRdbscan') # <-- Specify working directory here!!!

import arcpy
from arcpy.sa import *
import numpy as np
import pandas as pd

arcpy.env.overwriteOutput = True

###Documentation Density-based clustering tool in arcpy###
#--- https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/densitybasedclustering.htm ---#

### Files ###
#input_csv = r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\VIIRS_Fires\viirs_2012_Kenya.csv' # <-- NASA FIRMS VIIRS AFD.csv file for Kenya
input_csv = r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\updatedMFRdbscan\Kenya2012-2022.csv'
study_area_shp = r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\MFR_Forest\Forest_Reserve\MFR_Forest_Reserve.shp'

afd_pts = 'AFDs.shp'
afd_ptsEPSG4326 = 'AFDsEPSG4326.shp'
afd_ptsEPSG4326clip = 'AFDsEPSG4326Clip.shp'
clusters = 'stdbscan.shp'
cluster_buffers = 'stdbscanBuffers.shp'
cluster_buffers_dissolve = 'stdbscanBuffersDissolve.shp'
cluster_info = 'stdbscanClusterInfo.shp'
finalOutput = 'finalOutput.shp'
GEEUploadFile = 'GEEFileEPSG4326.shp'


###Convert AFD.csv file into point layer (.shp file format)###
#Table to Point Layer#
arcpy.management.XYTableToPoint(input_csv, os.path.join(os.getcwd(), afd_pts), 'longitude', 'latitude')

#Project AFDs to EPSG 4326#
arcpy.management.Project((os.path.join(os.getcwd(), afd_pts)), (os.path.join(os.getcwd(), afd_ptsEPSG4326)), 4326)

#Extract AFDs for smaller study area than the country-level#
arcpy.analysis.Clip(os.path.join(os.getcwd(), afd_ptsEPSG4326), study_area_shp , os.path.join(os.getcwd(), afd_ptsEPSG4326clip))

### Performs ST-DBSCAN clustering of AFD pts ###
# --> Spatial threshold: 562 meters#
# --> Temporal threshold: 16 days#
# --> Minimum cluster size: 2 pts#
arcpy.stats.DensityBasedClustering(os.path.join(os.getcwd(), afd_ptsEPSG4326clip), os.path.join(os.getcwd(), clusters), 'DBSCAN', 2, '562 Meters', None, 'acq_date', '16 Days')

with arcpy.da.SearchCursor(os.path.join(os.getcwd(), clusters), ['CLUSTER_ID']) as cursor:
    maxId = -1
    for row in cursor:
        if row[0] > maxId:
            maxId = row[0]

with arcpy.da.UpdateCursor(os.path.join(os.getcwd(), clusters), ['CLUSTER_ID']) as cursor:
    for row in cursor:
        if row[0] == -1:
            maxId += 1
            row[0] = maxId
            cursor.updateRow(row)
            
### Create Buffer around AFD points to define area of evaluation (buffer > 375m)###
arcpy.analysis.Buffer(os.path.join(os.getcwd(), clusters), os.path.join(os.getcwd(), cluster_buffers), "562 Meters", "FULL", "ROUND", "LIST", "CLUSTER_ID")

join = arcpy.management.JoinField(os.path.join(os.getcwd(), cluster_buffers), 'CLUSTER_ID', os.path.join(os.getcwd(), clusters), 'CLUSTER_ID', ['START_TIME', 'END_TIME'])

arcpy.management.CopyFeatures(join, os.path.join(os.getcwd(), GEEUploadFile))




        


