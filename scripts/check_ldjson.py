#!/usr/bin/env python3
import json
import re
import sys
import urllib.request

url = sys.argv[1] if len(sys.argv) > 1 else 'https://lilsolid.ru/product/iqos-iluma-i-standart-breeze-blue-10'
html = urllib.request.urlopen(url, timeout=15).read().decode('utf-8', 'replace')
blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
print('blocks:', len(blocks))
for i, b in enumerate(blocks):
    try:
        data = json.loads(b)
        print(f'--- block {i} type={data.get("@type")}')
        if data.get('@type') == 'Product':
            print('  keys:', list(data.keys()))
            print('  offers:', 'offers' in data, data.get('offers'))
        if data.get('@type') == 'ItemList':
            for el in data.get('itemListElement', [])[:2]:
                item = el.get('item', {})
                if isinstance(item, dict) and item.get('@type') == 'Product':
                    print('  list product keys:', list(item.keys()))
                    print('  image:', item.get('image'))
    except json.JSONDecodeError as e:
        print(f'--- block {i} INVALID JSON:', e)
        print(b[:500])
