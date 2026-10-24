# Editorial decision contract

All examples are synthetic. Never infer that a bookmark is the owner's opinion.

```json
{
  "state": "promoted",
  "reason": "A concrete operating check for the selected audience, not covered in existing drafts.",
  "signal_id": "2026-10-23-check-report-inputs-before-automation",
  "type": "content-idea",
  "topic": "Verifying automated reports",
  "hook": "Check the inputs before trusting an automated report",
  "intent": "Operations leaders evaluating automated weekly reporting",
  "formats": ["linkedin", "article"],
  "verification": "attributed-opinion",
  "body": "Explain how an operator can check source coverage before relying on an automated report. Frame the suggested checklist as an illustrative method, not an observed customer result.",
  "evidence": "The captured author's opinion concerns source coverage. The original X URL is in source.ref; no quantified result has been established."
}
```

`verification` is `primary-source-checked` or `attributed-opinion`. The evidence note must name
which primary source was read and what it supports, or explicitly limit the piece to attributed
opinion. A self-reported performance number is not verified simply because the original post says it.
The CLI enforces structure and provenance, not truth: the agent must perform the checks.

Hold: `{"state":"needs-research","reason":"The screenshot contains the claimed result; obtain readable context before using it."}`

Skip: `{"state":"skipped","reason":"Outside the workspace editorial scope."}`

Link: `{"state":"linked","signal_id":"2026-10-23-check-report-inputs-before-automation","reason":"Adds an independent example to the same angle."}`

For linked items, add their original URL to the existing signal evidence first. Do not reset `used`
or `evergreen` history. Linked does not mean redraft. A new angle needs deliberate review.
