# Music catalogs evals

Use these scenarios to test whether the plugin improves diligence behavior.

## Metrics

- Red-flag recall.
- False-positive rate.
- Evidence citation accuracy.
- Financial tie-out tolerance.
- Missing-document detection.
- Memo caveat quality.
- Time to first diligence memo.

## Scenarios

Each scenario file describes a realistic pressure case. Future iterations can
add fixture files under the same scenario folder.

## Scenario assets

Turn a scenario into a repeatable test by adding a folder with the same id under
`fixtures/scenarios/`. Keep each folder small enough to review by hand:

```text
fixtures/scenarios/{scenario-id}/
├── source/
├── normalized/
├── findings/
├── workpapers/
├── evidence-ledger.json
└── expected-behavior.md
```

Use synthetic data only. The fixture should prove the behavior named in the
scenario, not recreate a full real data room.
