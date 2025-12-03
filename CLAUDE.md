# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

The FVH Application Evaluator is a Django REST Framework + React/TypeScript web application for collaborative evaluation of applications (e.g., funding applications) using weighted criteria. It supports multiple evaluating organizations and was developed for the AI4Cities project.

## Architecture

### Backend (Django)
- **Framework**: Django 3.x with Django REST Framework
- **Database**: PostgreSQL
- **Main App**: `application_evaluator` with models for ApplicationRound, Application, Criterion, Organization, etc.
- **API**: REST endpoints in `application_evaluator/rest.py` with ViewSets and Serializers
- **Authentication**: Token-based authentication with django-rest-auth
- **Admin**: Custom Django admin interface for managing application rounds and criteria

### Frontend (React)
- **Framework**: React 16 with TypeScript
- **Build Tool**: Vite (migrated from Create React App)
- **UI**: Bootstrap 4 + Reactstrap
- **State Management**: Local component state (no Redux/Context)
- **Key Components**: ApplicationRounds, ApplicationScores, CriterionScore, etc.

### Key Domain Models
- **ApplicationRound**: Defines evaluation criteria and scoring model
- **Application**: Items to be evaluated, with attachments and scores
- **Criterion/CriterionGroup**: Hierarchical evaluation criteria with weights
- **Organization**: Evaluating organizations with assigned users
- **ApplicationScore**: Individual scores given by evaluators

## Development Commands

### Initial Setup
```bash
# Development environment setup
sh configure_dev.sh
docker-compose up
```

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

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Docker container commands
docker exec -it applicationevaluator-web-1 python manage.py runserver 0.0.0.0:8000
docker exec -it applicationevaluator-web-1 python manage.py createsuperuser
docker exec -it applicationevaluator-web-1 python manage.py migrate
```

### Frontend (React) - from `react_ui/` directory:
```bash
# Environment setup
npm install

# Development
npm start
npm run build
npm test

# Docker container commands
docker exec -it applicationevaluator-react-1 npm start
docker exec -it applicationevaluator-react-1 npm run build
```

### Database Operations
```bash
# Access PostgreSQL
docker exec -it applicationevaluator-db-1 psql -U application_evaluator -d application_evaluator

# Database backup/restore
docker exec -it applicationevaluator-db-1 pg_dump -U application_evaluator application_evaluator > backup.sql
```

## Configuration

### Environment-Specific Settings
- **Development**: `docker-compose.dev.yml` with `.env.dev`
- **Production**: `docker-compose.prod.yml` with production settings
- **Frontend Settings**: `react_ui/src/settings.{dev,prod}.json`

### Key Configuration Files
- **Django Settings**: `django_server/application_evaluator_config/settings.py`
- **URLs**: `django_server/application_evaluator_config/urls.py`
- **Docker**: `docker-compose.{dev,prod}.yml`
- **Frontend Build**: `react_ui/vite.config.js`

## Development Workflow

### Making Changes
1. Backend changes go in `django_server/application_evaluator/`
2. Frontend changes go in `react_ui/src/`
3. Use Docker containers for consistent development environment
4. API changes require updating both REST serializers and React components

### Testing Strategy
- Django tests in `django_server/application_evaluator/tests/`
- Run backend tests with `python manage.py test`
- Frontend testing setup exists but minimal coverage
- Integration testing via admin interface and evaluator UI

### Data Flow
1. Applications imported via Django admin (CSV upload)
2. Criteria and organizations defined in admin interface
3. Evaluators access React UI to score applications
4. Scores aggregated using weighted averages
5. Results exported via UI widgets

## Key URLs and Endpoints

### Local Development
- **React UI**: http://localhost:3000
- **Django Admin**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/rest/
- **API Documentation**: http://localhost:8000/swagger-ui/

### API Endpoints
- `/rest/application_rounds/` - Application rounds management
- `/rest/applications/` - Applications CRUD
- `/rest/criteria/` - Evaluation criteria
- `/rest/organizations/` - Organizations management
- `/rest-auth/` - Authentication endpoints

## Deployment

### Container Images
- Backend: `ghcr.io/forumviriumhelsinki/applicationevaluator-backend`
- Frontend: `ghcr.io/forumviriumhelsinki/applicationevaluator-frontend`

### Production Configuration
- Uses `compose.yml` for container orchestration
- Nginx configuration in `nginx.conf.sample`
- Skaffold configuration for Kubernetes deployment in `application/skaffold.yaml`

## Common Tasks

### Adding New Evaluation Criteria
1. Create CriterionGroup and Criterion objects in Django admin
2. Frontend automatically picks up new criteria via API
3. Evaluators can then score applications against new criteria

### Importing Applications
1. Use Django admin ApplicationRound interface
2. Upload CSV with application data
3. Applications appear in evaluator UI for scoring

### User Management
1. Create users in Django admin
2. Assign to organizations
3. Organizations get access to specific application rounds

## Security Considerations
- Token-based API authentication
- CSRF protection enabled
- CORS configured for frontend-backend communication
- File upload restrictions for application attachments
- User permissions based on organization membership
