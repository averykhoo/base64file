# Base64File

* like gzip.GzipFile, but writes out base64 text
* supports concurrent reading and writing

## Usage

...

## Publishing (notes for myself)

* init
  * `pip install flit`
  * `flit init`
  * make sure `nmd/__init__.py` contains a docstring and version
* publish / update
  * increment `__version__` in `nmd/__init__.py`
  * `flit publish`