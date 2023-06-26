import os
os.chdir(r'C:\Users\user\Documents\...\BA_dNBR') # <-- Specify working directory here!!!

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

from osgeo import gdal, ogr, osr

for file in os.listdir(os.getcwd()):
    if file.startswith('dNBR') & file.endswith('.tif'):

        clusterId = file.split('_')[-1].split('.')[0]

        processing.run("native:reclassifybytable",
                       {'INPUT_RASTER':os.path.join(os.getcwd(), file),
                        'RASTER_BAND':1,
                        'TABLE':['-1500','100','0','100','1500','1'],
                        'NO_DATA':0,
                        'RANGE_BOUNDARIES':1,
                        'NODATA_FOR_MISSING':False,
                        'DATA_TYPE':2,
                        'OUTPUT':'BA'+clusterId+'.tif'})


        src_ds = gdal.Open('BA'+clusterId+'.tif')
        srcband = src_ds.GetRasterBand(1)
        dst_layername = 'BA'
        drv = ogr.GetDriverByName("ESRI Shapefile")
        dst_ds = drv.CreateDataSource('BA'+clusterId+'.shp')

        sp_ref = osr.SpatialReference()
        sp_ref.SetFromUserInput('EPSG:4326')

        dst_layer = dst_ds.CreateLayer(dst_layername, srs = sp_ref )

        fld = ogr.FieldDefn("BA(sqkm)", ogr.OFTInteger)
        dst_layer.CreateField(fld)
        dst_field = dst_layer.GetLayerDefn().GetFieldIndex("BA(sqkm)")

        gdal.Polygonize(srcband, None, dst_layer, dst_field, [], callback=None )

        del src_ds
        del dst_ds

        processing.run("native:reprojectlayer",
               {'INPUT':'BA'+clusterId+'.shp',
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:32637'),
                'OPERATION':'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=utm +zone=37 +ellps=WGS84',
                'OUTPUT':'BAProj'+clusterId+'.shp'})

        layer = QgsVectorLayer('BAProj'+clusterId+'.shp', "BA"+clusterId, "ogr")

        layer.startEditing()

        layer.startEditing()
        
        selection = QgsFeatureRequest().setFilterExpression('"BA(sqkm)" != 1')

        for feature in layer.getFeatures(selection):
            layer.deleteFeature(feature.id())

        layer.commitChanges()

