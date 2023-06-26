var fireApprox = ee.FeatureCollection("users/sm0162/GEEFile");

// Cluster envelope layers
Map.addLayer(fireApprox, {color: 'f04020'}, 'MFR Clusters Fires');

var L7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2');
var L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');
var L9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2");


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

function exportImage(image, description) {
  Export.image.toDrive({
    image: image,
    description: description,
    region: image.geometry(),
    folder: 'BA_dNBR',
    scale: 30,
    maxPixels: 1E13,
  });
}

function generateNBR (image) {
  return image.normalizedDifference(['NIR', 'SWIR2']).rename('NBR');
}


var fireApproxLayerName = 'dNBR';
fireApprox = fireApprox.map(function (f) {
  return f.set('layerName', fireApproxLayerName);
});


var prepareDNBRGeneration = function (envelope) {
  envelope = ee.Feature(envelope);
  // Which layer?
  var layerName = envelope.get('layerName');
  // print('layerName', layerName);

  // Get Unique Feature ID
  var featID = envelope.get('CLUSTER_ID');
  // print('featID', featID);
  
    // Pre-fire start and end date definition
  var cluster_start_date = ee.Date(envelope.get('Date'));
  var pre_fire_start_date = (cluster_start_date.advance(-120, 'day'));
  var pre_fire_end_date = (cluster_start_date.advance(-1, 'day'));
  
  // Post-fire start and end date definition
  var cluster_end_date = ee.Date(envelope.get('Date'));
  var post_fire_start_date = (cluster_end_date.advance(1, 'day'));
  var post_fire_end_date = (cluster_end_date.advance(120, 'day'));

  var preImageL7 = L7.filterBounds(envelope.geometry()).filterDate(pre_fire_start_date, pre_fire_end_date);
  // print('preImageL7', preImageL7);
  // preImageL7 = preImageL7.map(mask_landsat);
  var preImageL8 = L8.filterBounds(envelope.geometry()).filterDate(pre_fire_start_date, pre_fire_end_date);
  // print('preImageL8', preImageL8)
  // preImageL8 = preImageL8.map(mask_landsat);
  var preImage = ee.Algorithms.If(preImageL8.size().eq(0), preImageL7, preImageL7.merge(preImageL8));
  preImage = ee.ImageCollection(preImage).map(mask_landsat);
  // print('preImage', preImage)
  // var preImage = ee.Algorithms.If(preImageL8.size().eq(0), preImageL7, preImageL7.merge(preImageL8));
  // var preImage = preImageL7.merge(preImageL8);

  var postImageL7 = L7.filterBounds(envelope.geometry()).filterDate(post_fire_start_date, post_fire_end_date);
  // print('postImageL7', postImageL7);
  // postImageL7 = postImageL7.map(mask_landsat);
  var postImageL8 = L8.filterBounds(envelope.geometry()).filterDate(post_fire_start_date, post_fire_end_date);
  // print('postImageL8', postImageL8);
  // postImageL8 = postImageL8.map(mask_landsat);
  // var postImage = postImageL7.merge(postImageL8);
  // var postImage = ee.Algorithms.If(postImageL8.size().eq(0), postImageL7, preImageL7.merge(postImageL8));
  var postImage = ee.Algorithms.If(postImageL8.size().eq(0), postImageL7, postImageL7.merge(postImageL8));
  postImage = ee.ImageCollection(postImage).map(mask_landsat);
  // print('postImage', postImage)

  preImage = preImage.map(generateNBR);
  // preImage = preImage.qualityMosaic('NBR').multiply(1000).rename('preImage_'+ layerName + '_' + featID);
  preImage = preImage.median().multiply(1000).rename([ee.String('preImage_').cat(layerName).cat('_').cat(featID)]);

  postImage = postImage.map(generateNBR);
  // postImage = postImage.qualityMosaic('NBR').multiply(1000).rename('postImage_'+ layerName + '_' + featID);
  postImage = postImage.median().multiply(1000).rename([ee.String('postImage_').cat(layerName).cat('_').cat(featID)]);
  
  // exportImage(preImage, 'preImage_'+ layerName + '_' + featID);
  
  var dNBR = preImage.subtract(postImage).rename([ee.String('dNBR_').cat(layerName).cat('_').cat(featID)])
  // var image = preImage.addBands(postImage).addBands(dNBR);
  var image = dNBR
  return image.clip(envelope.geometry());
};



var listfireApprox = fireApprox.toList(fireApprox.size());

// var firstFeat = bufcl.first();
// var firstFeat = ee.Feature(listBufCl.get(2));
// Map.addLayer(firstFeat)
// firstFeat = prepareDNBRGeneration(firstFeat);
// // print('firstFeat', firstFeat)


var listfireApproxNBR = listfireApprox.map(prepareDNBRGeneration);
//print('listfireApproxNBR', listfireApproxNBR)
var size = listfireApproxNBR.size().getInfo();

var startIndex = 80;
var endIndex = 85;
for (var i = startIndex; i<endIndex; i++) {
  print(i)
  var image = ee.Image(listfireApproxNBR.get(i));
  var bandName = image.bandNames().getInfo()[0].split('_');
  bandName.shift();
  var description = bandName.join("_");
  exportImage(image, description);
}
