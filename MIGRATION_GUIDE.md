# Django + React Application Modernization Guide

This guide outlines the systematic process for modernizing Django + React applications to follow modern standards, 12-factor app principles, and security best practices.

## Prerequisites

- Applications using Django backend + React frontend
- Currently using pipenv/pip + yarn/npm
- Docker-based deployment
- Environment variable configuration

## Phase 1: Python Backend Modernization

### 1.1 Migrate from pipenv to uv pip

**Audit Current State:**
```bash
# Check current dependency management
ls django_server/Pipfile*
ls django_server/requirements*.txt
ls django_server/pyproject.toml
```

**Create pyproject.toml:**
```bash
cd django_server/
# Convert Pipfile dependencies to pyproject.toml format
```

**Required pyproject.toml structure:**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-app-name"
version = "0.1.0"
description = "Your app description"
requires-python = ">=3.9"
dependencies = [
    # Convert from Pipfile [packages] section
]

[project.optional-dependencies]
dev = [
    # Convert from Pipfile [dev-packages] section
]

[tool.flake8]
max-line-length = 120
exclude = ["migrations", "__pycache__", "*.pyc"]

[tool.coverage.run]
source = ["."]
omit = ["*/migrations/*", "*/venv/*", "*/tests/*"]
```

**Update Dockerfile:**
```dockerfile
# Replace pipenv installation with uv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# Install dependencies
COPY pyproject.toml ./
RUN uv pip install --system -e .
```

### 1.2 Security Hardening

**Fix hardcoded secrets in settings.py:**
```python
# Before
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-key')

# After
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'dev-only-secret-key-not-for-production'  # pragma: allowlist secret
    else:
        raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production")
```

**Security checklist:**
- [ ] No hardcoded secrets with production fallbacks
- [ ] ALLOWED_HOSTS configured via environment variables
- [ ] DEBUG=False enforced in production
- [ ] Database credentials via environment variables
- [ ] CORS settings configurable

## Phase 2: Frontend Modernization

### 2.1 Migrate from yarn to npm

**Remove yarn artifacts:**
```bash
cd react_ui/
rm -f yarn.lock
```

**Install with npm:**
```bash
npm install  # Generates package-lock.json
```

**Update documentation references:**
- README.md: Replace `yarn install` → `npm install`
- CLAUDE.md: Update development commands
- Any scripts or CI files

### 2.2 Address Security Vulnerabilities

**Apply safe fixes:**
```bash
npm audit
npm audit fix
```

**Document breaking changes needed:**
- Note react-scripts version upgrades needed
- Document Bootstrap version considerations
- Plan for React version migrations

## Phase 3: Docker & Infrastructure

### 3.1 Docker Compose Modernization

**Remove deprecated version:**
```yaml
# Before
version: '3.8'
services:

# After
services:
```

**Health checks verification:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app_user}"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### 3.2 Environment Configuration

**Create comprehensive .env.example:**
```bash
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,localhost

# Database Configuration
POSTGRES_DB=app_prod
POSTGRES_USER=app_user
POSTGRES_PASSWORD=your-password
SQL_HOST=postgres
SQL_PORT=5432

# CORS Configuration
DJANGO_CORS_ALLOW_ALL=False
DJANGO_CORS_ALLOWED_ORIGINS=https://yourdomain.com

# External Services
SENTRY_DSN=https://your-sentry-dsn
# Add other service configurations
```

## Phase 4: 12-Factor App Compliance Audit

### 4.1 Validation Checklist

**I. Codebase**
- [ ] Single repository with clear service separation
- [ ] No environment-specific code in repository

**II. Dependencies**
- [ ] Explicit dependency declarations (pyproject.toml, package.json)
- [ ] Lock files present (package-lock.json)

**III. Config**
- [ ] All configuration via environment variables
- [ ] No secrets in code
- [ ] .env.example provided

**IV. Backing Services**
- [ ] Database treated as attached resource
- [ ] External services configurable via environment

**V. Build, Release, Run**
- [ ] Clear separation via Docker stages
- [ ] Reproducible builds

**VI. Processes**
- [ ] Stateless application processes
- [ ] No local file storage for user data

**VII. Port Binding**
- [ ] Services export via ports
- [ ] No hardcoded internal networking

**VIII. Concurrency**
- [ ] Process scaling via environment (gunicorn workers)
- [ ] Horizontal scaling ready

**IX. Disposability**
- [ ] Fast startup (health checks)
- [ ] Graceful shutdown

**X. Dev/Prod Parity**
- [ ] Docker ensures environment consistency
- [ ] Same services in all environments

**XI. Logs**
- [ ] Logs to stdout/stderr
- [ ] Structured logging configured

**XII. Admin Processes**
- [ ] Management commands via container exec
- [ ] Database migrations as admin processes

### 4.2 Common Issues to Fix

**Security Issues:**
```bash
# Check for hardcoded secrets
grep -r "SECRET_KEY\|PASSWORD\|TOKEN" --include="*.py" --exclude-dir=migrations .

# Check for hardcoded DEBUG
find . -name "*.py" -exec grep -l "DEBUG.*=.*True" {} \;

# Check for localhost hardcoding
grep -r "localhost\|127.0.0.1" --include="*.py" . | grep -v ALLOWED_HOSTS
```

**Configuration Issues:**
```bash
# Verify environment variable usage
grep -r "os.environ.get" --include="*.py" .

# Check for proper defaults
grep -r "os.environ.get.*," --include="*.py" .
```

## Phase 5: Documentation Updates

### 5.1 Update Installation Instructions

**README.md template:**
```markdown
## Prerequisites
* Python 3.9+ with uv
* Node.js 18+ with npm
* PostgreSQL
* Docker (for containerized deployment)

## Development Setup

### Backend (Django)
```bash
cd django_server/
uv pip install -e .
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend (React)
```bash
cd react_ui/
npm install
npm start
```

### Docker Development
```bash
docker-compose up
```
```

### 5.2 Update CLAUDE.md

**Development commands section:**
```markdown
### Backend (Django) - from `django_server/` directory:
```bash
# Environment setup
uv pip install -e .

# Database operations
python manage.py migrate
python manage.py runserver

# Code quality
flake8
python manage.py test
```

### Frontend (React) - from `react_ui/` directory:
```bash
# Environment setup
npm install

# Development
npm start
npm run build
npm test
```
```

## Phase 6: Testing & Validation

### 6.1 Build Testing
```bash
# Test Docker builds
docker-compose build

# Test full stack
docker-compose up

# Verify health endpoints
curl http://localhost:8000/health/
curl http://localhost:3000/
```

### 6.2 Security Validation
```bash
# Backend security check
cd django_server/
python manage.py check --deploy

# Frontend vulnerability scan
cd react_ui/
npm audit
```

### 6.3 Dependency Verification
```bash
# Verify Python dependencies
cd django_server/
uv pip check

# Verify Node dependencies
cd react_ui/
npm ls
```

## Phase 7: Follow-up Recommendations

### 7.1 Immediate Next Steps
- [ ] Set up pre-commit hooks
- [ ] Configure GitHub Actions CI/CD
- [ ] Implement release-please for automated releases
- [ ] Set up Dependabot for dependency updates

### 7.2 Medium-term Modernization
- [ ] React version upgrade (16.x → 18.x)
- [ ] Bootstrap upgrade (4.x → 5.x)
- [ ] Django version upgrade if needed
- [ ] TypeScript migration completion

### 7.3 Long-term Architecture
- [ ] Consider microservices if application grows
- [ ] Implement proper monitoring (OpenTelemetry)
- [ ] Set up proper logging aggregation
- [ ] Consider Kubernetes deployment

## Troubleshooting Common Issues

### uv Installation Issues
```bash
# If uv not found in PATH
ENV PATH="/root/.local/bin:$PATH"

# Alternative installation method
RUN pip install uv
```

### Docker Build Failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Environment Variable Issues
```bash
# Verify .env file loading
docker-compose config

# Check environment in container
docker-compose exec web printenv
```

---

## Migration Checklist Summary

**Phase 1: Python Backend**
- [ ] Create pyproject.toml from Pipfile
- [ ] Update Dockerfile for uv pip
- [ ] Fix hardcoded secrets
- [ ] Update Python version requirements

**Phase 2: Frontend**
- [ ] Remove yarn.lock
- [ ] Generate package-lock.json with npm
- [ ] Update documentation references
- [ ] Apply npm audit fixes

**Phase 3: Infrastructure**
- [ ] Remove docker-compose version attribute
- [ ] Verify health checks
- [ ] Update .env.example

**Phase 4: Compliance**
- [ ] Run 12-factor audit
- [ ] Fix security issues
- [ ] Verify environment configuration

**Phase 5: Documentation**
- [ ] Update README.md
- [ ] Update CLAUDE.md
- [ ] Document new workflows

**Phase 6: Testing**
- [ ] Test Docker builds
- [ ] Verify application functionality
- [ ] Run security scans

This systematic approach ensures consistent modernization across similar Django + React applications while maintaining security and operational best practices.
