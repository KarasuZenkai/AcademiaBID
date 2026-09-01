#!/usr/bin/env sh
set -eu

mkdir -p media
curl --fail --location --output media/demo.mp4 \
  "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
