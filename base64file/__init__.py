"""
An IO wrapper that reads/writes binary data as base64 into a text file
"""

from base64file.base64_file import Base64File
from base64file.base85_file import Ascii85File
from base64file.base85_file import Base85File
from base64file.convenience import open

__version__ = '0.0.9'

__all__ = (
    Base64File,
    Base85File,
    Ascii85File,
    open,
)
