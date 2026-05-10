"""Shared helpers for catalog-diligence scripts.

Importable from any sibling script (Python adds the script's directory to
`sys.path` automatically). Hyphenated script filenames cannot be imported,
so all sharable logic lives here under an underscore-prefixed name.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> dict[str, Any]:
    """Parse a YAML file. Uses PyYAML if available, else a small built-in
    parser that handles the limited grammar used by assumptions.yaml:

    - `key: value` scalars (strings, ints, floats, true/false, null/~)
    - block-style nested dicts via indentation
    - block-style lists (`- item`)
    - flow-style empty sequence/mapping (`[]`, `{}`)
    - quoted strings ("..." or '...')

    Does NOT support: anchors, aliases, multi-line strings, mixed flow
    style, complex keys, or merging.
    """
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return _parse_minimal_yaml(text)
    return yaml.safe_load(text) or {}


def _parse_scalar(raw: str) -> Any:
    s = raw.strip()
    if not s or s.lower() in {"null", "~"}:
        return None
    if s == "[]":
        return []
    if s == "{}":
        return {}
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in _split_flow(inner)]
    try:
        if "." in s or "e" in s.lower():
            return float(s)
        return int(s)
    except ValueError:
        pass
    return s


def _split_flow(inner: str) -> list[str]:
    items: list[str] = []
    depth = 0
    buf: list[str] = []
    in_quote: str | None = None
    for ch in inner:
        if in_quote:
            buf.append(ch)
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ('"', "'"):
            in_quote = ch
            buf.append(ch)
            continue
        if ch in "[{":
            depth += 1
            buf.append(ch)
            continue
        if ch in "]}":
            depth -= 1
            buf.append(ch)
            continue
        if ch == "," and depth == 0:
            items.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    if buf:
        items.append("".join(buf).strip())
    return [item for item in items if item]


def _parse_minimal_yaml(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        # Strip trailing inline comments (rough — does not respect quotes).
        stripped = raw
        if " #" in stripped and not stripped.lstrip().startswith("-"):
            stripped = stripped.split(" #", 1)[0]
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.rstrip()))

    root: dict[str, Any] = {}
    # Stack of (indent, container, last_key). last_key is set when we just
    # opened a key with no inline value, awaiting indented children.
    stack: list[tuple[int, Any, str | None]] = [(-1, root, None)]
    i = 0
    while i < len(lines):
        indent, line = lines[i]
        body = line.lstrip(" ")

        # Pop frames that are no longer in scope.
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent_indent, container, pending_key = stack[-1] if stack else (-1, root, None)

        if body.startswith("- "):
            value_part = body[2:].strip()
            # If the parent is awaiting children for a pending key, it must
            # become a list now.
            if pending_key is not None:
                new_list: list[Any] = []
                container[pending_key] = new_list
                stack[-1] = (parent_indent, container, None)
                stack.append((indent, new_list, None))
                container = new_list
            # value_part may be a scalar or a `key: value` (list of dicts).
            if ":" in value_part and not _looks_like_quoted_url(value_part):
                key, _, rest = value_part.partition(":")
                key = key.strip()
                rest = rest.strip()
                new_dict: dict[str, Any] = {}
                if rest:
                    new_dict[key] = _parse_scalar(rest)
                else:
                    # The dict will gain children at deeper indent.
                    new_dict[key] = None
                container.append(new_dict)
                stack.append((indent, new_dict, key if not rest else None))
            else:
                container.append(_parse_scalar(value_part))
            i += 1
            continue

        if ":" in body:
            key, _, rest = body.partition(":")
            key = key.strip()
            rest = rest.strip()
            if not isinstance(container, dict):
                # Shouldn't happen for well-formed input.
                i += 1
                continue
            if rest:
                container[key] = _parse_scalar(rest)
                stack[-1] = (parent_indent, container, None)
            else:
                # Look ahead to determine list vs dict child.
                child = _peek_child_kind(lines, i, indent)
                if child == "list":
                    new_list = []
                    container[key] = new_list
                    stack.append((indent, new_list, None))
                elif child == "dict":
                    new_dict = {}
                    container[key] = new_dict
                    stack.append((indent, new_dict, None))
                else:
                    container[key] = None
                    stack[-1] = (parent_indent, container, None)
            i += 1
            continue

        i += 1

    return root


def _peek_child_kind(lines: list[tuple[int, str]], current: int, current_indent: int) -> str | None:
    for j in range(current + 1, len(lines)):
        next_indent, next_line = lines[j]
        if next_indent <= current_indent:
            return None
        return "list" if next_line.lstrip(" ").startswith("- ") else "dict"
    return None


def _looks_like_quoted_url(s: str) -> bool:
    # Heuristic: avoid splitting URLs in unquoted scalars (e.g. https://...).
    return "://" in s


def deep_get(data: Any, dotted_key: str, default: Any = None) -> Any:
    """Walk a dotted path through nested dicts. Returns `default` on miss."""
    cur = data
    for part in dotted_key.split("."):
        if not isinstance(cur, dict):
            return default
        if part not in cur:
            return default
        cur = cur[part]
    return cur
