# First review batch: provisional responses

The 24 completed responses are preserved outside the source rasters. The reviewer marked 8 of 12 spectral candidates and 9 of 12 controls as `change`; all other responses used `other_change`. There were no `no_change` or `unclear` responses.

These counts are **not** precision, recall or evidence of a conversion rate. The initial cards mistakenly placed their yellow marker on the seam between years. Some notes describe broader changes, lake colour or very little change, so the label `change` cannot yet be assumed to mean vegetation-to-built-up at the sampled pixel. The controls were sampled from the spectral method's non-candidate set, not from verified non-change locations; genuine changes there are plausible.

The card generator now marks the sampled center in both dates. Reconcile labels using the corrected cards and, for ambiguous locations, independent higher-resolution imagery before producing a reference set. Preserve the original reviewer responses, and record any adjudicated label in a new field rather than overwriting them. Reserve geographic blocks before splitting reviewed examples into train, validation and test.
