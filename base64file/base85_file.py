import base64
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

    def _b64encode(self, x):
        out = base64.b85encode(x)
        assert -len(x) % self._3 == -len(out) % self._4
        return out

    def _b64decode(self, x):
        out = base64.b85decode(x)
        assert -len(x) % self._4 == -len(out) % self._3
        return out

    def __init__(self,
                 file_name: Optional[str] = None,
                 mode: Optional[str] = None,
                 file_obj: Optional[Union[TextIO, BinaryIO]] = None,
                 ):
        # we need at least one of these
        super().__init__(file_name, mode, file_obj)

    def readline(self, size=-1):
        raise NotImplementedError


class Ascii85File(Base85File):

    def _b64encode(self, x):
        out = base64.a85encode(x)
        assert -len(x) % self._3 == -len(out) % self._4, (x, out,len(x) % self._3, len(out) % self._4)
        return out

    def _b64decode(self, x):
        out = base64.a85decode(x)
        assert -len(x) % self._4 == -len(out) % self._3
        return out

    def __init__(self,
                 file_name: Optional[str] = None,
                 mode: Optional[str] = None,
                 file_obj: Optional[Union[TextIO, BinaryIO]] = None,
                 ):
        # we need at least one of these
        super().__init__(file_name, mode, file_obj)

    def readline(self, size=-1):
        raise NotImplementedError

