from tempfile import mkstemp
from shutil import move, copyfile
from os import remove, close

def replace(file_path, pattern, subst, backup=True):
    """Search and replace on line(s) and write result back to file"""
    result = False
    # create temp file
    fh, abs_path = mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if pattern in line:
                    new_file.write(line.replace(pattern, subst))
                    result = True
                else:
                    new_file.write(line)
    close(fh)
    if result:
        # create copy
        if backup:
            bak = '%s.BAK' % file_path
            remove(bak)
            copyfile(file_path, bak)
        else:
            # remove original file
            remove(file_path)
        # move new file
        move(abs_path, file_path)
    else:
        remove(abs_path)
    return result

"""
# TEST IN INTERPRETER
from utils import replace
with open('test.txt', 'w') as new_file:
    new_file.write('hello')

assert replace('test.txt', 'hello', 'hello_you') is True
assert replace('test.txt', 'helo', 'hello_you') is False
"""

