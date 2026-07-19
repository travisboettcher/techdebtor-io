#!/usr/bin/env bash
# Publish a draft post: flips draft to false and bumps the front-matter
# date to the publish date, so posts sort/display by when they actually
# went live rather than when they were drafted.
#
# Usage:
#   scripts/publish-post.sh <slug-or-path> [YYYY-MM-DD]
#
# Examples:
#   scripts/publish-post.sh a-vault-that-talks-back
#   scripts/publish-post.sh content/posts/a-vault-that-talks-back.md
#   scripts/publish-post.sh a-vault-that-talks-back 2026-07-15

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <slug-or-path> [YYYY-MM-DD]" >&2
  exit 1
fi

input="$1"
publish_date="${2:-$(date +%F)}"

if [[ ! "$publish_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "error: date must be in YYYY-MM-DD format, got '$publish_date'" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$input" == *.md ]]; then
  post_path="$input"
  [[ "$post_path" = /* ]] || post_path="$repo_root/$post_path"
else
  post_path="$repo_root/content/posts/${input}.md"
fi

if [[ ! -f "$post_path" ]]; then
  echo "error: post not found: $post_path" >&2
  exit 1
fi

if ! grep -q '^draft: true$' "$post_path"; then
  if grep -q '^draft: false$' "$post_path"; then
    echo "error: $post_path is already published (draft: false)" >&2
    exit 1
  fi
  echo "error: no 'draft: true' line found in $post_path" >&2
  exit 1
fi

tmp="$(mktemp)"
sed -e "s/^draft: true$/draft: false/" \
    -e "s/^date: .*/date: ${publish_date}/" \
    "$post_path" > "$tmp"
mv "$tmp" "$post_path"

echo "Published $(basename "$post_path") with date ${publish_date}"
