### Import os package & specify working directory ###
import os
os.chdir(r'C:\Users\user\Documents\.....\BA') # <-- Specify working directory here!!!

### Import packages from QGIS ###
from qgis._analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing
from qgis.core import QgsApplication
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

from PyQt5.QtCore import *
from PyQt5.QtCore import QVariant
from PyQt5 import QtCore

from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsVectorLayer,
    QgsField,
    QgsVectorDataProvider,
    QgsCoordinateReferenceSystem
)


### Files ###
input_csv = r'C:\Users\user\Documents\....\viirs_2012_Kenya.csv' # <-- NASA FIRMS VIIRS AFD.csv file for Kenya: Download: https://firms.modaps.eosdis.nasa.gov/country/
study_area_shp = r'C:\Users\user\Documents\...\StudyArea.shp' # <-- Shapefile of specific study area to clip AFDs (if applicable)

### Naming of Output Files ###
# File names can be changed here #
afd_pts = 'AFDs(EPSG4326).shp'                              # <-- AFD Point Shapefile: Generated from AFD Table (Coordinate system: WGS 84)
afd_pts23637 = 'AFDs(EPSG32637).shp'                        # <-- AFD Point Shapefile Projection (WGS 84 / UTM Zone 37N -> Kenya)
afd_pts23637clip = 'AFDs(EPSG32637)Clip.shp'                # <-- AFDs clipped to Study Area
clusters = 'stdbscan.shp'                                   # <-- Spation-temporal clustering output of AFDs using ST-DBSCAN Algorithm in QGIS (Tool: ST-DBSCAN Clustering)
cluster_buffers = 'stdbscanBuffers.shp'                     # <-- Buffers around AFD clusters (area approximation)
cluster_buffers_dissolve = 'stdbscanBuffersDissolve.shp'    #
cluster_info = 'stdbscanClusterInfo.shp'                    #
finalOutput = 'finalOutput.shp'                             # <-- AFD clusters associated with area (buffers) & information from clustering.
GEEUploadFile = 'GEEFile(EPSG4326).shp'                     # <-- Final file to be uploaded into GEE Asset (Coordinate System: WGS 84)

###Convert AFD.csv file into point layer (.shp file format)###
#Table to Point Layer#
processing.run("native:createpointslayerfromtable",{'INPUT':input_csv,
                                                     'XFIELD':'longitude',
                                                     'YFIELD':'latitude',
                                                     'ZFIELD':'',
                                                     'MFIELD':'',
                                                     'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                                     'OUTPUT':afd_pts})

#Reproject Point Layer to WGS 84 / UTM Zone 37N (UTM zone for Kenya: EPSD32637)#

processing.run("native:reprojectlayer",
               {'INPUT':afd_pts,
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:32637'),                                                              # Adjust projection parameters for study area!
                'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=utm +zone=37 +ellps=WGS84',    # Adjust projection parameters for study area!
                'OUTPUT':afd_pts23637})

#Extract AFDs for smaller study area other than country-level#
# Comment out step if not required #
processing.run("native:extractbylocation",
               {'INPUT':afd_pts23637,
                'PREDICATE':[0],
                'INTERSECT':study_area_shp,
                'OUTPUT':afd_pts23637clip})


layer = QgsVectorLayer(afd_pts23637clip, "VIIRS AFDs", "ogr")

#layer = QgsVectorLayer(afd_pts23637, "VIIRS AFDs", "ogr")    # !!! Uncomment & comment line above if AFDs were not clipped !!!


### Adds new field to shp file to store dates in DATE FORMAT ###
#Add Field#
layer_provider=layer.dataProvider()
layer_provider.addAttributes([QgsField("Date",QVariant.Date)])
layer.updateFields()

#Edit Field#
layer.startEditing()
for feature in layer.getFeatures():
    id = feature.id()

    date_string_format = feature['acq_date']
    
    m, d, y = list(map(int, date_string_format.split('/')))
    q_date_string = f'{y:04d}-{m:02d}-{d:02d}'
    qtDate = QtCore.QDate.fromString(q_date_string, 'yyyy-MM-dd')
    
    attr_value = {layer.fields().lookupField('Date'):qtDate}
    layer_provider.changeAttributeValues({id:attr_value})
layer.commitChanges()


### Performs ST-DBSCAN clustering of AFD pts ###
processing.run("native:stdbscanclustering",
               { 'DATETIME_FIELD' : 'Date',
                 'DBSCAN*' : False,
                 'EPS' : 750,                           # <-- Spatial Threshold: 750 meters
                 'EPS2' : 691200000,                    # <-- Temporal Threshold (millieseconds) = 8 days
                 'FIELD_NAME' : 'CLUSTER_ID',
                 'INPUT' : afd_pts23637clip,
                 #'INPUT' : afd_pts23637,            # !!! Uncomment & comment line above if AFDs were not clipped !!!
                 'MIN_SIZE' : 1,
                 'OUTPUT' : clusters,
                 'SIZE_FIELD_NAME' : 'CLUSTER_SIZE' })

### Create Buffer around AFD points to recreate pixel extent (375meters)###
processing.run("native:buffer",
               {'INPUT':clusters,
                'DISTANCE':375,
                'SEGMENTS':5,'END_CAP_STYLE':2,
                'JOIN_STYLE':0,
                'MITER_LIMIT':2,
                'DISSOLVE':True,
                'OUTPUT':cluster_buffers})

### Dissolve Buffer Features####
processing.run("native:dissolve",
               {'INPUT':cluster_buffers,
                'FIELD':[],'SEPARATE_DISJOINT':True,
                'OUTPUT':cluster_buffers_dissolve})

#Delete attribute fields & populate with cluster attribute fields#
layer = QgsVectorLayer(cluster_buffers_dissolve, "Cluster Buffers", "ogr")
layer_provider=layer.dataProvider()


layer.startEditing()
column2delete = layer.attributeList()
layer.dataProvider().deleteAttributes(column2delete)
layer.commitChanges()
        
processing.run("native:joinattributesbylocation",
               {'INPUT':cluster_buffers_dissolve,
                'PREDICATE':[0],
                'JOIN':clusters,
                'JOIN_FIELDS':[],
                'METHOD':1,
                'DISCARD_NONMATCHING':False,
                'PREFIX':'',
                'OUTPUT':cluster_info})

###Generate secondary buffer to extend pixel area###
processing.run("native:buffer",
               {'INPUT':cluster_info,
                'DISTANCE':250,
                'SEGMENTS':5,'END_CAP_STYLE':2,
                'JOIN_STYLE':0,
                'MITER_LIMIT':2,
                'DISSOLVE':False,
                'OUTPUT':finalOutput})

processing.run("native:reprojectlayer",
               {'INPUT':finalOutput,
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                'OPERATION':'+proj=pipeline +step +inv +proj=utm +zone=37 +ellps=WGS84 +step +proj=unitconvert +xy_in=rad +xy_out=deg',
                'OUTPUT':GEEUploadFile})

