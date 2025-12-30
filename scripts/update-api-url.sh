#!/bin/bash

# Script to update API URL in frontend files for deployment
# Usage: ./scripts/update-api-url.sh https://your-app.up.railway.app

if [ -z "$1" ]; then
    echo "Usage: ./scripts/update-api-url.sh <your-backend-url>"
    echo "Example: ./scripts/update-api-url.sh https://attendance-system.up.railway.app"
    exit 1
fi

BACKEND_URL=$1
API_URL="${BACKEND_URL}/api"

echo "========================================="
echo "Updating Frontend API URLs"
echo "========================================="
echo "Backend URL: $BACKEND_URL"
echo "API URL: $API_URL"
echo ""

# Files to update
FILES=(
    "frontend/js/main.js"
    "frontend/js/employee.js"
    "frontend/js/employee-settings.js"
    "frontend/js/manager.js"
    "frontend/js/manager-settings.js"
    "frontend/js/register.js"
    "frontend/js/user-management.js"
    "frontend/js/worker-scan.js"
)

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "Error: frontend directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Backup files
echo "Creating backups..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$file.backup"
        echo "✓ Backed up $file"
    fi
done
echo ""

# Update API URLs
echo "Updating API URLs..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        # Replace localhost URLs with production URL
        sed -i.tmp "s|const API_BASE_URL = 'http://localhost:5001/api'|const API_BASE_URL = '${API_URL}'|g" "$file"
        sed -i.tmp "s|const API_BASE_URL = 'http://127.0.0.1:5001/api'|const API_BASE_URL = '${API_URL}'|g" "$file"
        sed -i.tmp "s|http://localhost:5001/api|${API_URL}|g" "$file"
        sed -i.tmp "s|http://127.0.0.1:5001/api|${API_URL}|g" "$file"
        rm -f "$file.tmp"
        echo "✓ Updated $file"
    else
        echo "⚠ File not found: $file"
    fi
done

echo ""
echo "========================================="
echo "✓ API URLs Updated Successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review the changes in frontend/js/*.js files"
echo "2. Deploy frontend to Netlify/Vercel"
echo "3. Update backend CORS_ORIGINS to match frontend domain"
echo ""
echo "To restore original files (if needed):"
echo "  for file in frontend/js/*.js.backup; do mv \"\$file\" \"\${file%.backup}\"; done"
echo ""
