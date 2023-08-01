# ************************************************************************************************************************************************************************************* #
# This script extracts burned area from dNBR outputs downloaded from the user's Google Drive, using the QGIS python environment. The script genererates an output shapefile
# (BurnedAreaAtlas.shp) of extracted burned areas with an individual identifier and an approximated start date.
# The user needs/ can adjust the script where recommended (# <--).
# ************************************************************************************************************************************************************************************* #

### Import os package & specify working directory ###
import os
os.chdir(r'C:\Users\user\...\dNBR_Outputs') # <-- Specify working directory here!!!
# BA_dNBR directory contains GEE dNBR output files (.tif format) #

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
    QgsFeatureRequest,
    QgsVectorLayer,
    QgsField,
    QgsVectorDataProvider,
    QgsCoordinateReferenceSystem
)

### Import gdal package ###
from osgeo import gdal, ogr, osr

### Access dNBR.tif files in working directory ###
for file in os.listdir(os.getcwd()):
    if file.startswith('dNBR') & file.endswith('.tif'):

        clusterId = file.split('_')[-1].split('.')[0]

        # Reclassify raster: dNBR is classified as 'Burn' (1) or 'No Burn' (0) #
        processing.run("native:reclassifybytable",
                       {'INPUT_RASTER':os.path.join(os.getcwd(), file),
                        'RASTER_BAND':1,
                        'TABLE':['-1500','100','0','100','1500','1'],
                        'NO_DATA':0,
                        'RANGE_BOUNDARIES':1,
                        'NODATA_FOR_MISSING':False,
                        'DATA_TYPE':2,
                        'OUTPUT':'BA'+clusterId+'.tif'})

        # Convert .tif to .shp file #
        src_ds = gdal.Open('BA'+clusterId+'.tif')
        srcband = src_ds.GetRasterBand(1)
        dst_layername = 'BA'
        drv = ogr.GetDriverByName("ESRI Shapefile")
        dst_ds = drv.CreateDataSource('BA'+clusterId+'.shp')

        sp_ref = osr.SpatialReference()
        sp_ref.SetFromUserInput('EPSG:4326')

        dst_layer = dst_ds.CreateLayer(dst_layername, srs = sp_ref )

        fld = ogr.FieldDefn("Class", ogr.OFTInteger)
        dst_layer.CreateField(fld)
        dst_field = dst_layer.GetLayerDefn().GetFieldIndex("Class")

        gdal.Polygonize(srcband, None, dst_layer, dst_field, [], callback=None )

        del src_ds
        del dst_ds

        # 
        processing.run("native:reprojectlayer",
               {'INPUT':'BA'+clusterId+'.shp',
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:32637'),
                'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=utm +zone=37 +ellps=WGS84',
                'OUTPUT':'BAProj'+clusterId+'.shp'})

        # Remove 'No Burn' class from .shp file #
        layer = QgsVectorLayer('BAProj'+clusterId+'.shp', "BA"+clusterId, "ogr")
        layer.startEditing()        
        selection = QgsFeatureRequest().setFilterExpression('"Class" != 1')

        for feature in layer.getFeatures(selection):
            layer.deleteFeature(feature.id())

        layer.commitChanges()

        processing.run("native:dissolve", {'INPUT':'BAProj'+clusterId+'.shp',
                                           'FIELD' : [],
                                           'SEPARATE_DISJOINT':False,
                                           'OUTPUT':'BADissolve'+clusterId+'.shp'})
        
        processing.run("native:fieldcalculator",
                       {'INPUT':'BADissolve'+clusterId+'.shp',
                        'FIELD_NAME':'Area(sqkm)',
                        'FIELD_TYPE':0,'FIELD_LENGTH':0,
                        'FIELD_PRECISION':0,
                        'FORMULA':' $area / 1000000',
                        'OUTPUT':'Area'+clusterId+'.shp'})








        layer = QgsVectorLayer('Area'+clusterId+'.shp', "BA Area", "ogr")

        ### Adds new field to shp file to store ClusterID ###

        #Add field in date format#
        layer_provider=layer.dataProvider()
        layer_provider.addAttributes([QgsField("ClusterId",QVariant.Int)])
        layer.updateFields()

        #Edit field#
        layer.startEditing()

        for feature in layer.getFeatures():
            id = feature.id()
            
            attr_value = {layer.fields().lookupField('ClusterId'):int(clusterId)}
            layer_provider.changeAttributeValues({id:attr_value})

        layer.commitChanges()

#
area_layer_list = []

for file in os.listdir(os.getcwd()):
    if file.startswith('Area') & file.endswith('.shp'):
        area_layer_list.append(file)

processing.run("native:mergevectorlayers",
               {'LAYERS':area_layer_list,
                'CRS':QgsCoordinateReferenceSystem('EPSG:32637'),
                'OUTPUT':'BurnedAreaAtlas.shp'})


