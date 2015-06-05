# -*- coding: UTF-8 -*-
import collections
import io

from contextlib import contextmanager


# I'm not using abc's, because I want to be able for plugins to implement the
# API only partially.

class Analyzer(object):
    def __init__(self, code):
        self.code = code

    def find_block(self, start_row, max_block):
        raise NotImplementedError

# Although Code is mutable, and a sequence, but does not implement all methods
# of MutableSequence or Sequence. It only implements all methods from
# Sized and Iterable.

class Code(collections.Sized, collections.Iterable):
    """A lazy list interface for a file with code in it."""

    def __init__(self, file, read_ahead=50, newline='\n'):
        self.file = file
        self.lines = []
        self.tokens = [] # Cache for widgets
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
        'S.insert(index, value) -- insert value before index'
        # First we have to make sure that the line where we want to
        # insert a line exists:
        self[index]
        # Now we can insert:
        self.lines.insert(index, value)
        self.tokens.insert(index, None)

    def append(self, value):
        'S.append(value) -- append value to the end of the sequence'
        if self[-1] and not self[-1][-1] in ('\n', '\r'):
            self[-1] = self[-1] + self.newline
        self.lines.append(value)
        self.tokens.append(None)

    def clear(self):
        'S.clear() -> None -- remove all items from S'
        self.lines = []
        self.tokens = []
        self.file.seek(0, 2)

    def extend(self, values):
        'S.extend(iterable) -- extend sequence by appending elements from the iterable'
        if not self[-1][-1] in ('\n', '\r'):
            self[-1] = self[-1] + self.newline
        self.lines.extend(values)
        self.tokens.extend([None for x in values])

    def delete_characters(self, fromrow, fromcol, torow, tocol):
        start = self[fromrow][:fromcol]
        end = self[torow][tocol:]
        for row in range(torow, fromrow, -1):
            del self[row]
        self[fromrow] = start + end

    def split_row(self, row, col, newline):
        nextline = self[row][col:]
        try:
            self.insert(row + 1, nextline)
        except IndexError:
            # row is the last line:
            self.append(nextline)

        self[row] = self[row][:col] + newline

    def merge_rows(self, first, last):
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
