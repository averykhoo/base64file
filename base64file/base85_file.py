import base64
import builtins
import io
import warnings
from typing import BinaryIO
from typing import Optional
from typing import TextIO
from typing import Union

from base64file import Base64File


class Base85File(Base64File):

    # these are constants that need to be changed if you decide to use base85 instead
    _4 = 5  # (encoded size) number of base64 chars per chunk (change to 5)
    _3 = 4  # (decoded size) number of raw bytes per chunk (change to 4)
    _binary = 'binary'  # or 'text'

    @staticmethod
    def _b64encode(x):
        return base64.b85encode(x)

    @staticmethod
    def _b64decode(x):
        return base64.b85decode(x)

    def __init__(self,
                 file_name: Optional[str] = None,
                 mode: Optional[str] = None,
                 file_obj: Optional[Union[TextIO, BinaryIO]] = None,
                 ):
        """
        At least one of file_obj and file_name must be given a
        non-trivial value.

        The new class instance is based on file_obj, which can be a regular
        file, an io.BytesIO object, or any other object which simulates a file.
        It defaults to None, in which case file_name is opened to provide
        a file object.

        When file_obj is not None, the file_name argument is only used to be
        included in the gzip file header, which may include the original
        file_name of the uncompressed file.  It defaults to the file_name of
        file_obj, if discernible; otherwise, it defaults to the empty string,
        and in this case the original file_name is not included in the header.

        The mode argument can be any of 'r', 'rb', 'a', 'ab', 'w', 'wb', 'x', or
        'xb' depending on whether the file will be read or written.  The default
        is the mode of file_obj if discernible; otherwise, the default is 'rb'.
        A mode of 'r' is equivalent to one of 'rb', and similarly for 'w' and
        'wb', 'a' and 'ab', and 'x' and 'xb'.
        """

        # we need at least one of these
        super().__init__(file_name, mode, file_obj)

    def __repr__(self):
        s = repr(self.file_obj)
        return '<base85 ' + s[1:-1] + ' ' + hex(id(self)) + '>'



if __name__ == '__main__':
    with open('tmp.txt', 'wt+') as f:
        print(f.write('\1\2'))
        print(f.write('\3'))
        bf = Base85File(file_obj=f)
        bf.write(b'01234567890123456789')
        bf.seek(1)
        print(bf.read(1))
        bf.write(b'qwert')
        bf.close()
    with open('tmp.txt', 'rb') as f:
        print(type(f))
        f.seek(3)
        bf = Base85File(file_obj=f)
        print(bf.read())
        bf.close()
