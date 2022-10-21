import io
import os

from base64file.base64_file import Base64File


def open(filename, mode="rb", encoding=None, errors=None, newline=None):
    """Open a base64 file in binary or text mode.

    The filename argument should be an actual filename (a str or bytes object).

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" or "ab" for
    binary mode, or "rt", "wt", "xt" or "at" for text mode. The default mode is
    "rb".

    For binary mode, this function is equivalent to the Base64File constructor:
    Base64File(filename, mode). In this case, the encoding, errors
    and newline arguments must not be provided.

    For text mode, a Base64File object is created, and wrapped in an
    io.TextIOWrapper instance with the specified encoding, error handling
    behavior, and line ending(s).

    """
    if "b" in mode:
        if "t" in mode:
            raise ValueError("Invalid mode: %r" % (mode,))
        if encoding is not None:
            raise ValueError("Argument 'encoding' not supported in binary mode")
        if errors is not None:
            raise ValueError("Argument 'errors' not supported in binary mode")
        if newline is not None:
            raise ValueError("Argument 'newline' not supported in binary mode")

    file_mode = mode.replace('t', '')
    if isinstance(filename, (str, bytes, os.PathLike)):
        binary_file = Base64File(filename, file_mode)
    elif hasattr(filename, "read") or hasattr(filename, "write"):
        binary_file = Base64File(file_obj=filename)
    else:
        raise TypeError("filename must be a str or bytes object, or a file")

    if "t" in mode:
        return io.TextIOWrapper(binary_file, encoding, errors, newline, write_through=True)
    else:
        return binary_file
