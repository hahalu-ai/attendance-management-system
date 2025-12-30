#!/bin/bash

echo "========================================="
echo "Railway Deployment Verification Script"
echo "========================================="
echo ""

cd "$(dirname "$0")/.." || exit 1

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "✗ Error: backend directory not found"
    exit 1
fi

cd backend || exit 1

echo "Checking deployment files..."
echo ""

# Files to check
declare -A files
files["Procfile"]="Railway process file"
files["railway.json"]="Railway configuration"
files["nixpacks.toml"]="Nixpacks configuration"
files["start.sh"]="Startup script"
files["runtime.txt"]="Python runtime version"
files["requirements.txt"]="Python dependencies"
files["run.py"]="Application entry point"
files[".env.example"]="Environment template"

all_present=true

for file in "${!files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file - ${files[$file]}"
    else
        echo "✗ MISSING: $file - ${files[$file]}"
        all_present=false
    fi
done

echo ""
echo "Checking file permissions..."

if [ -x "start.sh" ]; then
    echo "✓ start.sh is executable"
else
    echo "⚠ start.sh is not executable - fixing..."
    chmod +x start.sh
    echo "✓ Fixed: start.sh is now executable"
fi

echo ""
echo "Checking Python dependencies..."

if grep -q "gunicorn" requirements.txt; then
    echo "✓ gunicorn is in requirements.txt"
else
    echo "✗ gunicorn is missing from requirements.txt"
    all_present=false
fi

if grep -q "Flask" requirements.txt; then
    echo "✓ Flask is in requirements.txt"
else
    echo "✗ Flask is missing from requirements.txt"
    all_present=false
fi

if grep -q "mysql-connector-python" requirements.txt; then
    echo "✓ mysql-connector-python is in requirements.txt"
else
    echo "✗ mysql-connector-python is missing from requirements.txt"
    all_present=false
fi

echo ""
echo "Checking directory structure..."

if [ -d "app" ]; then
    echo "✓ app/ directory exists"

    if [ -f "app/__init__.py" ]; then
        echo "  ✓ app/__init__.py exists"
    else
        echo "  ✗ app/__init__.py missing"
        all_present=false
    fi

    if [ -f "app/config.py" ]; then
        echo "  ✓ app/config.py exists"
    else
        echo "  ✗ app/config.py missing"
        all_present=false
    fi
else
    echo "✗ app/ directory missing"
    all_present=false
fi

if [ -d "database" ]; then
    echo "✓ database/ directory exists"

    if [ -f "database/init_database.sql" ]; then
        echo "  ✓ database/init_database.sql exists"
    else
        echo "  ✗ database/init_database.sql missing"
        all_present=false
    fi
else
    echo "✗ database/ directory missing"
    all_present=false
fi

echo ""
echo "Checking Git status..."

cd .. || exit 1

if [ -d ".git" ]; then
    echo "✓ Git repository initialized"

    # Check if there are uncommitted changes
    if git diff --quiet && git diff --cached --quiet; then
        echo "✓ No uncommitted changes"
    else
        echo "⚠ Warning: You have uncommitted changes"
        echo ""
        echo "Uncommitted files:"
        git status --short
        echo ""
        echo "Run these commands to commit:"
        echo "  git add ."
        echo "  git commit -m 'Add Railway deployment configuration'"
        echo "  git push origin main"
    fi

    # Check remote
    if git remote get-url origin &> /dev/null; then
        remote_url=$(git remote get-url origin)
        echo "✓ Git remote configured: $remote_url"
    else
        echo "⚠ Warning: No git remote configured"
        echo "  Add remote with: git remote add origin <your-github-url>"
    fi
else
    echo "⚠ Warning: Git repository not initialized"
    echo "  Initialize with: git init"
fi

echo ""
echo "========================================="

if [ "$all_present" = true ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo "========================================="
    echo ""
    echo "Your project is ready for Railway deployment!"
    echo ""
    echo "Next steps:"
    echo "1. Commit and push to GitHub (if not already done)"
    echo "2. Create project on Railway.app"
    echo "3. Set Root Directory to 'backend'"
    echo "4. Add MySQL database"
    echo "5. Configure environment variables"
    echo "6. Deploy!"
    echo ""
    echo "See DEPLOYMENT_GUIDE.md for detailed instructions"
else
    echo "❌ SOME CHECKS FAILED"
    echo "========================================="
    echo ""
    echo "Please fix the missing files/directories above"
    echo "See RAILWAY_TROUBLESHOOTING.md for help"
fi

echo ""
