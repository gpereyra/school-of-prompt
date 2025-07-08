# Release Process

Simple, practical guide for releasing School of Prompt.

## Current Setup

- **Version Management**: Automated via GitHub Actions
- **PyPI Publishing**: Manual (simplified CI/CD pipeline)
- **Testing**: Automated via CI/CD

## Release Process

### 1. Automated Version Update (Recommended)

**Use GitHub Actions to handle version bumping:**

1. Go to **GitHub → Actions → "Create Release"**
2. Click **"Run workflow"**
3. Select version type:
   - **patch**: Bug fixes (0.3.0 → 0.3.1) 
   - **minor**: New features (0.3.0 → 0.4.0)
   - **major**: Breaking changes (0.3.0 → 1.0.0)
4. Click **"Run workflow"**

**This automatically:**
- Updates version in `school_of_prompt/__init__.py` and `setup.py`
- Creates git tag (e.g., `v0.3.1`)
- Creates GitHub release with generated notes
- Pushes changes to repository

### 2. Manual PyPI Publishing

**After the automated release, manually publish to PyPI:**

```bash
# 1. Pull the latest changes (including new version)
git pull origin master

# 2. Build the package
python -m build

# 3. Check the package
twine check dist/*

# 4. Upload to PyPI
twine upload dist/*
```

### 3. Verification

**Verify the release:**

```bash
# Check PyPI page
https://pypi.org/project/school-of-prompt/

# Test installation
pip install school-of-prompt==X.X.X

# Basic functionality test
python -c "import school_of_prompt; print(school_of_prompt.__version__)"
```

## Manual Release (If Automation Fails)

### 1. Update Version Manually

```bash
# Edit version in both files
vim school_of_prompt/__init__.py  # Update __version__ = "X.X.X"
vim setup.py                      # Update version="X.X.X"
```

### 2. Create Release

```bash
# Commit and tag
git add school_of_prompt/__init__.py setup.py
git commit -m "Bump version to vX.X.X"
git tag -a "vX.X.X" -m "Release vX.X.X"
git push origin master
git push origin --tags

# Create GitHub release
gh release create "vX.X.X" --title "School of Prompt vX.X.X" --notes "Release notes"
```

### 3. Publish to PyPI

```bash
# Build and upload
python -m build
twine upload dist/*
```

## Requirements

### Tools Needed

```bash
# Install required tools
pip install build twine

# GitHub CLI (for manual releases)
gh auth login
```

### PyPI Authentication

**Option 1: API Token (Recommended)**
```bash
# Configure .pypirc with API token
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-your-api-token-here
EOF
```

**Option 2: Environment Variable**
```bash
export TWINE_PASSWORD="pypi-your-api-token-here"
twine upload dist/*
```

## Pre-Release Checklist

Before releasing:

- [ ] All tests pass: `./check_ci.sh`
- [ ] Version is correctly incremented
- [ ] Changes are documented
- [ ] No sensitive information in code

## Release Types

- **Patch (0.3.0 → 0.3.1)**: Bug fixes, documentation updates
- **Minor (0.3.0 → 0.4.0)**: New features, backward compatible changes  
- **Major (0.3.0 → 1.0.0)**: Breaking changes, major new features

## Emergency Releases

For critical fixes:

1. Create hotfix branch: `git checkout -b hotfix/critical-fix`
2. Make minimal fix and test thoroughly
3. Use automated release workflow with patch version
4. Publish immediately to PyPI

## Troubleshooting

### Common Issues

**Version conflicts on PyPI:**
```bash
# Check if version already exists
pip index versions school-of-prompt
```

**Build failures:**
```bash
# Clean build directory
rm -rf dist/ build/
python -m build
```

**Upload failures:**
```bash
# Check package validity
twine check dist/*

# Verbose upload for debugging
twine upload dist/* --verbose
```

## Current Limitations

- PyPI publishing is manual (not automated in CI/CD)
- No test PyPI publishing step
- Manual verification required

This simplified process balances automation with control, avoiding the complexity of full CI/CD publishing while maintaining reliable version management.