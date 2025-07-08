# 🚀 School of Prompt Release Process

This document outlines the complete release process for School of Prompt, from development to PyPI publication.

## 📋 Table of Contents

- [Overview](#overview)
- [Pre-Release Checklist](#pre-release-checklist)
- [Release Types](#release-types)
- [Automated Release Process](#automated-release-process)
- [Manual Release Steps](#manual-release-steps)
- [Post-Release Tasks](#post-release-tasks)
- [Emergency Releases](#emergency-releases)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

School of Prompt uses a **fully automated release process** with GitHub Actions. The workflow supports:

- ✅ **Semantic versioning** (patch, minor, major)
- ✅ **Automated testing** across multiple Python versions and platforms
- ✅ **Security scanning** with Bandit and Safety
- ✅ **Dual PyPI publishing** (Test PyPI + Production PyPI)
- ✅ **Automatic release notes** generation
- ✅ **Cross-platform validation** (Linux, macOS, Windows)

## ✅ Pre-Release Checklist

Before creating a release, ensure:

### 🧪 Code Quality
- [ ] All tests pass: `python tests/test_framework.py`
- [ ] Code is formatted: `black school_of_prompt/ examples/ tests/`
- [ ] Imports are sorted: `isort school_of_prompt/ examples/ tests/`
- [ ] No linting errors: `flake8 school_of_prompt/`
- [ ] Documentation is updated

### 📦 Package Validation  
- [ ] Package builds cleanly: `python setup.py check --strict`
- [ ] Examples work with current code
- [ ] No sensitive information in code
- [ ] MANIFEST.in includes/excludes correct files

### 🔐 Security & Dependencies
- [ ] No security vulnerabilities: `bandit -r school_of_prompt/`
- [ ] Dependencies are up to date: `safety check`
- [ ] No unused dependencies

### 📚 Documentation
- [ ] README.md reflects current features
- [ ] RELEASE_NOTES.md is updated (if needed)
- [ ] Examples are working and current
- [ ] API documentation matches implementation

## 🏷️ Release Types

School of Prompt follows [Semantic Versioning](https://semver.org/):

### 🔧 **Patch Release** (0.3.0 → 0.3.1)
- Bug fixes
- Performance improvements  
- Documentation updates
- Security patches

### ⚡ **Minor Release** (0.3.0 → 0.4.0)
- New features
- API enhancements (backward compatible)
- New metrics or data sources
- Enhanced functionality

### 🚀 **Major Release** (0.3.0 → 1.0.0)
- Breaking API changes
- Architecture overhauls
- Removal of deprecated features
- Major new capabilities

## 🤖 Automated Release Process

### Step 1: Trigger Release Workflow

1. **Navigate to GitHub Actions**:
   ```
   GitHub Repository → Actions → "🏷️ Create Release"
   ```

2. **Click "Run workflow"**:
   - **Branch**: `master` (default)
   - **Version bump type**: `patch`, `minor`, or `major`
   - **Pre-release**: Check if this is a beta/RC release

3. **Click "Run workflow"** to start the process

### Step 2: Automated Process Execution

The workflow automatically performs:

#### 🔍 **Version Management**
```bash
# Current version detection
CURRENT_VERSION=$(python -c "import school_of_prompt; print(school_of_prompt.__version__)")

# Version calculation (patch: 0.3.0 → 0.3.1)
NEW_VERSION="$major.$minor.$((patch + 1))"

# File updates
sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" school_of_prompt/__init__.py
sed -i "s/version=\".*\"/version=\"$NEW_VERSION\"/" setup.py
```

#### 📝 **Release Notes Generation**
```bash
# Automatic changelog from git commits
git log "$LATEST_TAG..HEAD" --pretty=format:"- %s" --reverse
```

#### 🏷️ **Git Tagging**
```bash
# Create annotated tag
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
git push origin master
git push origin --tags
```

#### 🚀 **GitHub Release Creation**
```bash
# Create GitHub release with notes
gh release create "v$NEW_VERSION" \
  --title "🎸 School of Prompt v$NEW_VERSION" \
  --notes-file release_notes.md
```

### Step 3: CI/CD Pipeline Activation

Once the release is created, the **CI/CD pipeline automatically triggers**:

#### 🧪 **Multi-Platform Testing**
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating systems**: Ubuntu, Windows, macOS
- **Test types**: Unit, integration, installation

#### 🔒 **Security Scanning**
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability checking
- **Static analysis**: Code quality validation

#### 🏗️ **Package Building**
```bash
# Clean build
python -m build

# Package validation
twine check dist/*
```

#### 📦 **PyPI Publishing**
1. **Test PyPI**: Validates package installation
2. **Production PyPI**: Final publication
3. **Installation verification**: Cross-platform testing

## 🛠️ Manual Release Steps

If automation fails, you can create releases manually:

### 1. Version Update
```bash
# Update version manually
vim school_of_prompt/__init__.py  # Change __version__
vim setup.py                      # Change version

# Verify changes
python -c "import school_of_prompt; print(school_of_prompt.__version__)"
```

### 2. Create Git Tag
```bash
# Commit version changes
git add school_of_prompt/__init__.py setup.py
git commit -m "🔖 Bump version to v0.3.1"

# Create and push tag
git tag -a "v0.3.1" -m "Release v0.3.1"
git push origin master
git push origin --tags
```

### 3. Manual GitHub Release
```bash
# Using GitHub CLI
gh release create "v0.3.1" \
  --title "🎸 School of Prompt v0.3.1" \
  --notes "Release notes here"
```

### 4. Manual PyPI Publishing
```bash
# Build package
python -m build

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ school-of-prompt==0.3.1

# Upload to Production PyPI
twine upload dist/*
```

## ✅ Post-Release Tasks

After a successful release:

### 📊 **Verification**
- [ ] Check PyPI package page: https://pypi.org/project/school-of-prompt/
- [ ] Verify installation: `pip install school-of-prompt==X.X.X`
- [ ] Test basic functionality
- [ ] Check GitHub release page

### 📢 **Communication**
- [ ] Update project documentation if needed
- [ ] Announce release (if major/minor)
- [ ] Update dependent projects
- [ ] Monitor for user feedback

### 🔍 **Monitoring**
- [ ] Check download statistics
- [ ] Monitor for bug reports
- [ ] Review CI/CD logs for any issues
- [ ] Update issue templates if needed

## 🚨 Emergency Releases

For critical security fixes or major bugs:

### Fast-Track Process
1. **Create hotfix branch**:
   ```bash
   git checkout -b hotfix/critical-fix
   ```

2. **Make minimal fix**:
   - Focus only on the critical issue
   - Avoid unrelated changes

3. **Test thoroughly**:
   ```bash
   python tests/test_framework.py
   ```

4. **Create emergency release**:
   - Use patch version bump
   - Mark as critical in release notes
   - Follow normal release process

### Emergency Checklist
- [ ] Issue is genuinely critical (security/breaking)
- [ ] Fix is minimal and well-tested
- [ ] Release notes clearly indicate emergency nature
- [ ] Stakeholders are notified

## 🔧 Troubleshooting

### Common Issues

#### **Release Workflow Fails**
```bash
# Check workflow logs in GitHub Actions
# Common fixes:
- Ensure all tests pass locally first
- Check for merge conflicts
- Verify GitHub secrets are configured
```

#### **PyPI Upload Fails**
```bash
# Check for version conflicts
twine check dist/*

# Verify credentials
twine upload --repository testpypi dist/* --verbose
```

#### **Version Calculation Errors**
```bash
# Verify current version format
python -c "import school_of_prompt; print(school_of_prompt.__version__)"

# Ensure semantic versioning (X.Y.Z)
```

#### **Test Failures**
```bash
# Run tests locally first
python tests/test_framework.py

# Check specific Python version
python3.8 tests/test_framework.py
```

### GitHub Secrets Required

Ensure these secrets are configured in repository settings:

- `PYPI_API_TOKEN`: Production PyPI publishing
- `TEST_PYPI_API_TOKEN`: Test PyPI publishing  
- `CODECOV_TOKEN`: Code coverage reporting (optional)

### Environment Setup

For manual releases, ensure you have:

```bash
# Required tools
pip install build twine bump2version

# GitHub CLI (for release creation)
gh auth login
```

## 📚 Additional Resources

- **GitHub Actions Logs**: Repository → Actions tab
- **PyPI Package Page**: https://pypi.org/project/school-of-prompt/
- **Semantic Versioning**: https://semver.org/
- **GitHub CLI Docs**: https://cli.github.com/manual/
- **Twine Documentation**: https://twine.readthedocs.io/

---

## 🎸 Summary

The School of Prompt release process is designed to be:

- **🤖 Automated**: Minimal manual intervention required
- **🔒 Secure**: Multiple validation and security checks  
- **🧪 Tested**: Cross-platform validation before release
- **📚 Documented**: Automatic release notes and documentation
- **🚀 Fast**: From trigger to PyPI in minutes

For most releases, simply use the **"Create Release" GitHub Action** with the appropriate version bump type. The automation handles the rest! 🎸

**Need help?** Check the troubleshooting section or review recent workflow runs in GitHub Actions.