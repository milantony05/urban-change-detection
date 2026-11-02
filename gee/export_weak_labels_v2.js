// Dynamic World weak labels with additional hard negatives for North Bengaluru.
// 0 ignored, 1 weak non-target, 2 weak vegetation-to-built-up candidate.
// These labels are NOT independent ground truth.
var aoi = ee.Geometry.Rectangle([77.48, 13.04, 77.75, 13.22]);
var source = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1');
var classes = ['trees', 'grass', 'shrub_and_scrub', 'built', 'water', 'bare'];

function summarize(start, end, name) {
  var images = source.filterBounds(aoi).filterDate(start, end);
  print(name + ' scenes', images.size());
  var median = images.select(classes).median();
  return {
    veg: median.select(['trees', 'grass', 'shrub_and_scrub']).reduce(ee.Reducer.max()),
    built: median.select('built'),
    water: median.select('water'),
    bare: median.select('bare'),
    observed: images.select('built').count().gt(0)
  };
}

var before = summarize('2018-01-01', '2018-04-01', '2018');
var after = summarize('2025-01-01', '2025-04-01', '2025');
var observed = before.observed.and(after.observed);

// Class confidence is deliberately high. Crops are not counted as positive
// vegetation because their dry-season appearance is unstable.
var beforeVeg = before.veg.gte(0.65).and(before.built.lt(0.25));
var afterBuilt = after.built.gte(0.65).and(after.veg.lt(0.25));
var positive = beforeVeg.and(afterBuilt).and(observed);

// A confident non-vegetated source or non-built destination rules out our
// specific transition, regardless of what happened at the other date.
var sourceNotVeg = before.built.gte(0.70)
  .or(before.water.gte(0.70))
  .or(before.bare.gte(0.70));
var destinationNotBuilt = after.veg.gte(0.70)
  .or(after.water.gte(0.70))
  .or(after.bare.gte(0.70));
var negative = sourceNotVeg.or(destinationNotBuilt).and(observed).and(positive.not());

var weakLabel = negative.toUint8()
  .add(positive.toUint8().multiply(2))
  .unmask(0)
  .rename('weak_label')
  .clip(aoi)
  .toUint8();

print('Weak label counts (preview, may take time)', weakLabel.reduceRegion({
  reducer: ee.Reducer.frequencyHistogram(),
  geometry: aoi,
  scale: 30,
  maxPixels: 1e8
}));
Map.centerObject(aoi, 11);
Map.addLayer(weakLabel, {min: 0, max: 2, palette: ['black', 'gray', 'red']}, 'Weak v2');

Export.image.toDrive({
  image: weakLabel,
  description: 'NorthBengaluru_DynamicWorld_weak_labels_v2',
  folder: 'urban_change_detection',
  fileNamePrefix: 'north_bengaluru_weak_labels_v2',
  region: aoi,
  crs: 'EPSG:32643',
  crsTransform: [10, 0, 768770, 0, -10, 1463110],
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF'
});
