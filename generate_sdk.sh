#!/usr/bin/env bash
set -euo pipefail

npm install -g @openapitools/openapi-generator-cli
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o crowd_sdk

echo "SDK generated in ./crowd_sdk"
