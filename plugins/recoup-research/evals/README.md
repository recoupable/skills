# Evaluation Fixtures

Test fixtures for validating research plugin skills and commands.

## Structure

Each eval is a YAML file with:
- `name` — eval identifier
- `skill` — which skill to test
- `input` — user prompt
- `expected` — what the output should contain
- `must_call` — API endpoints that must be called
- `must_not` — anti-patterns to check for

## Running evals

Evals are designed to be run by the agent itself — present the input, verify
the output contains expected elements, and check that the right endpoints were
called.

## Fixtures

- `artist-research-basic.yaml` — basic artist research sweep
- `playlist-pitch.yaml` — playlist pitch target generation
- `emerging-discovery.yaml` — A&R scouting for emerging artists
- `graceful-degradation.yaml` — fallback when the structured provider has no data
