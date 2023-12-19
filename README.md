# Octopus Workflows

## Installation

### Virtual Env

* Create a venv either manually, or with Pycharm
* Specify the location of this `venv` in the `Makefile`
  * Default is assumed to be `venv` w.r.t. the project root 

Activating venv:
```shell
source venv/bin/activate
```

Exiting a venv:
```shell
deactivate
```

* Install the project for 
  * Production: `make install`
  * Development: `make install-dev`

All requirements will be handled by make and pyproject.toml.

### Formatting and Linting

Check formatting and Linting:

```shell
make check-format
```

Apply formatting and Linting:

```shell
make format
```

### Run Tests

In the main environment, run:

```shell
pytest
```

For all supported environments:

```shell
tox
```

If a specific toc venv fails, one can switch to it:

```shell
# Change to python 3.9 venv
source .tox/py39/bin/activate
```

## Using the Workflows

**Add me**

## Issues

### Parsing

* Substitution of variables - issues with the regex and substitute - need to resolve
* Parsing mathematical expressions - have to specify
* Parsing the various rules for blocks - not fulyl handled
* Clearly the only way to effectively parse is to wrap the oct parser

### Adding File Dependencies to the Workflow

I think the cleanest way to do this is with file rules:
* Attribute a file dependency to all calculations
* Attribute a file dependency only to calculations that match a rule
