# IDVA Token Microservice
The IDVA Token microservice is a Python Flask
application that exposes an API for generating and validating simple tokens.

Tokens are at default valid for 7 days and have 1 use. Time and uses can be adjusted when registering a token.

## Building Locally

### Pre-requisites
Make sure you have the following installed if you intend to build the project locally.
- [Python 3.11](https://www.python.org/)
- [CloudFoundry CLI](https://docs.cloudfoundry.org/cf-cli/)

### Development Setup
To set up your environment, run the following commands (or the equivalent
commands if not using a bash-like terminal):
```shell
# Clone the project
git clone https://github.com/GSA-TTS/identity-idva-token-service
cd identity-idva-token-service

# Set up Python virtual environment
python3.11 -m venv .venv
source .venv/bin/activate
# .venv\Scripts\Activate.ps1 on Windows

# Install dependencies and pre-commit hooks
python -m pip install -r requirements-dev.txt
pre-commit install

```
Install [PostgreSQL](https://www.postgresql.org/).

Set up a local database:
```shell
psql
create database idva_token;
# \q
```

To set a custom secret key, use the following environment variable: `SECRET_KEYS`.

The project can be ran locally with:
```shell
python manage.py run
```

### Running the application
After completing [development setup](#development-setup) application locally with:
```shell
python -m pytest
python manage.py test
```

### API Endpoints

#### Authorization
```
Headers

X-API-Key: <api-key>
```

#### Token Registering
Create a new token.

`POST /auth`

```
Request body:
{
  "seconds": int, //OPTIONAL
  "uses": int //OPTIONAL
}
```

#### Token Validating
Validates a token without changing its properties.

`GET /auth/<token>`


#### Token Invoking
Invokes a token, decrementing its uses by 1.

`POST /auth/<token>/decrement`


#### Token Exhausting
Exhausts a token rendering it useless.

`DELETE /auth/<token>`


#### Survey Response Export
Export Qualtrics Survey response on a public endpoint.

`POST /export/survey-response`

```
Request body:
{
  "surveyId": str
  "responseId": str
  "participant": {
    "first": str
    "last": str
    "email": str
    "time": str
  }
}
```

### Deploying to Cloud.gov during development
All deployments require having the correct Cloud.gov credentials in place. If
you haven't already, visit [Cloud.gov](https://cloud.gov) and set up your
account and CLI.

*manifest.yml* file contains the deployment configuration for cloud.gov, and expects
a vars.yaml file that includes runtime variables referenced. For info, see
[cloud foundry manifest files reference](https://docs.cloudfoundry.org/devguide/deploy-apps/manifest-attributes.html)

Running the following `cf` command will deploy the application to cloud.gov
```shell
cf push --vars-file vars.yaml \
  --var ENVIRONMENT=<env>
```

## Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in
[CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright
and related rights in the work worldwide are waived through the
[CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication.
By submitting a pull request, you are agreeing to comply with this waiver of
copyright interest.