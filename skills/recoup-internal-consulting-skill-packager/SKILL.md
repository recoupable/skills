---
name: recoup-internal-consulting-skill-packager
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Validate and package changes in the explicitly selected plugin repository, then publish only when authorized. Use for packaging, releasing, or refreshing skills."
---

# Consulting Skill Packager

First locate the actual plugin source repository. A business workspace containing a vendored copy
or a submodule is not automatically the publication destination. Read its packaging instructions,
manifest files, Git status, and remote; preserve unrelated work.

1. Validate skill names, descriptions, supporting resources, and changed helpers. Run that plugin's
   checks. In Recoup Skills, run all five validation gates listed in the selected repository AGENTS.md
   plus the focused consulting media/runtime tests. Do not assume source-repository tooling is bundled.
2. Inspect the destination's installed plugin and marketplace formats. Update all applicable manifests
   consistently; do not copy a personal source URL into a differently owned package.
3. Keep a source edit, an installed-plugin update, and a vendored copy update distinct. None is automatic.
4. Review the final files for private examples, credentials, local paths, and asset terms. Sanitizing
   current files does not sanitize prior Git history. Use a reviewed snapshot for a new sharing boundary.
5. Commit the intended changes according to the workspace convention. Publish only to the explicitly
   authorized repository and branch; an ordinary skill edit alone is not a request to publish.
6. Report the exact committed/published state and which installed or vendored copies still need updating.

For a move into Recoup Skills, follow that repository's current naming, resolver, manifest, and
portability checks. Do not assume its internal skill label means the GitHub repository is private.
