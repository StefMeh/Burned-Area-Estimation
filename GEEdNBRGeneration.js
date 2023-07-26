// GEEFile(EPSG4326) file in GEE user's assets
// 'fe' = Fire Events
var fe = ee.FeatureCollection("users/user/GEEFileEPSG4326");

// Landsat 7 & 8 Atmospherically Corrected Surface Reflectance Data Image Collections
var L7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2');
var L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');

// Landsat Masking Function
function  mask_landsat(image) {
  var date = ee.Number.parse(ee.Date(image.get('system:time_start')).format('yyyyMMdd'));
  var mask = image.select('QA_PIXEL').bitwiseAnd(ee.Number(2).pow(3).int()).eq(0)
    .and(image.select('QA_PIXEL').bitwiseAnd(ee.Number(2).pow(4).int()).eq(0));
  var satellite = ee.String(image.get('SPACECRAFT_ID'));
  image = ee.Image(ee.Algorithms.If(
    satellite.compareTo('LANDSAT_7').eq(0),
    image.select(['SR_B4', 'SR_B7'])
      .multiply(0.0000275).add(-0.2).multiply(10000)
      .rename(['NIR', 'SWIR2']),
    image.select(['SR_B5', 'SR_B7'])
      .multiply(0.0000275).add(-0.2).multiply(10000)
      .rename(['NIR', 'SWIR2'])
    ));
  return image.updateMask(mask.eq(0)).set('date', date);
}

// Google Drive Export Function
// Creates folder "dNBR_Output" in user's Google Drive
function exportImage(image, description) {
  Export.image.toDrive({
    image: image,
    description: description,
    region: image.geometry(),
    folder: 'dNBR_Output',
    scale: 30,
    maxPixels: 1E13,
  });
}

// Function to generate dNBR
function generateNBR (image) {
  return image.normalizedDifference(['NIR', 'SWIR2']).rename('NBR');
}

// Assign layer name property
var LN = 'FireEvents';
fe = fe.map(function (f) {
  return f.set('layerName', LN);
});

// Main Function
var prepareDNBRGeneration = function (envelope) {
  envelope = ee.Feature(envelope);
  // Which layer?
  var layerName = envelope.get('layerName');
  // print('layerName', layerName);

  // Get Unique Feature ID
  var featID = envelope.get('CLUSTER_ID');
  // print('featID', featID);
  
  // Pre-fire start and end date definition
  var cluster_start_date = ee.Date(envelope.get('START_TIME'));          // If input file is generated through QGIS: Use 'Date'
                                                                        // If input file is generated through ArcGISPro: Use 'START_TIME'
  var pre_fire_start_date = (cluster_start_date.advance(-120, 'day'));
  var pre_fire_end_date = (cluster_start_date.advance(-1, 'day'));
  
  // Post-fire start and end date definition
  var cluster_end_date = ee.Date(envelope.get('END_TIME'));              // If input file is generated through QGIS: Use 'Date'
                                                                        // If input file is generated through ArcGISPro: Use 'END_TIME'
  var post_fire_start_date = (cluster_end_date.advance(1, 'day'));
  var post_fire_end_date = (cluster_end_date.advance(120, 'day'));

  var preImageL7 = L7.filterBounds(envelope.geometry()).filterDate(pre_fire_start_date, pre_fire_end_date);
  // preImageL7 = preImageL7.map(mask_landsat);
  var preImageL8 = L8.filterBounds(envelope.geometry()).filterDate(pre_fire_start_date, pre_fire_end_date);
  // preImageL8 = preImageL8.map(mask_landsat);
  var preImage = ee.Algorithms.If(preImageL8.size().eq(0), preImageL7, preImageL7.merge(preImageL8));
  preImage = ee.ImageCollection(preImage).map(mask_landsat);

  var postImageL7 = L7.filterBounds(envelope.geometry()).filterDate(post_fire_start_date, post_fire_end_date);
  // postImageL7 = postImageL7.map(mask_landsat);
  var postImageL8 = L8.filterBounds(envelope.geometry()).filterDate(post_fire_start_date, post_fire_end_date);
  // postImageL8 = postImageL8.map(mask_landsat);
  var postImage = ee.Algorithms.If(postImageL8.size().eq(0), postImageL7, postImageL7.merge(postImageL8));
  postImage = ee.ImageCollection(postImage).map(mask_landsat);

  preImage = preImage.map(generateNBR);
  preImage = preImage.median().multiply(1000).rename([ee.String('preImage_').cat(layerName).cat('_').cat(featID)]);
  // preImage = preImage.qualityMosaic('NBR').multiply(1000).rename('preImage_'+ layerName + '_' + featID);

  postImage = postImage.map(generateNBR);
  postImage = postImage.median().multiply(1000).rename([ee.String('postImage_').cat(layerName).cat('_').cat(featID)]);
  // postImage = postImage.qualityMosaic('NBR').multiply(1000).rename('postImage_'+ layerName + '_' + featID);
    
  var dNBR = preImage.subtract(postImage).rename([ee.String('dNBR_').cat(layerName).cat('_').cat(featID)])
  var image = dNBR
  return image.clip(envelope.geometry());
};


var listfe = fe.toList(fe.size());

var listfeNBR = listfe.map(prepareDNBRGeneration);
print('listfeNBR', listfeNBR)
var size = listfeNBR.size().getInfo();

// For large files (> 100 fire events) break up exports to be generated using startIndex & endIndex
var startIndex = 0;
var endIndex = 10;
for (var i = startIndex; i<endIndex; i++) {
  var image = ee.Image(listfeNBR.get(i));
  var bandName = image.bandNames().getInfo()[0].split('_');
  bandName.shift();
  var description = bandName.join("_");
  exportImage(image, description);
}

// For Batch export of GEE tasks refer to: https://github.com/gee-hydro/gee_monkey.git under 'Free Version'
