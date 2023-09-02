# Basic usage

I have used `pipenv`, so it should be enough to set up a new pipenv virtual environment and then run `pipenv install` to download all dependencies.
All the following commands are counting with all dependencies from virtual environment, so one has to run the following command to enter it 
(or pehaps it is sufficient to simply prepend `pipenv run`):

```shell
pipenv shell
```

Prepare local SQLite DB for loca testing using:

```shell
python manage.py migrate
```

After setting up clean DB, one has to create a new super-user to enable access to site admin using the following command and then following up on-screen instructions:

```shell
python manage.py createsuperuser
```

> **TODO:** fixtures

Generate *MO* file (so-called machine object file) to enable basic czech localization (to be seen in site admin) by running:

```shell
python manage.py compilemessages --locale cs
```

Running all unit tests:

```shell
pytest
```

To start the server locally, run:

```shell
python manage.py runserver 8000
```

And then the following URLs shall be available:

- [admin/backoffice (http://www.localhost:8000/site-admin)](http://www.localhost:8000/site-admin)
- [GraphQL endpoint (http://api.localhost:8000/gql)](http://api.localhost:8000/gql)
- [GraphiQL for testing only with enabled debug mode (http://api.localhost:8000/giql)](http://api.localhost:8000/giql)


# Development hints

## Generating GraphQL schema

Running:

```shell
python manage.py graphql_schema --schema apps.api.graphql.schema.schema --out ./assets/schema.graphql
```

should generate GraphQL schema in SDL format within `assets/` directory.

## Localizing

Localization is using basic django mechanism based on gnugettext. 
For localization process are used PO (aka Portable Object) files.
But the server itself requires MO (aka Machine Object) files that are compiled out of PO files.

To extract new messages for localization out of project's source code into PO file:

```shell
python manage.py makemessages --locale cs
```

To compile MO file out of PO file after the localization process:

```shell
python manage.py compilemessages --locale cs
```

## Adding apps

Lets add a brand-new app called `abc`: 

```shell
mkdir apps/abc
python manage.py startapp abc apps.abc
```

Then one correction has to be done manually -- go to `apps/abc/apps.py` and prepad `apps.` to the value of attribute `name` of your `AppConfig`.

## Honorable mentions

- basic site admin for models of apps **carpool** and **reservation**
- custom time-oriented list filters in admin of **reservation** (rent time and/or return time in the given time interval, rent duration in the given range)
- basic czech localization of site admin
- generated GraphQL schema (for cooperation with FE platforms - CLI, web app, mobile apps)
- pytest-based unit tests with checking of exceptions and captured logs 

## What might be next?

- REST API endpoints
- OpenAPI for REST API
- user authentication and authorization
- mocks for 3rd party testing
- integration testing
- "dockerization"
- fixtures for additional features + manual testing and trials
- pre-commit hook running some external tools like
  - **pre-commit** 
  - code formatter (**black**)
  - type-checker (**mypy**) ?!
  - linter (**flake8**, perhaps **ruff**)
  - import sorting (**isort**)
- prepare CI workflows
