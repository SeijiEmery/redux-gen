import os
import re

#
# file utils
#


def read_file(path):
    with open(path, 'r') as f:
        return path, f.read()


def write_file(path, contents):
    base_path = os.path.split(path)[0]
    if base_path and not os.path.exists(base_path):
        os.makedirs(base_path)
    with open(path, 'w') as f:
        f.write(contents)


#
# parser
#


def parse_model(file_path, contents):
    return {}


def generate_files(data, path, lang=None):
    pass


if __name__ == '__main__':
    generate_files(parse_model(*read_file('test/samples/todo.rxm')),
                   lang='typescript', path='test/output/todo/')
