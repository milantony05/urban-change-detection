// Phase 2 export for North Bengaluru.
// Run in https://code.earthengine.google.com/ and start all Tasks.

var aoi = ee.Geometry.Rectangle([77.48, 13.04, 77.75, 13.22]);
var reflectanceBands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12'];

function maskSentinel2(image) {
  var scl = image.select('SCL');
  var clear = scl.neq(1)   // saturated or defective
    .and(scl.neq(3))       // cloud shadow
    .and(scl.neq(8))       // medium-probability cloud
    .and(scl.neq(9))       // high-probability cloud
    .and(scl.neq(10))      // cirrus
    .and(scl.neq(11));     // snow or ice
  return image.select(reflectanceBands)
    .updateMask(clear)
    .copyProperties(image, ['system:time_start', 'CLOUDY_PIXEL_PERCENTAGE']);
}

function exportPeriod(start, end, label) {
  var raw = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40));

  var clear = raw.map(maskSentinel2);
  // GeoTIFF export requires every band in this image to use a compatible type.
  // Scene counts are small, but UInt16 matches the reflectance bands.
  var validCount = clear.select('B2').count().rename('valid_count').toUint16();
  var reflectance = clear.median()
    .resample('bilinear')
    .round().toUint16();
  var composite = reflectance
    .addBands(validCount)
    .unmask(0)
    .clip(aoi)
    .toUint16(); // Cast the complete final image, including any Byte band.

  print(label + ' scene count', raw.size());
  print(label + ' scene IDs', raw.aggregate_array('system:index'));

  Map.addLayer(composite, {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000}, label);

  Export.image.toDrive({
    image: composite,
    description: 'NorthBengaluru_Sentinel2_' + label,
    folder: 'urban_change_detection',
    fileNamePrefix: 'north_bengaluru_' + label,
    region: aoi,
    crs: 'EPSG:32643',
    scale: 10,
    maxPixels: 1e10,
    fileFormat: 'GeoTIFF',
    formatOptions: {cloudOptimized: true}
  });

  var images = raw.toList(raw.size());
  var manifest = ee.FeatureCollection(images.map(function (item) {
    var image = ee.Image(item);
    return ee.Feature(null, {
      period: label,
      image_id: image.get('system:index'),
      acquired_utc: ee.Date(image.get('system:time_start')).format("YYYY-MM-dd'T'HH:mm:ss"),
      scene_cloud_percent: image.get('CLOUDY_PIXEL_PERCENTAGE')
    });
  }));

  Export.table.toDrive({
    collection: manifest,
    description: 'NorthBengaluru_manifest_' + label,
    folder: 'urban_change_detection',
    fileNamePrefix: 'north_bengaluru_' + label + '_scenes',
    fileFormat: 'CSV'
  });
}

Map.centerObject(aoi, 11);
Map.addLayer(aoi, {color: 'yellow'}, 'AOI');
exportPeriod('2018-01-01', '2018-04-01', '2018_dry_season_v2');
exportPeriod('2025-01-01', '2025-04-01', '2025_dry_season_v2');
