import os
os.chdir(r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\VIIRS_Fires') # <-- Specify working directory here!!!

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
#input_csv = 'MFR_Fire_HS_Table2012.csv' # <-- NASA FIRMS VIIRS AFD.csv file
input_csv = r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\VIIRS_Fires\viirs_2012_Kenya.csv' # <-- NASA FIRMS VIIRS AFD.csv file for Kenya
study_area_shp = r'C:\Users\Stephanie\Documents\Thesis\Thesis_Data\MFR_Forest\Forest_Reserve\MFR_Forest_Reserve.shp'

afd_pts = 'AFDs(EPSG4326).shp'
afd_pts23637 = 'AFDs(EPSG32637).shp'
afd_pts23637clip = 'AFDs(EPSG32637)Clip.shp'
clusters = 'stdbscan.shp'
cluster_buffers = 'stdbscanBuffers.shp'
cluster_buffers_dissolve = 'stdbscanBuffersDissolve.shp'
cluster_info = 'stdbscanClusterInfo.shp'
finalOutput = 'finalOutput.shp'
GEEUploadFile = 'GEEFile(EPSG4326).shp'

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
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:32637'),
                'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=utm +zone=37 +ellps=WGS84',
                'OUTPUT':afd_pts23637})

#Extract AFDs for smaller study area than the country-level#
processing.run("native:extractbylocation",
               {'INPUT':afd_pts23637,
                'PREDICATE':[0],
                'INTERSECT':study_area_shp,
                'OUTPUT':afd_pts23637clip})


layer = QgsVectorLayer(afd_pts23637clip, "VIIRS AFDs", "ogr")

### Adds new field to shp file to store dates in date format ###

#Add field in date format#
layer_provider=layer.dataProvider()
layer_provider.addAttributes([QgsField("Date",QVariant.Date)])
layer.updateFields()

#Edit field#
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
                 'EPS' : 750,                           # <-- Spatial Threshold
                 'EPS2' : 691200000,                    # <-- Temporal Threshold (millieseconds) = 8 days
                 'FIELD_NAME' : 'CLUSTER_ID',
                 'INPUT' : afd_pts23637clip,
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

