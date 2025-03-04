#!/bin/bash

set -e

# Due to the complexity of the frontend build process (especially in macOS),
# we leave the automation of the frontend build process to the future work.
# NOW, we just provide a simple script to rebuild the frontend manually.
# Please run the script after you have made changes to the frontend code.

cd frontend
npm ci
npm run build
cd ..
cp -r frontend/dist/ agentsociety/_dist/
