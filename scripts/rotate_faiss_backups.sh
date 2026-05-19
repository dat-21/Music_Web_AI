#!/bin/bash
set -euo pipefail

INDEX_PATH="${1:-/data/faiss.index}"
BASE_DIR=$(dirname "$INDEX_PATH")
BASE_NAME=$(basename "$INDEX_PATH")

ls -t "$BASE_DIR"/"$BASE_NAME".*.bak 2>/dev/null | tail -n +6 | while read -r old; do
  ts=$(basename "$old")
  ts=${ts#"$BASE_NAME".}
  ts=${ts%.bak}
  meta="$BASE_DIR/$BASE_NAME.metadata.json.$ts.bak"
  rm -f "$old" "$meta"
done
