"""Validate customer instructions against the files that actually ship."""
from pathlib import PurePosixPath
import re
from urllib.parse import unquote, urlsplit


RECOUP_LINK = re.compile(
    r"https://github\.com/recoupable/skills/(?:blob|tree)/main/skills/[^\s<>`)]+"
)
LOCAL_REFERENCE = re.compile(r"`((?:references|scripts|templates|fixtures)/[^`\s<>]+)`")


def validate_customer_dependencies(files):
    for name, data in files.items():
        path = PurePosixPath(name)
        if path.parts[0] != 'skills' or path.suffix not in {'.md', '.mdx'}:
            continue
        text = data.decode('utf-8')
        for match in RECOUP_LINK.finditer(text):
            url = match.group()
            parts = unquote(urlsplit(url).path).split('/')
            target = '/'.join(parts[5:])
            if '..' in PurePosixPath(target).parts:
                raise ValueError(f'Invalid Recoup dependency in {name}: {url}')
            exists = (target in files if parts[3] == 'blob' else
                      any(p.startswith(target.rstrip('/') + '/') for p in files))
            if not exists:
                raise ValueError(f'Customer file references missing packaged Recoup path: {name}: {url}')
        # Entry points declare bundled dependencies. Supporting prose can name
        # example scripts from the workflow it explains, rather than files to load.
        if path.name != 'SKILL.md':
            continue
        for relative in LOCAL_REFERENCE.findall(text):
            target = PurePosixPath('skills', path.parts[1], relative)
            if target.suffix and str(target) not in files:
                raise ValueError(f'Customer file references missing bundled file: {name}: {relative}')
