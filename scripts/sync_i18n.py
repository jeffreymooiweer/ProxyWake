#!/usr/bin/env python3
"""Merge missing translation keys from en.json into all other locale files."""

import json
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / 'frontend' / 'src' / 'i18n' / 'locales'
SOURCE = 'en.json'


def deep_merge(base, overlay):
  result = dict(base)
  for key, value in overlay.items():
    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
      result[key] = deep_merge(result[key], value)
    elif key not in result:
      result[key] = value
  return result


def main():
  source_path = LOCALES_DIR / SOURCE
  source = json.loads(source_path.read_text(encoding='utf-8'))

  for path in sorted(LOCALES_DIR.glob('*.json')):
    if path.name == SOURCE:
      continue
    locale = json.loads(path.read_text(encoding='utf-8'))
    merged = deep_merge(locale, source)
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Updated {path.name}')


if __name__ == '__main__':
  main()
