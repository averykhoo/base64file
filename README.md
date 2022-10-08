# Base64File

* like gzip.GzipFile, but writes out base64 text
* supports concurrent reading and writing

## Usage

```python
from base64file import Base64File

with open('some-file.txt', 'w') as f:
    b = Base64File(file_obj=f)
    b.write(b'\0\1\2\3\4')
    b.seek(0)
    b.write(b'\n')
    print(b.read(2))  # prints b'\1\2'
    b.close()
```
