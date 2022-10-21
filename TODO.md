# TODO

* support `readline()`
* support line wraps
* more comprehensive tests
* add base85 and ascii85 to readme

## Publishing (notes for myself)

* init
    * `pip install flit`
    * `flit init`
    * make sure `nmd/__init__.py` contains a docstring and version
* publish / update
    * increment `__version__` in `nmd/__init__.py`
    * `flit publish`
* other
    * maybe store password to .pypirc
    * add home url to pyproject.toml
