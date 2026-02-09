#!/bin/bash
#Script to package Lambda fuction with dependencies
# Exit immediately if a command exits with a non-zero status
set -e

echo " Creating Lambda deployment package..."

#Anchor the paths
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")
PACKAGE_DIR="$REPO_ROOT/lambda_dist"
ZIP_FILE="$REPO_ROOT/weather_ingestion_lambda.zip"

#Create clean directory
echo "Cleaning old artifacts..."
rm -rf "$PACKAGE_DIR" "$ZIP_FILE"
mkdir -p "$PACKAGE_DIR"

#Install dependencies to lambda_package/
echo "Installing dependencies from $REPO_ROOT/requirements.txt..."
pip install -r "$REPO_ROOT/requirements.txt" -t "$PACKAGE_DIR" --quiet

#Copy source code (Avoiding hidden files)
echo "Copying source code..."
cp -r "$REPO_ROOT/src/"* "$PACKAGE_DIR/"

#Trim the fat (Reduce size)
echo "Removing unnecessary files to reduce size..."
find "$PACKAGE_DIR" -type d -name "__pycache__" -exec rm -rf {} +
rm -rf "$PACKAGE_DIR"/*.dist-info
rm -rf "$PACKAGE_DIR"/*.egg-info
find "$PACKAGE_DIR" -name "*.pyc" -delete

#Create zip file
echo "Creating zip file..."
cd "$PACKAGE_DIR"
zip -q -r "$ZIP_FILE" .


echo "✅ Package created at: $ZIP_FILE"
echo "📊 Final Size: $(du -h "$ZIP_FILE" | cut -f1)"
