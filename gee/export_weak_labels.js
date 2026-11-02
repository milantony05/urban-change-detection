// Weak training labels for Bengaluru, derived from Dynamic World probabilities.
// These are model-generated suggestions, NEVER an independent evaluation set.
var aoi = ee.Geometry.Rectangle([77.48, 13.04, 77.75, 13.22]);
var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1');
var vegetation = ['trees', 'grass', 'shrub_and_scrub'];

function period(start, end, label) {
  var images = dw.filterBounds(aoi).filterDate(start, end);
  print(label + ' Dynamic World scenes', images.size());
  var probabilities = images.select(vegetation.concat(['built'])).median();
  var veg = probabilities.select(vegetation).reduce(ee.Reducer.max());
  return {
    veg: veg,
    built: probabilities.select('built'),
    observed: images.select('built').count().gt(0)
  };
}

var before = period('2018-01-01', '2018-04-01', '2018');
var after = period('2025-01-01', '2025-04-01', '2025');
var confidentVegBefore = before.veg.gte(0.65).and(before.built.lt(0.25));
var confidentVegAfter = after.veg.gte(0.65).and(after.built.lt(0.25));
var confidentBuiltBefore = before.built.gte(0.65).and(before.veg.lt(0.25));
var confidentBuiltAfter = after.built.gte(0.65).and(after.veg.lt(0.25));

var positive = confidentVegBefore.and(confidentBuiltAfter);
var stableVeg = confidentVegBefore.and(confidentVegAfter);
var stableBuilt = confidentBuiltBefore.and(confidentBuiltAfter);
var observed = before.observed.and(after.observed);

// 0 = uncertain / missing / all other transitions; 1 = stable class negative;
// 2 = vegetation-to-built-up positive. No claim of ground truth.
var weakLabel = stableVeg.or(stableBuilt).and(observed).toUint8()
  .add(positive.and(observed).toUint8().multiply(2))
  .unmask(0)
  .rename('weak_label')
  .clip(aoi)
  .toUint8();

Map.centerObject(aoi, 11);
Map.addLayer(weakLabel, {min: 0, max: 2, palette: ['black', 'gray', 'red']}, 'Weak labels');
Export.image.toDrive({
  image: weakLabel,
  description: 'NorthBengaluru_DynamicWorld_weak_labels',
  folder: 'urban_change_detection',
  fileNamePrefix: 'north_bengaluru_weak_labels_v1',
  region: aoi,
  crs: 'EPSG:32643',
  crsTransform: [10, 0, 768770, 0, -10, 1463110],
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF'
});
