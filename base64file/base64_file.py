import base64
import builtins
import io
import warnings
from typing import BinaryIO
from typing import Optional
from typing import TextIO
from typing import Union


class Base64File(io.BufferedIOBase):
    """
    The GzipFile class simulates most of the methods of a file object.

    This class only supports opening files in binary mode.
    If you need to open a compressed file in text mode, use the gzip.open() function.
    """

    # these are constants that need to be changed if you decide to use base85 instead
    _4 = 4  # (encoded size) number of base64 chars per chunk (change to 5)
    _3 = 3  # (decoded size) number of raw bytes per chunk (change to 4)
    _binary = 'binary'  # or 'text'

    @staticmethod
    def _b64encode(x):
        # return base64.b85encode(x)
        return base64.b64encode(x)

    @staticmethod
    def _b64decode(x):
        # return base64.b85decode(x)
        return base64.b64decode(x, validate=True)

    def __init__(self,
                 file_name: Optional[str] = None,
                 mode: Optional[str] = None,
                 file_obj: Optional[Union[TextIO, BinaryIO]] = None,
                 alt_chars: Optional[str] = None,
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
        if file_obj is None and file_name is None:
            raise ValueError('either file_name or file_obj must be specified')

        # file object provided
        if file_obj is not None:
            # don't need the file name
            if file_name is not None and file_name != getattr(file_obj, 'name', None):
                warnings.warn(f'specified file_name "{file_name}" will be ignored, and file_obj will be used as-is')

            # what is the current mode
            self.mode = getattr(file_obj, 'mode', mode)
            if mode is not None and mode != self.mode:
                warnings.warn(f'specified mode "{mode}" will be ignored, and file_obj will be used as-is')

            # wrap in a text io wrapper if needed
            if isinstance(file_obj, (BinaryIO, io.BytesIO, io.BufferedIOBase, io.RawIOBase)):
                file_obj = self._opened_file_obj = io.TextIOWrapper(file_obj, encoding='ascii', newline='')
            elif isinstance(file_obj, (TextIO, io.StringIO, io.TextIOBase)):
                self._opened_file_obj = None
            else:
                raise TypeError(f'unexpected file_obj type, got {type(file_obj)}')

        # file object has to be created from file_name and mode
        else:
            if mode is None:
                mode = 'r'
            if mode and set(mode).issubset({'r', 'w', 'a', 'x', '+', self._binary[0]}):
                if self._binary[0] not in mode:
                    mode += self._binary[0]
                    warnings.warn(f'base64_file only supports {self._binary}, changing mode to {mode}')
            else:
                raise ValueError(f'invalid mode "{mode}"')
            self.mode = mode

            # create file obj
            file_obj = self._opened_file_obj = builtins.open(file_name, mode or 'rb')

        # keep track of file object
        self.file_obj = file_obj

        # allow reading/writing to happen from the middle of a file
        self.file_tell_offset = file_obj.tell()
        self._cursor = 0  # base64 bytes
        self._buffer = bytearray()
        self._buffer_cursor = 0

        # flags
        self._data_not_written_flag = False

        # base64 args
        if alt_chars is not None:
            self._b64encode = lambda x: base64.b64encode(x, altchars=alt_chars)
            self._b64decode = lambda x: base64.b64decode(x, altchars=alt_chars, validate=True)

    def __repr__(self):
        s = repr(self.file_obj)
        return '<base64 ' + s[1:-1] + ' ' + hex(id(self)) + '>'

    @property
    def tell(self):
        return self._cursor

    @property
    def closed(self):
        return self.file_obj is None or self.file_obj.closed

    def readable(self):
        return self.file_obj and self.file_obj.readable()

    def writable(self):
        return self.file_obj and self.file_obj.writable()

    def seekable(self):
        return self.file_obj and self.file_obj.seekable()

    def _ensure_not_closed(self):
        if self.file_obj is None:
            raise ValueError("write() on closed GzipFile object")
        if self.file_obj.closed:
            raise ValueError('I/O operation on closed file')

    def _ensure_readable(self):
        if not self.readable():
            raise io.UnsupportedOperation('File not open for reading')

    def _ensure_writable(self):
        if not self.writable():
            raise io.UnsupportedOperation('File not open for writing')

    def _ensure_seekable(self):
        if not self.seekable():
            raise io.UnsupportedOperation('File does not support seeking')

    def write(self, data: Union[bytes, bytearray]) -> int:
        self._ensure_not_closed()
        self._ensure_writable()

        assert 0 <= self._buffer_cursor <= len(self._buffer) <= self._3 and self._buffer_cursor < self._3

        # check expected file position
        _expected_tell = self.file_tell_offset + self._4 * ((self._cursor - self._buffer_cursor) // self._3)
        if _expected_tell != self.file_obj.tell():  # maybe we read ahead a bit
            self._ensure_seekable()
            self.file_obj.seek(_expected_tell)

        # insert into buffer, possibly only inserting something in the middle
        _tmp, self._buffer = self._buffer, self._buffer[:self._buffer_cursor]
        self._buffer.extend(data)
        if len(_tmp) > len(self._buffer):
            self._buffer.extend(_tmp[len(self._buffer):])
        self._buffer_cursor += len(data)
        self._cursor += len(data)
        _tmp.clear()

        _num_writable_bytes = self._3 * (self._buffer_cursor // self._3)
        self.file_obj.write(self._b64encode(self._buffer[:_num_writable_bytes]).decode('ascii'))

        self._buffer, _tmp = self._buffer[_num_writable_bytes:], self._buffer
        self._buffer_cursor -= _num_writable_bytes
        _tmp.clear()
        self._data_not_written_flag = self._buffer_cursor != 0

        # sanity check
        assert (self._cursor - self._buffer_cursor) % self._3 == 0  # we've written a whole number of chunks
        assert self.file_tell_offset + self._4 * (
                (self._cursor - self._buffer_cursor) // self._3) == self.file_obj.tell()
        assert 0 <= self._buffer_cursor <= len(self._buffer) <= self._3 and self._buffer_cursor < self._3

        return len(data)

    def read(self, size=-1) -> bytes:
        self._ensure_not_closed()
        self._ensure_readable()  # cannot read if writing

        assert 0 <= self._buffer_cursor <= len(self._buffer) <= self._3 and self._buffer_cursor < self._3

        # no-op
        if size == 0:
            return b''

        # check expected file position
        if self._data_not_written_flag:
            self._ensure_seekable()
            _expected_write_tell = self.file_tell_offset + self._4 * ((self._cursor - self._buffer_cursor) // self._3)
            assert _expected_write_tell == self.file_obj.tell()
            assert 0 <= self._buffer_cursor < self._3
            self._ensure_seekable()

            # read one chunk of data, appending to existing unwritten bytes
            if len(self._buffer) < self._3:
                _tmp, self._buffer = self._buffer, bytearray()
                self._buffer.extend(
                    self._b64decode(self.file_obj.read(self._4).encode('ascii')))
                self._buffer[:self._buffer_cursor] = _tmp[:self._buffer_cursor]

            # don't write anything (yet)
            if len(self._buffer) < self._3 or (size > 0 and self._buffer_cursor + size < self._3):
                self.file_obj.seek(_expected_write_tell)  # return file cursor to where we should write from
                if size < 0:
                    size = len(self._buffer)
                out = self._buffer[self._buffer_cursor:self._buffer_cursor + size]
                self._buffer_cursor += len(out)
                self._cursor += len(out)
                assert 0 <= self._buffer_cursor <= len(self._buffer) <= self._3 and self._buffer_cursor < self._3
                return bytes(out)

            # write one chunk of data
            assert len(self._buffer) == self._3
            self.file_obj.seek(_expected_write_tell)
            self.file_obj.write(self._b64encode(self._buffer[:self._3]).decode('ascii'))
            self._data_not_written_flag = False

        # prepare to read data
        assert len(self._buffer) in {0, self._3}
        assert 0 <= self._buffer_cursor <= len(self._buffer) <= self._3 and self._buffer_cursor < self._3
        assert (self._cursor - self._buffer_cursor) % self._3 == 0
        _expected_tell = self.file_tell_offset + self._4 * (self._cursor // self._3)
        if len(self._buffer) > 0:
            _expected_tell += self._4
        assert _expected_tell == self.file_obj.tell(), (_expected_tell, self.file_obj.tell())

        # figure out exactly how much to read
        if size > 0:
            _size_to_read = size - (len(self._buffer) - self._buffer_cursor)
            _file_size_to_read = self._4 * (_size_to_read // self._3)
            if _size_to_read % self._3 > 0:
                _file_size_to_read += self._4
        else:
            _file_size_to_read = -1

        # read data
        _bytes_read = self.file_obj.read(_file_size_to_read).encode('ascii')
        assert len(_bytes_read) % self._4 == 0, (len(_bytes_read), _bytes_read)
        # if _file_size_to_read < 0 or len(_bytes_read) < _file_size_to_read:
        #     _bytes_read += b'===='
        self._buffer.extend(self._b64decode(_bytes_read))

        # how much to return
        if size > 0:
            out = bytes(self._buffer[self._buffer_cursor:self._buffer_cursor + size])
        else:
            out = bytes(self._buffer[self._buffer_cursor:])
        self._buffer_cursor += len(out)
        self._cursor += len(out)

        # clear read buffer
        _tmp, self._buffer = self._buffer, bytearray()
        _num_bytes_to_clear = self._3 * (self._buffer_cursor // self._3)
        self._buffer.extend(_tmp[_num_bytes_to_clear:])
        _tmp.clear()
        self._buffer_cursor -= _num_bytes_to_clear

        assert 0 <= self._buffer_cursor <= len(self._buffer) <= self._3 and self._buffer_cursor < self._3
        return out

    def close(self):
        # ensure data is written
        if self._data_not_written_flag:
            self.read(self._3)

        # remove the file obj immediately
        file_obj, self.file_obj = self.file_obj, None
        if file_obj is None:
            return

        # really make sure
        if self._data_not_written_flag:
            file_obj.write(self._b64encode(self._buffer).decode('ascii'))

        # close my_file_obj if we opened it via file_name in __init__
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
        self._ensure_not_closed()
        self._ensure_seekable()
        self._ensure_readable()

        # ensure data is written
        if self._data_not_written_flag:
            self.read(self._3)

        # write to end of file
        if self._data_not_written_flag:
            self.file_obj.write(self._b64encode(self._buffer).decode('ascii'))

        if whence == io.SEEK_SET:
            if offset < 0:
                raise IOError('unable to seek to negative file size')
            self._cursor = self._3 * (offset // self._3)
            _offset = self._4 * (offset // self._3)

            self.file_obj.seek(_offset + self.file_tell_offset)
            self._buffer.clear()
            self._buffer_cursor = 0

            if offset % self._3:
                self.read(offset % self._3)

        elif whence == io.SEEK_CUR:
            if self._cursor + offset < 0:
                raise IOError(f'unable to seek back that far, current tell is {self._cursor}')
            self.seek(self._cursor + offset)

        elif whence == io.SEEK_END:
            _tmp = self.file_obj.tell()
            self.file_obj.seek(0, io.SEEK_END)
            _len = (self.file_obj.tell() - self.file_tell_offset)
            self.file_obj.seek(self.file_tell_offset + self._4 * (_len // self._4))
            self._cursor = self._3 * (_len // self._4)
            self.read()

        return self._cursor

    def readline(self, size=-1):
        raise NotImplementedError


if __name__ == '__main__':
    with open('tmp.txt', 'wt+') as f:
        print(f.write('\1\2'))
        print(f.write('\3'))
        bf = Base64File(file_obj=f)
        bf.write(b'01234567890123456789')
        bf.seek(1)
        print(bf.read(1))
        bf.write(b'qwert')
        bf.close()
    with open('tmp.txt', 'rb') as f:
        print(type(f))
        f.seek(3)
        bf = Base64File(file_obj=f)
        print(bf.read())
        bf.close()
