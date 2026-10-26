"""Single tracked-file customer boundary shared by every host adapter."""
from pathlib import Path
import re
from plugin_package_dependencies import validate_customer_dependencies

INTERNAL = re.compile(r'\brecoup-internal-[a-z0-9-]+')

def package_files(root, tracked, audience):
    result = {}
    for name in sorted(tracked):
        p = root / name
        parts = Path(name).parts
        if not p.is_file():
            continue
        if p.is_symlink() and not p.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'External symlink: {name}')
        if audience == 'customer':
            if not (name in {'.codex-plugin/plugin.json', '.mcp.json', 'LICENSE'} or
                    parts[0] == 'assets' or
                    (parts[0] == 'skills' and len(parts) > 2 and not parts[1].startswith('recoup-internal-'))):
                continue
        elif parts[0] in {'.github', '.git'}:
            continue
        data = p.read_bytes()
        if audience == 'customer' and parts[0] == 'skills':
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                text = ''
            if INTERNAL.search(text):
                raise ValueError(f'Customer file references excluded internal skill: {name}')
        result[name] = data
    if audience == 'customer':
        validate_customer_dependencies(result)
    for required in ('.codex-plugin/plugin.json', '.mcp.json'):
        if required not in result:
            raise ValueError(f'Missing {required}')
    skills = sorted(n.split('/')[1] for n in result if re.fullmatch(r'skills/[^/]+/SKILL.md', n))
    if not skills:
        raise ValueError('No skills packaged')
    return result, skills

