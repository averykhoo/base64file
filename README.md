# Base64File

* like gzip.GzipFile, but writes out your binary data as base64 text
  * and obviously the inverse, it reads base64 text files as binary data
* supports most modes
    * the standard `wb`, `rb`, `ab`, `xb`, with optional `+` for concurrent reading/writing
    * the `b` is optional to specify

## Usage

```python
from base64file import Base64File

# open a new/existing file
with Base64File('some-file.txt', 'w+') as b:
    b.write(b'\0\1\2\3\4')
    b.seek(0)
    b.write(b'\n')
    print(b.read(2))  # prints b'\1\2'

# wrap an existing open file
with open('some-file.txt', 'w+') as f:
    with Base64File(file_obj=f) as b:
        b.write(b'\0\1\2\3\4')
        b.seek(0)
        b.write(b'\n')
        print(b.read(2))  # prints b'\1\2'

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
