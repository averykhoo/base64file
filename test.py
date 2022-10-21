from pathlib import Path

from base64file import Ascii85File
from base64file import Base64File
from base64file import Base85File

if __name__ == '__main__':
    Path('tmp').mkdir(exist_ok=True, parents=True)
    for i in range(7, 20):
        for klass in [Ascii85File, Base64File, Base85File]:
            with open(f'tmp/{klass.__name__.lower()}.txt', 'wt+') as f:
                print(f.write('\1\2'))
                print(f.write('\3'))
                bf = klass(file_obj=f)
                bf.write(b'01234567890123456789'[:i])
                bf.seek(1)
                print(bf.read(1))
                bf.write(b'qwert')
                bf.close()
            with open(f'tmp/{klass.__name__.lower()}.txt', 'rb') as f:
                print(type(f))
                f.seek(3)
                bf = klass(file_obj=f)
                print(bf.read() == b'01qwert7890123456789'[:i])
                bf.close()
