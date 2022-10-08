# TODO

* support with syntax
* support base85, etc
* support line wraps
* remove test from the library

## Publishing (notes for myself)

* init
    * `pip install flit`
    * `flit init`
    * make sure `nmd/__init__.py` contains a docstring and version
* publish / update
    * increment `__version__` in `nmd/__init__.py`
    * `flit publish`