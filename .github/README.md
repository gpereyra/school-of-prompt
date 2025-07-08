# 🎸 School of Prompt CI/CD Pipeline

This directory contains the complete CI/CD automation for School of Prompt, providing enterprise-grade development workflows.

## 🚀 Workflows Overview

### 📋 Main Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI/CD Pipeline** | Push, PR, Release | Full testing, building, and publishing |
| **Release Creation** | Manual dispatch | Version bumping and release creation |
| **Code Quality** | PR, Manual | Formatting, linting, security checks |
| **Documentation** | Push to docs | Validate examples and update stats |
| **Dependencies** | Weekly schedule | Automated dependency updates |

### 🔄 Workflow Details

#### 1. **CI/CD Pipeline** (`ci-cd.yml`)

**Triggers:**
- Push to `master`/`main`/`develop`
- Pull requests to `master`/`main`
- Published releases

**Jobs:**
1. **🧪 Test Suite**
   - Multi-Python version testing (3.8-3.12)
   - Code coverage reporting
   - Dependency caching

2. **🔒 Security Scan**
   - Bandit security analysis
   - Safety vulnerability check
   - Artifact upload for reports

3. **🏗️ Build Package**
   - Python wheel and source distribution
   - Package validation with twine
   - Artifact storage

4. **📦 Installation Test**
   - Cross-platform installation testing
   - Import verification
   - Multi-Python version support

5. **🧪 Test PyPI Publishing**
   - Automatic publishing to TestPyPI on `master` push
   - Skip existing versions

6. **🚀 Production PyPI Publishing**
   - Automatic publishing to PyPI on release
   - Production deployment

7. **📝 Release Notes Update**
   - Automatic changelog generation
   - GitHub release enhancement
   - PyPI links integration

#### 2. **Release Creation** (`release.yml`)

**Triggers:**
- Manual workflow dispatch with version type selection

**Features:**
- Semantic version bumping (patch/minor/major)
- Automatic changelog generation
- Git tag creation and pushing
- GitHub release creation
- Pre-release support

#### 3. **Code Quality** (`code-quality.yml`)

**Triggers:**
- Pull requests
- Manual dispatch for auto-formatting

**Checks:**
- Black code formatting
- isort import sorting
- Flake8 linting
- Bandit security analysis
- Auto-format PR creation (manual)

#### 4. **Documentation** (`docs.yml`)

**Triggers:**
- Changes to documentation files
- Manual dispatch

**Tasks:**
- Example file validation
- Link checking
- Repository statistics generation
- Documentation consistency

#### 5. **Dependencies** (`dependencies.yml`)

**Triggers:**
- Weekly schedule (Mondays 9 AM UTC)
- Manual dispatch

**Features:**
- Dependency version updates
- Security vulnerability scanning
- Automated PR creation
- Review assignment

## 🔧 Setup Requirements

### GitHub Secrets

Configure these secrets in your GitHub repository:

| Secret | Purpose | Required |
|--------|---------|----------|
| `PYPI_API_TOKEN` | PyPI publishing | ✅ Yes |
| `TEST_PYPI_API_TOKEN` | TestPyPI publishing | ✅ Yes |
| `GITHUB_TOKEN` | Release management | 🔄 Auto |

### PyPI Tokens Setup

1. **PyPI Production Token**:
   ```bash
   # Go to https://pypi.org/manage/account/token/
   # Create token with scope: "Entire account"
   # Add as PYPI_API_TOKEN secret
   ```

2. **TestPyPI Token**:
   ```bash
   # Go to https://test.pypi.org/manage/account/token/  
   # Create token with scope: "Entire account"
   # Add as TEST_PYPI_API_TOKEN secret
   ```

## 🎯 Usage

### Creating a Release

1. **Manual Release**:
   ```bash
   # Go to Actions → Create Release
   # Select version type: patch/minor/major
   # Choose pre-release if needed
   # Click "Run workflow"
   ```

2. **What Happens**:
   - Version is bumped in all files
   - Git tag is created and pushed
   - GitHub release is created
   - CI/CD pipeline automatically builds and publishes to PyPI

### Development Workflow

1. **Feature Development**:
   ```bash
   git checkout -b feature/amazing-feature
   # Make changes
   git push origin feature/amazing-feature
   # Create PR → triggers CI checks
   ```

2. **Code Quality**:
   ```bash
   # Manual formatting (if needed)
   # Go to Actions → Code Quality → Run workflow
   # This creates a PR with auto-formatting
   ```

3. **Merging**:
   ```bash
   # PR merge to master triggers:
   # - Full test suite
   # - TestPyPI publishing
   # - Documentation updates
   ```

### Monitoring

- **Test Results**: Check Actions tab for test outcomes
- **Coverage**: View coverage reports in PR comments
- **Security**: Review security scan artifacts
- **Dependencies**: Monitor weekly dependency PRs

## 🛠️ Local Development

### Pre-commit Setup

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Manual run
pre-commit run --all-files
```

### Testing Locally

```bash
# Run full test suite
pytest tests/ -v --cov=school_of_prompt

# Code quality checks
black --check school_of_prompt/ examples/ tests/
isort --check-only school_of_prompt/ examples/ tests/
flake8 school_of_prompt/ examples/ tests/
bandit -r school_of_prompt/
```

### Manual Release Testing

```bash
# Test package build
python -m build
twine check dist/*

# Test installation
pip install dist/*.whl
python -c "import school_of_prompt; print(school_of_prompt.__version__)"
```

## 🔍 Troubleshooting

### Common Issues

1. **PyPI Publishing Fails**:
   - Check API tokens are valid
   - Verify version not already published
   - Review package metadata

2. **Tests Fail in CI**:
   - Check Python version compatibility
   - Verify dependencies are pinned correctly
   - Review test environment differences

3. **Security Scan Issues**:
   - Review Bandit report artifacts
   - Check Safety vulnerability reports
   - Update dependencies if needed

4. **Release Creation Fails**:
   - Verify git history is clean
   - Check version format in files
   - Ensure bump2version configuration is correct

### Debugging

```bash
# Check workflow logs in GitHub Actions
# Download artifacts for detailed reports
# Review specific job outputs for errors
```

## 📋 Best Practices

1. **Commit Messages**: Use conventional commits for better changelog generation
2. **Version Bumping**: Use semantic versioning (MAJOR.MINOR.PATCH)
3. **Security**: Regularly review and update dependencies
4. **Testing**: Maintain high test coverage (>90%)
5. **Documentation**: Keep examples and docs updated

## 🎸 Rock Your CI/CD!

This comprehensive pipeline ensures:
- ✅ Code quality and security
- ✅ Automated testing and validation
- ✅ Seamless releases and publishing
- ✅ Documentation consistency
- ✅ Dependency management

**Every push rocks, every release is a hit!** 🤘