DMiner
======

## Requirements
### Databases
Because `dminer` has been designed to allow interfaces for any backend database, we highly encourage you to read the official documentation for your backend of choice. However, we explicitly support `elasticsearch`, as this is the easiest route to gaining a feature-full experience with `dminer`. Documentation on how to set up `elasticsearch` and it's supporting modules for use with `dminer` have therefore been added to the [wiki]().

It is notable however, that a database is only required for ingestion purposes. Due to the design of the pipeline, it is possible to perform scrape-only operations and regressively ingest these scrapes at later times.

### System Dependencies
Due to the use of the `geckodriver` to control Firefox through Selenium, you must have the `geckodriver` added to the system path and loaded in your current session. Therefore, you must download, configure, and install the `geckodriver` for your particular operating system.







## Installation

### System Dependencies (globally required)
In order for the module to work in either development or production mode, there are several system dependencies required. First of all, due to the use of

### Development module
To install `dminer` in a development mode so that changes can be made to source, you can install it as follows:
```sh
git clone <url>
cd dminer
pip install -r dev-requirements.txt
python setup.py develop
```
It is suggested that you have a working install of `virtualenv` and `virtualenvwrapper` to prevent possible collisions with system dependencies. If you have `virtualenvwrapper` installed, you can run `mkvirtualenv dminer` before running the above installation commands in order to create the environment, and use the `workon dminer` and `deactivate` commands to interact with your virtual environment as needed. Further documentation on `virtualenv` and `virtualenvwrapper` can be found as follows:

* [Virtualenv]()
* [Virtualenvwrapper]()


### Production module
To install `dminer` in a production environment, you can run:
```sh
git clone <url>
cd dminer
pip install -r requirements.txt
python setup.py install
```
Similarly to the development module install, this can also be done within a `virtualenv`. It is suggested that you do so, as to prevent possible system dependency collisions.






## Documentation

### Code
To provide documentation for `dminer`, we use the `pdoc` module to extract documentation from module and class docstrings. To view the documentation in an easy to use fashion, you can run:
```sh
pdoc --http
```
For further `pdoc` options, you can run `pdoc --help`, or view the [repository]() and [documentation]().

### Usage
For the `dminer` CLI usage, you can perform:

```sh
dminer --help
```
and options will be displayed. You can also pass `--help` within argument subgroups for group-specific arguments. For example:
```sh
dminer scrape --help
```

### Module and Pipeline Design
For module and pipeline design documentation, there are sections in the wiki dedicated to these topics. There is also a white-paper with sections discussing design choices and implementation on a top-level.

* [Module Design]()
* [Pipeline Design]()
* [White-paper]()


## Maintainers

### Primaries
* [Andrew]()
* [Bobby]()
* [Heather]()

### Community
* [Get Involved]()
