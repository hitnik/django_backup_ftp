import tarfile
import os
import re


def archive_file(path):
    head, tail = os.path.split(path)
    output_filename = re.sub(r'.\w+$', '.tar.gz', tail)
    tar = tarfile.TarFile.gzopen(os.path.join(head, output_filename), mode='w', compresslevel=5)
    tar.add(path, arcname=os.path.basename(path))
    tar.close()
    return os.path.join(head, output_filename)


def extract_file(path):
    head, tail = os.path.split(path)
    tf = tarfile.open(path)
    out = re.sub(r'tar.gz', 'json', path)
    tf.extractall(path=head)
    tf.close()
    return out

if __name__ == '__main__':
    pass
