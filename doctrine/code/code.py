# -*- coding: UTF-8 -*-
import collections
import io

from contextlib import contextmanager


class Code(collections.MutableSequence):
    """A lazy interface for a file with code in it

    A ``Code`` object takes a file-like object (that should be opened read
    only) and provides an access to that file like if it is a list of lines.
    It's much like doing ``file.readlines()`` on a file, except that the
    access is lazy, so the file will only be read when you are accessing it.

    Usually you don't create the ``Code`` object directly, but you use the
    ``CodeContext`` context manager, see below.

    In addition the the MutableSequnce interface (ie all the method a list has)
    ``Code`` also has the special methods ``delete_characters``, ``split_row``
    and ``merge_rows``.
    """

    def __init__(self, file, read_ahead=50, newline='\n'):
        self.file = file
        self.lines = []
        self.tokens = []  # Cache for widgets
        self.read_ahead = read_ahead
        self.newline = newline

    def __setitem__(self, index, value):
        self.lines[index] = value
        self.tokens[index] = None

    def __delitem__(self, index):
        del self.lines[index]
        del self.tokens[index]

    def __getitem__(self, index):
        if index < 0:
            # We must now read in the whole file:
            while True:
                line = self.file.readline()
                if not line:
                    break
                self.lines.append(line)
                self.tokens.append(None)
            self._check_eof()

        while index >= len(self.lines):
            line = self.file.readline()
            if not line:
                self._check_eof()
                break
            self.lines.append(line)
            self.tokens.append(None)

        return self.lines[index]

    def __iter__(self):
        return iter(self.lines)

    def __len__(self):
        # Read in whole file:
        self[-1]
        return len(self.lines)

    def _check_eof(self):
        # When reaching the end of file, check if the last line ends in
        # a line feed. In that case, add an empty "dummy" line.
        try:
            last = self.lines[-1]
            if last and last[-1] in (u'\r', u'\n'):
                self.lines.append(u'')
                self.tokens.append(None)
        except IndexError:
            # An empty file!
            self.lines.append(u'')
            self.tokens.append(None)

    def insert(self, index, value):
        """Insert a line before index"""
        # First we have to make sure that the line where we want to
        # insert a line exists:
        self[index]
        # Make sure the line has a line ending
        if value and not value[-1] in ('\n', '\r'):
            value += self.newline
        # Now we can insert:
        self.lines.insert(index, value)
        self.tokens.insert(index, None)

    def append(self, value):
        """Append a line to the end of the sequence"""
        # Make sure the previous line has a line ending:
        if self[-1] and not self[-1][-1] in ('\n', '\r'):
            self[-1] = self[-1] + self.newline
        self.lines.append(value)
        self.tokens.append(None)

    def clear(self):
        """Empty the file"""
        self.lines = []
        self.tokens = []
        self.file.seek(0, 2)

    def extend(self, values):
        """Extend the file by appending lines"""
        if not self[-1][-1] in ('\n', '\r'):
            self[-1] = self[-1] + self.newline
        self.lines.extend(values)
        self.tokens.extend([None for x in values])

    def delete_characters(self, fromrow, fromcol, torow, tocol):
        """Remove all characters between two positions.
        Used for example when cutting text.
        """
        start = self[fromrow][:fromcol]
        end = self[torow][tocol:]
        for row in range(torow, fromrow, -1):
            del self[row]
        self[fromrow] = start + end
        # XXX For cutting it would be useful if it returned what was deleted.

    def split_row(self, row, col, newline):
        """Inserts a newline in the middle of a row.
        Used when pressing enter.
        """
        nextline = self[row][col:]
        try:
            self.insert(row + 1, nextline)
        except IndexError:
            # row is the last line:
            self.append(nextline)

        self[row] = self[row][:col] + newline

    def merge_rows(self, first, last):
        """Merges a set of rows.
        Used for deleting a newline or readjusting lines.
        """
        merged = ''.join(line.rstrip(u'\r\n') for line in self[first:last])
        self[last] = merged + self[last]
        del self[first:last]


class CodeContext(object):
    """A context manager for the infile"""

    def __init__(self, filename, filetype):
        self.filename = filename
        self.filetype = filetype

    @contextmanager
    def open(self):
        with io.open(self.filename, encoding='UTF8') as f:
            self.code = Code(f)
            yield self.code

    def save(self):
        # Load to end:
        self.code[-1]
        with io.open(self.filename, 'wt', encoding='UTF8') as f:
            f.writelines(self.code)
