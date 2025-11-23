# 🚀 CI/CD & Code Quality Setup

## Overview

This project includes automated testing, deployment pipelines, and pre-commit hooks for maintaining high code quality.

---

## 🔄 Continuous Integration (CI)

### What Runs on Every Commit

**Location**: `.github/workflows/ci.yml`

#### 1. Testing
- Runs on Python 3.9, 3.10, and 3.11
- Executes all pytest tests
- Generates coverage reports
- Uploads to Codecov

#### 2. Linting
- **flake8**: Code style checking
- **black**: Code formatting verification
- **isort**: Import order checking
- **mypy**: Type checking

#### 3. Security
- **safety**: Checks for known security vulnerabilities in dependencies
- **bandit**: Scans code for security issues

#### 4. Docker Build
- Builds Docker image (on master branch)
- Tests container imports

### Triggers
- Push to `master`, `main`, or `develop` branches
- Pull requests to these branches

### View Results
Go to: **https://github.com/DriraYosr/bus-passenger-classifier/actions**

---

## 🚀 Continuous Deployment (CD)

### What Runs on Deployment

**Location**: `.github/workflows/cd.yml`

#### Staging Deployment
**Trigger**: Push to `master` branch

Steps:
1. Run smoke tests
2. Deploy to staging environment
3. Notify team

#### Production Deployment
**Trigger**: Git tag starting with `v` (e.g., `v1.0.0`)

Steps:
1. Run full test suite
2. Build production Docker image
3. Deploy to production
4. Create GitHub release
5. Notify team

### How to Deploy

```bash
# Deploy to staging (automatic on merge to master)
git push origin master

# Deploy to production
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## 🎯 Pre-commit Hooks

### What Are Pre-commit Hooks?

Pre-commit hooks automatically check and fix your code **before** you commit, ensuring:
- Consistent code style
- No syntax errors
- No security issues
- Proper formatting

### Setup (One-Time)

```bash
# Install pre-commit and hooks
python setup_precommit.py
```

This installs:
- ✅ **black** - Code formatter
- ✅ **isort** - Import sorter
- ✅ **flake8** - Code linter
- ✅ **bandit** - Security checker
- ✅ **mypy** - Type checker
- ✅ **trailing-whitespace** - Cleanup
- ✅ **YAML/JSON** validators

### What Happens on Commit

```bash
git commit -m "Add new feature"
```

**Automatic checks:**
```
black................................................Passed
isort................................................Passed
flake8...............................................Passed
bandit...............................................Passed
trailing-whitespace..................................Passed
check-yaml...........................................Passed
```

If any check fails, the commit is blocked and issues are auto-fixed (where possible).

### Manual Run

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

### Skip Hooks (Not Recommended)

```bash
git commit --no-verify -m "message"
```

---

## 📊 Code Coverage

### View Coverage Locally

```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### View on Codecov

After CI runs, coverage reports are uploaded to:
**https://codecov.io/gh/DriraYosr/bus-passenger-classifier**

---

## 🔧 Local Development Workflow

### 1. Before Starting Work

```bash
# Make sure pre-commit is installed
python setup_precommit.py
```

### 2. During Development

```bash
# Write code as usual
# Pre-commit hooks run automatically on commit
git add .
git commit -m "feat: Add new feature"
```

### 3. Before Pushing

```bash
# Run all tests locally
pytest tests/ -v

# Check code quality manually
pre-commit run --all-files

# Push
git push origin your-branch
```

### 4. Create Pull Request

- GitHub Actions CI runs automatically
- All checks must pass before merging
- Review coverage report

---

## 🏷️ Commit Message Format

We use **Conventional Commits** for clear history:

```bash
# Format
<type>(<scope>): <description>

# Examples
feat: Add user authentication
fix: Correct prediction endpoint error
docs: Update README with API examples
test: Add tests for data validation
refactor: Simplify feature engineering
style: Format code with black
perf: Optimize model loading time
ci: Update GitHub Actions workflow
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Formatting
- `perf`: Performance
- `ci`: CI/CD changes
- `chore`: Maintenance

---

## 🛠️ Troubleshooting

### Pre-commit Hook Fails

```bash
# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install
```

### CI Fails on GitHub

1. Check GitHub Actions logs
2. Run the same command locally:
   ```bash
   pytest tests/ -v
   flake8 src/ --max-line-length=120
   black --check src/
   ```
3. Fix issues and commit

### Skip CI (Emergency Only)

Add `[skip ci]` to commit message:
```bash
git commit -m "docs: Update README [skip ci]"
```

---

## 📈 Code Quality Metrics

### Current Status

![CI Status](https://github.com/DriraYosr/bus-passenger-classifier/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/DriraYosr/bus-passenger-classifier/branch/master/graph/badge.svg)

### Goals

- ✅ Test Coverage: > 80%
- ✅ All Linters: Pass
- ✅ Security: No vulnerabilities
- ✅ Type Hints: > 70%

---

## 🎯 Best Practices

### 1. Small, Focused Commits
```bash
# Good
git commit -m "feat: Add input validation"
git commit -m "test: Add validation tests"

# Avoid
git commit -m "Add stuff and fix things"
```

### 2. Run Tests Before Committing
```bash
pytest tests/ -v
```

### 3. Let Hooks Fix Issues
```bash
# Hooks will auto-format
git add .
git commit -m "feat: Add feature"
# black and isort fix files automatically
git add .
git commit -m "feat: Add feature"
```

### 4. Keep CI Green
- Never merge failing CI
- Fix issues immediately
- Don't use `[skip ci]` unless absolutely necessary

---

## 🚀 For Your Presentation

### Show CI/CD Pipeline

1. **Open GitHub Actions**:
   https://github.com/DriraYosr/bus-passenger-classifier/actions

2. **Show workflow run**:
   - Multiple Python versions tested
   - Linting and security checks
   - Docker build success

3. **Demonstrate pre-commit**:
   ```bash
   # Make a change with wrong formatting
   echo "x=1" >> src/config.py
   git add .
   git commit -m "test: Demo pre-commit"
   # Shows automatic formatting
   ```

4. **Explain deployment**:
   > "On every push, automated tests run. When we tag a release, it automatically deploys to production with full testing and creates a GitHub release."

---

## 📚 Additional Resources

- [Pre-commit documentation](https://pre-commit.com/)
- [GitHub Actions docs](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Codecov](https://codecov.io/)

---

**✅ Your project now has professional-grade CI/CD automation!**
