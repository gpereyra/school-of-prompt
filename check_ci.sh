#!/bin/bash

# Local CI/CD Check Script
# Run this script to verify your changes will pass CI/CD pipeline

set -e

echo "🔍 Running local CI/CD checks..."

echo ""
echo "1️⃣  Running tests..."
python -m pytest tests/ -v --tb=short

echo ""
echo "2️⃣  Checking for syntax errors with Flake8..."
flake8 school_of_prompt/ --count --select=E9,F63,F7,F82 --show-source --statistics

echo ""
echo "3️⃣  Running security checks with Bandit..."
bandit -r school_of_prompt/ --severity-level medium --quiet

echo ""
echo "✅ All checks passed! Your code is ready for CI/CD pipeline."