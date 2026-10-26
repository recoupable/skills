"""Validate customer instructions against the files that actually ship."""
from pathlib import PurePosixPath
import re
from urllib.parse import unquote, urlsplit


RECOUP_LINK = re.compile(
    r"https://github\.com/recoupable/skills/(?:blob|tree)/main/skills/[^\s<>`)\]\"']+"
)
LOCAL_REFERENCE = re.compile(r"`((?:references|scripts|templates|fixtures)/[^`\s<>]*)`")
LOCAL_LINK = re.compile(
    r"\[[^\]\n]*\]\(<?((?:\./)?(?:references|scripts|templates|fixtures)/[^\s)>]+)"
)


def validate_customer_dependencies(files):
    for name, data in files.items():
        path = PurePosixPath(name)
        if path.parts[0] != 'skills' or path.suffix not in {'.md', '.mdx'}:
            continue
        text = data.decode('utf-8')
        for match in RECOUP_LINK.finditer(text):
            url = match.group().rstrip('.,;:!?')
            parts = unquote(urlsplit(url).path).split('/')
            target = '/'.join(parts[5:])
            if '..' in PurePosixPath(target).parts:
                raise ValueError(f'Invalid Recoup dependency in {name}: {url}')
            exists = (target in files if parts[3] == 'blob' else
                      any(p.startswith(target.rstrip('/') + '/') for p in files))
            if not exists:
                raise ValueError(f'Customer file references missing packaged Recoup path: {name}: {url}')
        # Progressive disclosure can load required helpers from any support guide.
        # Concrete backticked support paths must exist; illustrative layouts belong
        # in fenced examples, and optional external helpers must name their owner.
        for relative in LOCAL_REFERENCE.findall(text) + LOCAL_LINK.findall(text):
            target = PurePosixPath('skills', path.parts[1], unquote(urlsplit(relative).path))
            if '..' in target.parts:
                raise ValueError(f'Invalid bundled dependency in {name}: {relative}')
            if str(target) not in files and not any(
                p.startswith(str(target).rstrip('/') + '/') for p in files
            ):
                raise ValueError(f'Customer file references missing bundled file: {name}: {relative}')
