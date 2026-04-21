@echo off
echo Generating Python SDK from OpenAPI...
call env\Scripts\activate
npm install --save-dev @openapitools/openapi-generator-cli
npx openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o crowd_sdk
echo SDK generated in crowd_sdk
