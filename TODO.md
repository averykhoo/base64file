# TODO

* support `readline()`
* support reading & writing of line wraps into output file
* more comprehensive tests

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
