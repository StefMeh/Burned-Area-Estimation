# Moderate Resolution Burned Area Estimation
The repository provides code resources to estimate burned area based on a combination of VIIRS Active Fire Detections (AFDs), acquired from NASA's Fire Information for Resource Management System (FIRMS), part of NASA's Earth Observing System Data and Information System (EOSDIS), and Landsat 7 &amp; 8 atmospherically corrected surface reflectance data made available through the US Geological Survey (USGS), and accessible through the Google Earth Engine (GEE) platform.

# Introduction

# Data Acquisition
Active Fire Detections Download -> NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/download/

# Fire Events & Duration Approximation
Active Fire Detections (AFDs) are spatio-temporally clustered to add information to the data by developing an estimate of individual fire events. Spatio-temporal clustering allows to assign approximate fire start- and end dates, based on AFDs' acquisition dates, and an approximate fire extent, based on AFDs' spatial resolution (375 meters) to estimated fire events.

Spatio-temporal clustering can be performed using the Density-based Clustering tool in ArcGIS Pro, or the ST-DBSCAN Clustering tool in QGIS. The tool performs ST-DBSCAN (Spatio-Temporal Density-Based Spatial Clustering of Applications with Noise), a clustering algorithm for vector data originally developed by Ester et al. (1996) and further developed by Birant & Kut (2007).

(Use either stdbscanArcGISPro3.py or stdbscanQGIS.py)

## Tool Documentation
Density-based Clustering (ArcGIS Pro): https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/densitybasedclustering.htm
ST-DBSCAN Clustering (QGIS): https://docs.qgis.org/3.28/en/docs/user_manual/processing_algs/qgis/vectoranalysis.html#st-dbscan-clustering

## Further Resources
Ester, Martin, et al. "A density-based algorithm for discovering clusters in large spatial databases with noise." kdd. Vol. 96. No. 34. 1996.
Birant, Derya, and Alp Kut. "ST-DBSCAN: An algorithm for clustering spatial–temporal data." Data & knowledge engineering 60.1 (2007): 208-221.

Humber, Michael, Maria Zubkova, and Louis Giglio. "A remote sensing-based approach to estimating the fire spread rate parameter for individual burn patch extraction." International Journal of Remote Sensing 43.2 (2022): 649-673.
Artés, Tomàs, et al. "A global wildfire dataset for the analysis of fire regimes and fire behaviour." Scientific data 6.1 (2019): 296.

# dNBR Generation
The approximate extent of spatio-temporal clusters of AFDs is integrated into a cloud-based Google Earth Engine (GEE) workflow, assessing Landsat atmospherically corrected surface reflectance data to calculate differenced Normalized Burn Ratio (dNBR). Imagery is acquired for uniform pre- and post-fire periods of 120 days, respectively, and averaged, before calculating dNBR.

(Use either GEEdNBRGeneration.js or JNdNBRGeneration.ipynb)

## Further Resources
Key, Carl H., and Nathan C. Benson. "Landscape assessment (LA)." FIREMON: Fire effects monitoring and inventory system 164 (2006): LA-1.
Miller, Jay D., and Andrea E. Thode. "Quantifying burn severity in a heterogeneous landscape with a relative version of the delta Normalized Burn Ratio (dNBR)." Remote sensing of Environment 109.1 (2007): 66-80.

# Burned Area Extraction
Derived burn severity (dNBR) is classified based on the classification system for dNBR by Key & Benson (2006). Burn perimeters are extracted for a severity classification of low to high severity.

(Use either dNBRProcessingArcGISPro3.py or dNBRProcessingQGIS.py)

## Further Resources
Key, Carl H., and Nathan C. Benson. "Landscape assessment (LA)." FIREMON: Fire effects monitoring and inventory system 164 (2006): LA-1.

# Resources on Installations & Accounts
## Accounts
### Google Earth Engine
https://earthengine.google.com/
## Installations
### Anaconda
https://docs.anaconda.com/free/anaconda/install/
### ArcPy
https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/installing-arcpy.htm
### QGIS
https://anaconda.org/conda-forge/qgis
### geemap
https://github.com/gee-community/geemap.git
