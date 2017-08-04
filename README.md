DMiner
======

## Requirements
### Databases
Because `dminer` has been designed to allow interfaces for any backend database, we highly encourage you to read the official documentation for your backend of choice. However, we explicitly support `elasticsearch`, as this is the easiest route to gaining a feature-full experience with `dminer`. Documentation on how to set up `elasticsearch` and its supporting modules for use with `dminer` will soon be added to a wiki.

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

* [Virtualenv](https://pypi.python.org/pypi/virtualenv)
* [Virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper)


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
For further `pdoc` options, you can run `pdoc --help`, or view the repository and documentation.

### Usage
For the `dminer` CLI usage, you can perform:

```sh
dminer --help
```
and options will be displayed. You can also pass `--help` within argument subgroups for group-specific arguments. For example:
```sh
dminer scrape --help
```
### Example
For an example on how to use CLI to scrape:
```sh
dminer scrape <asset> -u <username> -p <password> -k <DBC username> -s <DBC password>
```


### Module and Pipeline Design
For module and pipeline design documentation, there are sections in the wiki dedicated to these topics. There is also a white-paper with sections discussing design choices and implementation on a top-level.

* [Module Design]()
* [Pipeline Design]()
* [White-paper](https://github.com/infosecanon/dminer/blob/master/IEEE_CNS_Dminer.pdf)

### Troubleshooting
Problem: Geckodriver isn't installed:

Reference [1]( https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu)

Fix:
```sh
$ wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz
$ tar -xvzf geckodriver-v0.18.0-linux64.tar.gz
$ chmod +x geckodriver
$ sudo mv geckodriver /usr/local/bin
```

Problem:  Error: selenium.common.exceptions.WebDriverException: Message: Unable to find a matching set of capabilities

Reference [1](https://github.com/SeleniumHQ/selenium/issues/3890) [2](https://github.com/mozilla/geckodriver/releases)

Fix:
Please update to Selenium v3.4, geckodriver > v0.16.0 (see above), Firefox v54.0

```sh
$ sudo apt-get update
$ sudo apt-get install firefox
```

## Maintainers

### Primaries
* [Andrew](https://github.com/m0nik3r)
* [Bobby](https://github.com/btonic)
* [Heather](https://github.com/infosecanon)
