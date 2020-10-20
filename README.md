# SimpleNight API

## Building

### Prerequisites
- python3.7 (preferred with [pyenv](https://github.com/pyenv/pyenv))

### Getting Started

#### Virtual Environment and Python Dependencies
After pre-requisites are satisfied, from the root of the project, run:
```bash
python3.7 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
pre-commit install
```

This will create a virtual environment, install all production and development dependencies, and `pre-commit`.  We currently have `pre-commit` configured to run the `black` code formatter and `flake` linter on each commit.

#### Postgres Database Container

We run a Postgres container even for tests.  Postgres is run within a Docker container, and started using Docker-compose.  Please ensure you have both Docker and `docker-compose` installed.  
To build our development Postgres image, and start a container, execute the following commands from the project root:

```bash
docker build -t simplenight-postgres:13 dev/
docker-compose -f dev/docker-compose.yml up
```

#### Testing

If you're running on OSX, there are several helper scripts within `bin/`.  Tests can be executed by running `./bin/test-local`.

For windows, run: 

`python manage.py test --settings api.environments.local api.tests.unit api.tests.integration`

#### PyCharm

If you're running PyCharm Professional Edition, the Django test runner is supported directly.  Change your settings file under Languages & Frameworks -> Django to point to `api/environments/local.py`, and you'll be able to run tests directly within Django.