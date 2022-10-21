# Base64File

An IO wrapper that but reads/writes binary data as base64 text, supporting concurrent reading and writing. Similar
to [`GzipFile`](https://docs.python.org/3/library/gzip.html#gzip.GzipFile), it simulates most of the methods of a
standard file object (with the exception of `readline`).

## Usage

### base64file.open()

* Similar to `gzip.open()` or `io.open()`

```python
import base64file

# to write text
with base64file.open('some-file.txt', 'rt', encoding='utf8') as f:
    f.write('1234567890')

# to write binary
with base64file.open('some-file.txt', 'rb') as f:
    f.write(b'\1\2\3\4\5')
```

### base64file.Base64File

* When opening a Base64File without specifying an underlying file, a filename must be provided, and the usual binary
  modes are supported: `r`, `rb`,  `w`,  `wb`, `a`, `ab`, `x`, and `xb` (optional `+` to enable concurrent
  reading/writing, e.g. `wb+`).
* When opening a Base64File with a specified underlying file, the mode is inherited from the specified file (replacing
  text-mode with binary-mode). If a binary-mode file is provided, it is automatically wrapped with
  a [`TextIOWrapper`](https://docs.python.org/3/library/io.html#io.TextIOWrapper).

```python
from base64file import Base64File

# open a new/existing file for concurrent reading and writing
with Base64File('some-file.txt', 'w+') as b:
    b.write(b'\0\1\2\3\4')
    b.seek(0)
    b.write(b'\n')
    print(b.read(2))  # prints b'\1\2'

# wrap an existing file (in this example, open for reading)
with open('some-file.txt', 'r') as f:
    with Base64File(file_obj=f) as b:
        print(b.read(2))  # prints b'\n\1'
        print(b.read())  # prints b'\2\3\4'

# if you need to keep the file open, remember to close it
f = open('some-file.txt', 'w+')
b = Base64File(file_obj=f)
b.write(b'\0\1\2\3\4')
b.seek(0)
b.write(b'\n')
print(b.read(2))  # prints b'\1\2'
b.close()  # this is necessary, otherwise the final 1-2 bytes may not be written
f.close()
```
