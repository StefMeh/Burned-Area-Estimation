# Moderate Resolution Burned Area Estimation
The repository provides code resources to estimate burned area based on a combination of VIIRS Active Fire Detections (AFDs), acquired from NASA's Fire Information for Resource Management System (FIRMS), part of NASA's Earth Observing System Data and Information System (EOSDIS), and Landsat 7, 8 & 9 atmospherically corrected surface reflectance data made available through the US Geological Survey (USGS), and accessible through the Google Earth Engine (GEE) platform. The workflow is devided in three steps, using separate code scripts: 1) Fire Events & Duration Approximation (stdbscanArcGISPro3.py or stdbscanQGIS.py), 2) dNBR Generation (GEEdNBRGeneration.js or JNdNBRGeneration.ipynb), and 3) Burned Area Extraction (dNBRProcessingArcGISPro3.py or dNBRProcessingQGIS.py). User requirements include an ArcPy or QGIS python environment, a Google Earth Engine Account, and potentially a geemap python environment.

# Introduction
Global burned area products show high errors of commission in agricultural settings related to subsidence farming, involving anthropogenic fire activity for land clearing and field preparation, pre- and post-harvest. Burned areas < 100 hectares are laregely not registered by global burned area products, and not accounted for in land management or national to global greehouse gas inventories. This is an issue especially in low-income countries, where resources are limited to develop continuous operational fire and burned area monitoring services based on higher spatial resolution data (20 - 30 meter spatial resolution). The repository provides open-source resources to generate information on fire events and associated burned area over any study area, to support higher accuracy burned area monitoring.

# Data
Active Fire Detections Download -> NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/download/

# (1) Fire Events & Duration Approximation
Active Fire Detections (AFDs) are spatio-temporally clustered to add information to the data by developing an estimate of individual fire events. Spatio-temporal clustering allows to assign approximate fire start- and end dates, based on AFDs' acquisition dates, and an approximate fire extent, based on AFDs' spatial resolution (375 meters) to estimate fire events.

Spatio-temporal clustering can be performed using the Density-based Clustering tool in ArcGIS Pro, or the ST-DBSCAN Clustering tool in QGIS. The tool performs ST-DBSCAN (Spatio-Temporal Density-Based Spatial Clustering of Applications with Noise), a clustering algorithm for vector data originally developed by Ester et al. (1996) and further developed by Birant & Kut (2007).

(Use either stdbscanArcGISPro3.py or stdbscanQGIS.py)

## Requirements
Either an ArcPy or QGIS python environment.

## Tool Documentation
* Density-based Clustering (ArcGIS Pro): https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/densitybasedclustering.htm
* ST-DBSCAN Clustering (QGIS): https://docs.qgis.org/3.28/en/docs/user_manual/processing_algs/qgis/vectoranalysis.html#st-dbscan-clustering

## Further Resources
(ST-)DBSCAN
* Ester, Martin, et al. "A density-based algorithm for discovering clusters in large spatial databases with noise." kdd. Vol. 96. No. 34. 1996.
* Birant, Derya, and Alp Kut. "ST-DBSCAN: An algorithm for clustering spatial–temporal data." Data & knowledge engineering 60.1 (2007): 208-221.

ST-DBSCAN in Fire Research
* Humber, Michael, Maria Zubkova, and Louis Giglio. "A remote sensing-based approach to estimating the fire spread rate parameter for individual burn patch extraction." International Journal of Remote Sensing 43.2 (2022): 649-673.
* Artés, Tomàs, et al. "A global wildfire dataset for the analysis of fire regimes and fire behaviour." Scientific data 6.1 (2019): 296.

# (2) dNBR Generation
The approximate extent of spatio-temporal clusters of AFDs is integrated into a cloud-based Google Earth Engine (GEE) workflow, assessing Landsat atmospherically corrected surface reflectance data to calculate differenced Normalized Burn Ratio (dNBR). Imagery is acquired for uniform pre- and post-fire periods and averaged before calculating dNBR.

(Use either GEEdNBRGeneration.js or JNdNBRGeneration.ipynb)

## Requirements
A Google Earth Engine account, or a Google Earth Engine account and a geemap python environment.

## Further Resources
NBR / dNBR
* Key, Carl H., and Nathan C. Benson. "Landscape assessment (LA)." FIREMON: Fire effects monitoring and inventory system 164 (2006): LA-1.
* Miller, Jay D., and Andrea E. Thode. "Quantifying burn severity in a heterogeneous landscape with a relative version of the delta Normalized Burn Ratio (dNBR)." Remote sensing of Environment 109.1 (2007): 66-80.

# (3) Burned Area Extraction
Derived burn severity (dNBR) is classified based on the classification system for dNBR by Key & Benson (2006). Burn perimeters are extracted for a severity classification of low to high severity.

(Use either dNBRProcessingArcGISPro3.py or dNBRProcessingQGIS.py)

## Requirements
Either an ArcPy or QGIS python environment.

## Further Resources
NBR / dNBR
* Key, Carl H., and Nathan C. Benson. "Landscape assessment (LA)." FIREMON: Fire effects monitoring and inventory system 164 (2006): LA-1.

# Workflow
![GitHubWorkflow](https://github.com/StefMeh/Burned-Area-Estimation/assets/135348279/cebcc615-5e88-424c-bfaa-cd73aa8a1c28)

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

# Acknowlegements
The resources in this repository were developed as part of a Master's Thesis research project. This research was made possible and supported by SERVIR, a joint initiative between the National Aeronautic Space Administration (NASA) and the U.S. Agency for International Development (USAID), and the NASA Applied Sciences Capacity Building Program. Funding was provided through the Cooperative Agreement 80MSFC22M0004 between NASA and the University of Alabama in Huntsville (UAH).

# Thesis
## Abstract
Kenya is frequently subject to fire activity. Natural fire occurrence is part of and beneficial to most of the country’s ecosystems. However, anthropogenic activities associated with agricultural practices increasingly introduce fire activity to ecosystems that are not fire adapted, such as forest systems. Registration of small-size burned areas below an extent of 1 square kilometer, especially from fires in mixed agricultural-forest interfaces, is a substantial gap in currently available products. Addressing this issue, an improved spatial resolution fire burned area product was generated, based on VIIRS Active Fire Detections and Landsat Surface Reflectance data products, and used to characterize fire activity and its role in land cover land use change dynamics in the Mau Forest Reserve in Kenya. Detection information on fire events and burned areas increased between 85 to 100 % and 53 to 100 %, respectively, greatly affecting intact parts of the forest.

## Citation
Mehlich, Stefanie, "The role of the anthropogenic fire regime in protected areas in Kenya : a case study in the Mau Forest region" (2023). Theses. 471.
https://louis.uah.edu/uah-theses/471
