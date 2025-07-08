#!/bin/bash

# Local CI/CD Check Script
# Run this script to verify your changes will pass CI/CD pipeline

set -e

echo "🔍 Running local CI/CD checks..."

echo ""
echo "1️⃣  Running tests..."
python -m pytest tests/ -v --tb=short

echo ""
echo "2️⃣  Checking code formatting with Black..."
black --check school_of_prompt/ examples/ tests/

echo ""
echo "3️⃣  Checking import sorting with isort..."
isort --check-only school_of_prompt/ examples/ tests/

echo ""
echo "4️⃣  Running security checks with Bandit..."
bandit -r school_of_prompt/ --quiet

echo ""
echo "5️⃣  Checking for dependency vulnerabilities with Safety..."
safety check --json > /dev/null

echo ""
echo "✅ All checks passed! Your code is ready for CI/CD pipeline."