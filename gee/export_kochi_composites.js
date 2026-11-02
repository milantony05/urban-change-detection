// Candidate external-city imagery. Use for pixel-quality checks only until
// the Bengaluru model and threshold are frozen. No Kochi labels for tuning.
var aoi = ee.Geometry.Rectangle([76.20, 9.88, 76.42, 10.10]);
var bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12'];

function clean(image) {
  var scl = image.select('SCL');
  var clear = scl.neq(1).and(scl.neq(3)).and(scl.neq(8))
    .and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  return image.select(bands).updateMask(clear);
}

function exportPeriod(start, end, label) {
  var raw = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi).filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40));
  var clear = raw.map(clean);
  var composite = clear.median().round().toUint16()
    .addBands(clear.select('B2').count().rename('valid_count').toUint16())
    .unmask(0).clip(aoi).toUint16();
  print(label + ' scenes', raw.size());
  Map.addLayer(composite, {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000}, label);
  Export.image.toDrive({
    image: composite,
    description: 'Kochi_Sentinel2_' + label,
    folder: 'urban_change_detection',
    fileNamePrefix: 'kochi_' + label,
    region: aoi, crs: 'EPSG:32643', scale: 10,
    maxPixels: 1e10, fileFormat: 'GeoTIFF',
    formatOptions: {cloudOptimized: true}
  });
  var list = raw.toList(raw.size());
  var manifest = ee.FeatureCollection(list.map(function (item) {
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
    description: 'Kochi_manifest_' + label,
    folder: 'urban_change_detection',
    fileNamePrefix: 'kochi_' + label + '_scenes',
    fileFormat: 'CSV'
  });
}

Map.centerObject(aoi, 11);
Map.addLayer(aoi, {color: 'yellow'}, 'Candidate Kochi AOI');
exportPeriod('2018-01-01', '2018-04-01', '2018_dry_season');
exportPeriod('2025-01-01', '2025-04-01', '2025_dry_season');
