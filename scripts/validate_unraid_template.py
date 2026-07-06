#!/usr/bin/env python3
"""Validate the ProxyWake Unraid Community Applications template."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / 'unraid' / 'proxywake.xml'

REQUIRED_ELEMENTS = (
    'Name',
    'Repository',
    'Registry',
    'Network',
    'WebUI',
    'TemplateURL',
    'Icon',
    'Support',
    'Project',
    'Overview',
    'Category',
)


class ValidationError(Exception):
    pass


def _text(root: ET.Element, tag: str) -> str:
    element = root.find(tag)
    if element is None or element.text is None:
        raise ValidationError(f'Missing or empty element: {tag}')
    return element.text.strip()


def _config_targets(root: ET.Element) -> dict[str, ET.Element]:
    configs: dict[str, ET.Element] = {}
    for config in root.findall('Config'):
        target = config.get('Target')
        if target:
            configs[target] = config
    return configs


def validate_template(path: Path = TEMPLATE_PATH) -> None:
    if not path.is_file():
        raise ValidationError(f'Template not found: {path}')

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValidationError(f'Invalid XML: {exc}') from exc

    if root.tag != 'Container':
        raise ValidationError(f'Expected root element Container, found {root.tag!r}')

    for tag in REQUIRED_ELEMENTS:
        _text(root, tag)

    repository = _text(root, 'Repository')
    if 'jeffersonmouze/proxywake' not in repository:
        raise ValidationError(
            f'Repository must contain jeffersonmouze/proxywake, found: {repository}'
        )

    webui = _text(root, 'WebUI')
    if '[PORT:5001]' not in webui:
        raise ValidationError(f'WebUI must contain [PORT:5001], found: {webui}')

    icon = _text(root, 'Icon')
    if 'raw.githubusercontent.com' not in icon:
        raise ValidationError(f'Icon must point to raw.githubusercontent.com, found: {icon}')

    template_url = _text(root, 'TemplateURL')
    if 'raw.githubusercontent.com' not in template_url:
        raise ValidationError(
            f'TemplateURL must point to raw.githubusercontent.com, found: {template_url}'
        )

    configs = _config_targets(root)
    required_configs = {
        '5001': 'WebUI Port',
        '/app/backend/data': 'Appdata',
        'PROXYWAKE_SECRET_KEY': 'Secret Key',
    }
    for target, label in required_configs.items():
        if target not in configs:
            raise ValidationError(f'Missing {label} Config with Target={target!r}')

    port_config = configs['5001']
    if port_config.get('Type') != 'Port':
        raise ValidationError('WebUI Port Config must have Type=Port')

    appdata_config = configs['/app/backend/data']
    if appdata_config.get('Type') != 'Path':
        raise ValidationError('Appdata Config must have Type=Path')

    secret_config = configs['PROXYWAKE_SECRET_KEY']
    if secret_config.get('Type') != 'Variable':
        raise ValidationError('Secret Key Config must have Type=Variable')


def main() -> int:
    try:
        validate_template()
    except ValidationError as exc:
        print(f'Unraid template validation failed: {exc}', file=sys.stderr)
        return 1

    print('Unraid template validation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
