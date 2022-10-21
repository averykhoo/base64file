import builtins
import io
import secrets
import warnings
from typing import BinaryIO
from typing import Optional
from typing import TextIO
from typing import Union

try:
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers.algorithms import ChaCha20
except ImportError:
    Cipher = ChaCha20 = None


class ChaCha20File(io.BufferedIOBase, io.BytesIO):

    def __init__(self,
                 filename: Optional[str] = None,
                 mode: Optional[str] = None,
                 *,
                 secret_key: bytes = b'',  # length 32
                 file_obj: Optional[Union[TextIO, BinaryIO]] = None,
                 ):
        """
        At least one of file_obj and filename must be given a non-trivial value.
        When file_obj is not None, the filename argument is ignored.

        The mode argument can be any of the standard file modes.
        It defaults to the mode of file_obj if discernible; otherwise, the default is 'rb'.
        A mode of 'r', 'w', 'a', or 'x' is equivalent to one of 'rb', 'wb', 'ab', or 'xb'.
        """

        # STEP 1: sanity checks

        if Cipher is None or ChaCha20 is None:
            raise ImportError("the cryptography package doesn't seem to be available")

        # for chacha20 to work
        assert isinstance(secret_key, bytes) and len(secret_key) == 32

        # we need at least one of these to be valid
        if isinstance(filename, str):
            filename = filename.strip() or None
        if file_obj is None and filename is None:
            raise ValueError('either filename or file_obj must be specified')

        # STEP 2: figure out file mode
        self.mode: str = ''

        # try to read it (and convert it) from the file, if one was provided
        if file_obj is not None:
            # convert text mode to binary mode
            file_mode = getattr(file_obj, 'mode', '')
            if file_mode:
                self.mode = 'rb' if 'r' in file_mode else 'wb'

        # couldn't read from file_obj, try to use provided mode instead
        if mode and not self.mode:
            if not set(mode).issubset({'r', 'w', 'x', 'b'}):
                raise ValueError(mode)
            self.mode = 'rb' if 'r' in mode else 'wb'

        # mode not provided, so we'll just assume it's read-only
        if not self.mode:
            self.mode = 'rb'

        # sanity check
        assert self.mode in {'rb', 'wb'}

        # STEP 3: open file if needed

        # file object provided
        if file_obj is not None:

            # don't need the file name, give a warning that the provided name will be ignored
            if filename and filename != getattr(file_obj, 'name', None):
                warnings.warn(f'specified filename "{filename}" will be ignored, and file_obj will be used as-is')

            # wrap in a text io wrapper if needed
            file_mode = getattr(file_obj, 'mode', '')
            if isinstance(file_obj, (BinaryIO, io.BytesIO, io.BufferedIOBase, io.RawIOBase)) or 'b' in file_mode:
                self._opened_file_obj = None
            elif isinstance(file_obj, (TextIO, io.StringIO, io.TextIOBase)) or 't' in file_mode:
                raise ValueError(f'file_obj in text mode ({file_mode})')
            else:
                raise TypeError(f'unexpected file_obj type, got {type(file_obj)}')

        # file object has to be created from filename and mode
        else:
            file_obj = self._opened_file_obj = builtins.open(filename, self.mode)

        # keep track of file object
        self.file_obj = file_obj

        # STEP 4: cipher stuff

        # get nonce
        if self.mode == 'rb':
            nonce = self.file_obj.read(16)
        elif self.mode == 'wb':
            nonce = secrets.token_bytes(16)
            self.file_obj.write(nonce)
        else:
            raise RuntimeError

        # init the algorithm
        algorithm = ChaCha20(secret_key, nonce)
        cipher = Cipher(algorithm, mode=None)
        self._encryptor = cipher.encryptor() if self.mode == 'wb' else None
        self._decryptor = cipher.decryptor() if self.mode == 'rb' else None
        self._cursor = 0

    def __repr__(self):
        return f'<{self.__class__.__name__} {repr(self.file_obj)[1:-1]} {hex(id(self))}>'

    @property
    def tell(self):
        return self._cursor

    @property
    def closed(self):
        return self.file_obj is None or self.file_obj.closed

    def readable(self):
        return self.file_obj and self.file_obj.readable() and self.mode == 'rb'

    def writable(self):
        return self.file_obj and self.file_obj.writable() and self.mode == 'wb'

    # noinspection PyMethodMayBeStatic
    def seekable(self):
        return False

    def _ensure_not_closed(self):
        if self.file_obj is None:
            raise ValueError(f'I/O operation on closed {self.__class__.__name__} object')
        if self.file_obj.closed:
            raise ValueError('I/O operation on closed file')

    def _ensure_readable(self):
        if not self.readable():
            raise io.UnsupportedOperation('File not open for reading')

    def _ensure_writable(self):
        if not self.writable():
            raise io.UnsupportedOperation('File not open for writing')

    def write(self, data: Union[bytes, bytearray]) -> int:
        self._ensure_not_closed()
        self._ensure_writable()
        self.file_obj.write(self._encryptor.update(data))
        self._cursor += len(data)
        return len(data)

    def read(self, size=-1) -> bytes:
        self._ensure_not_closed()
        self._ensure_readable()  # cannot read if writing

        # no-op
        if size == 0:
            return b''

        # read data
        out = self._decryptor.update(self.file_obj.read(size))
        self._cursor += len(out)
        return out

    def close(self):
        # ensure data is written
        self.flush()

        # remove the file obj immediately
        file_obj, self.file_obj = self.file_obj, None
        if file_obj is None:
            return

        # close my_file_obj if we opened it via filename in __init__
        if self._opened_file_obj is not None:
            self._opened_file_obj.close()
            self._opened_file_obj = None

    def flush(self):
        self._ensure_not_closed()
        self.file_obj.flush()

    # noinspection SpellCheckingInspection
    def fileno(self):
        return self.file_obj.fileno()

    def seek(self, offset, whence=io.SEEK_SET):
        raise NotImplementedError

    def readline(self, size=-1):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':
    from pathlib import Path

    Path('../tmp').mkdir(exist_ok=True, parents=True)

    with ChaCha20File('../tmp/test.bin', 'wb', secret_key=b'\0' * 32) as f:
        f.write(b'asdf')
    with open('../tmp/test.bin', 'rb') as f1:
        with ChaCha20File(file_obj=f1, secret_key=b'\0' * 32) as f2:
            print(f2.read())
