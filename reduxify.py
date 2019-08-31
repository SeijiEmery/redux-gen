import os
import re

#
# file utils
#


class LineNumMap:
    def __init__(self, contents):
        self.line_start_indices = [0]
        for i, c in enumerate(contents):
            if c == '\n':
                self.line_start_indices.append(i + 1)
        self.line_start_indices.append(len(contents))

    def __repr__(self):
        return repr(self.line_start_indices)


class FileView:
    def __init__(self, contents, file_name):
        self.contents = contents
        self.file_name = file_name
        self.line_map = LineNumMap(contents)

    def __str__(self):
        return '%s\n%s' % (self.file_name, '\n'.join([
            '%3d: %s' % (i + 1, self.contents[
                self.line_map.line_start_indices[i]:
                self.line_map.line_start_indices[i + 1]
            ].strip('\n'))
            for i in range(len(self.line_map.line_start_indices) - 1)
        ]))


def read_file(path):
    with open(path, 'r') as f:
        return FileView(f.read(), path)


def write_file(path, contents):
    base_path = os.path.split(path)[0]
    if base_path and not os.path.exists(base_path):
        os.makedirs(base_path)
    with open(path, 'w') as f:
        f.write(contents)

#
# regex utils
#


def make_regex(*parts):
    return re.compile(r'\s*'.join(parts))


MODEL_REGEX = make_regex('model', '\\(', r'([^)]*)', '\\)', '{')


#
# parser
#


def parse_model(file_view):
    output = []
    src_start_index = 0

    print(file_view)

    for match in re.finditer(MODEL_REGEX, file_view.contents):
        match_begin, match_end = match.span()
        print(match_begin, match_end)
        print(match)

    return {}


def generate_files(data, path, lang=None):
    pass


if __name__ == '__main__':
    generate_files(parse_model(read_file('test/samples/todo.rxm')),
                   lang='typescript', path='test/output/todo/')
