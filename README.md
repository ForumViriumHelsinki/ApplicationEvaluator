# DjangoReactApp

Boilerplate code to set up a Django / React web app with:
 * Django >=3.0
 * Postgres db
 * Django Rest Framework
 * Swagger ReST documentation at /swagger-ui/
 * Django-rest-auth for authentication over ReST
   * react_ui/src/sessionRequest.js for UI-side integration to that
 * Github Action for running as CI:
   * Django tests with coverage
   * Flake8 code style verification
 * Create React App-generated React app boilerplate
 * Bootstrap 4 with FVH color theme
 * Docker scripts
 
To use this boilerplate in a new project:
 * Go to https://github.com/ForumViriumHelsinki/DjangoReactApp
 * Click "Use this template"
 * Name your new project
 * Click Create repository
 * When done, clone the new repo and run `sh name_project.sh`
 * The script will ask for a slug & full name for the new project and configure the boilerplate files with the project-specific names.
 