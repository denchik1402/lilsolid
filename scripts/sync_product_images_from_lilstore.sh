#!/bin/bash
# Синхронизация изображений товаров с основного магазина (lilstore.ru)
set -e
SRC="${1:-lilstore@104.128.141.177:/home/lilstore/my_shop/static/images/products/}"
DEST="${2:-/home/lilstore/lilsolid/static/images/products/}"
echo "Sync products images: $SRC -> $DEST"
mkdir -p "$DEST"
rsync -az --delete "$SRC" "$DEST"
echo "Done: $(find "$DEST" -type f | wc -l) files"
