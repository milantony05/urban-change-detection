# Review reconciliation and label meaning

The second round returned eight clarifications. Three changed from `other_change` to `change`; three changed from `other_change` to `no_change`; one remained `other_change` (submitted as `other_changes`); and one remained `change` while describing lake-to-land. The revised cards marked the sampled location in both dates.

The complete 24-item review is retained as **contextual review**, not an independent pixel-level test set. A lake-to-land transition is outside the vegetation-to-built-up target. Plot lines, visible urbanization near a marker, or a broad change across a card do not prove the sampled 10 m pixel's source and destination classes. The first round also had a marker-position error. No precision or recall is reported from these labels.

`scripts/reconcile_reviews.py` merges both sheets, preserves the original answer and revised answer, and leaves `source_2018`, `destination_2025` and `target_transition` unverified. This is deliberate. For true reference labels, inspect the marked pixel and its immediate neighborhood with independent date-appropriate evidence, record both classes (`vegetation`, `built_up`, `water`, `bare`, `other`, or `unclear`), and derive the positive class only from `vegetation` to `built_up`. Any uncertainty should remain excluded from scoring.

The next training path can use a public land-cover product as **weak labels** for development, with spatial blocks separated. The final test set must be independently adjudicated with the two explicit classes; it cannot be produced by the same public model used for training.
