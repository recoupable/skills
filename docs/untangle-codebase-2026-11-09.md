# Untangle codebase — 2026-11-09

## Scope and evidence

Apply caldoai's `untangle-codebase` workflow to the maintained Recoup Skills tooling,
based on `7517ff4`. Comments/test pruning were not selected. Customer skill contents,
publication policy, opt-in model evaluation, and portability remain unchanged.

## Decision log (recorded before implementation)

### Own resolver inventory and table-token parsing in one dependency-light module

- `scripts/check_resolvable.py` and `scripts/run_resolver_eval.py` independently
  enumerate installed skills and parse the same backtick-wrapped table tokens.
- Commit [`faa5469`](https://github.com/recoupable/skills/commit/faa5469c9004131d0407e8df969bb6930330adbd) changed the slug grammar in both files for non-Recoup names;
  this is demonstrated co-change, not hypothetical deduplication.
- Evaluation's copies read the module-global plugin path, hiding the same input
  already explicit in the reachability gate.
- `SKILL_TOKEN_PLAIN` is unused after exact-answer routing validation; remove this
  dead pattern rather than maintaining a third description of slug syntax.
- Fix: a sibling `resolver_catalog.py` owns the existing grammar and two explicit
  path-based readers. Both command entry points depend on it. It imports only
  pathlib/re, never the model runner or publication machinery.
- Preserve table rows only, whitespace handling, dotted and user-named slugs,
  existing messages/exit codes, and structural-vs-live evaluation distinction.

## Deliberately retained boundaries

- Copies registered in `scripts/vendored.json` are required for independently
  installable skills. Central imports across skill folders would break portability.
- Host-specific package metadata and customer/staff boundaries represent different
  requirements. Existing common package-file/dependency policy remains canonical.
- The signed sync receiver must execute trusted repository-local code; do not add
  a runtime import from another repository or change its allowlist in this refactor.
- Gateway/TLS fallback and fixture-level transport failures encode real external
  service behavior; not every exception is a removable special case.
- Historical/example/media-generation scripts are not production package adapters;
  resemblance alone is not sufficient evidence to merge their workflows.

## Verification

Baseline: reachability 129 skills; structural evaluation 221 positive, 130 negative,
6 no-route/clarification fixtures; existing routing tests 4/4 pass. No live model
calls, publishing, or external messages are part of verification.

Final: all five validation gates pass (129 skills; 144 vendored copies across
51 groups; 8 manifests). Nine focused routing tests pass, including both CLI
entrypoints launched from an unrelated working directory. Python 3.13 runs:
117 catalog tests, 3 Business ownership tests, 15 plugin package tests, and
1 Claude package test pass; all generated package adapters build successfully.
The host's default Python 3.9 cannot run an existing `Path.hardlink_to` fixture;
using a supported interpreter resolves this without changing unrelated tests.

An independent reviewer repeated the synthetic inventory tests and both routing
gates, inspected the extraction/import boundary and found no actionable issues.
No model API calls, release creation, or publication occurred. Full test/build
logs are retained in the ignored monorepo task-evidence directory.


## Automated review follow-up

- Negative gate fixtures now assert the expected domain diagnostic and reject
  tracebacks; a crashing Python process must not count as a successful rejection.
- Both direct-script and `python -m scripts.<gate>` invocation remain supported.
  The small package-aware import branch represents those real launch contexts;
  the catalog logic remains single-owned.
- GitHub API readback confirms the full co-change revision linked above exists.
  The automated claim that it was absent was not reproduced.
- Nine focused routing tests and the five gates pass after these changes; broader
  catalog coverage is 117 tests on Python 3.13. No live model calls were made.
