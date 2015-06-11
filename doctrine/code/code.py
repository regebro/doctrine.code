# -*- coding: UTF-8 -*-
import collections
import io

from contextlib import contextmanager

NEWLINES = u'\n\r'


class Code(collections.MutableSequence):
    """A ``Code`` object takes a file-like object (that should be opened read
    only) and provides an access to that file like if it is a list of lines.
    It's much like doing ``file.readlines()`` on a file, except that the
    access is lazy, so the file will only be read when you are accessing it.

    Usually you don't create the ``Code`` object directly, but you use the
    ``CodeContext`` context manager, see below.

    In addition the the MutableSequence interface (ie all the method a list has)
    ``Code`` also has the special methods ``delete_text``, ``insert_text``,
    ``split_row`` and ``merge_rows``.
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
            if last and last[-1] in NEWLINES:
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
        if value and not value[-1] in NEWLINES:
            value += self.newline
        # Now we can insert:
        self.lines.insert(index, value)
        self.tokens.insert(index, None)

    def append(self, value):
        """Append a line to the end of the sequence"""
        # Make sure the previous line has a line ending:
        if self[-1] and not self[-1][-1] in NEWLINES:
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
        if not self[-1][-1] in NEWLINES:
            self[-1] = self[-1] + self.newline
        self.lines.extend(values)
        self.tokens.extend([None for x in values])

    def delete_text(self, fromrow, fromcol, torow, tocol):
        """Remove all text between two positions and return the deleted text.
        Used for example when cutting text.
        """
        start = self[fromrow][:fromcol]
        end = self[torow][tocol:]

        # Save what is deleted, so it can be returned.
        if fromrow != torow:
            deleted = [self[torow][:tocol]]
            rest = self[fromrow][fromcol:]
        else:
            deleted = []
            rest = self[fromrow][fromcol:tocol]

        for row in range(torow, fromrow, -1):
            if row != torow:
                deleted.append(self[row])
            del self[row]
        deleted.append(rest)

        self[fromrow] = start + end
        return ''.join(reversed(deleted))

    def insert_text(self, row, col, text):
        """Inserts a multiline text at a certain row and column.
        Used for example when pasting text."""
        # First split the text into lines:
        if row >= len(self):
            raise ValueError("Can not insert text after end of file")
        curline = self[row]
        if col > len(curline.rstrip(NEWLINES)):
            raise ValueError("Can not insert text after end of line")

        lines = []
        line = ''
        newline = False
        for c in text:
            if newline:
                if c in NEWLINES and c != newline:
                    # Two char newline: Add c to the new line
                    line += c
                    c = ''

                lines.append(line)
                line = c
                newline = False
                continue

            line += c
            if c in NEWLINES:
                newline = c

        if line:
            lines.append(line)

        # Now insert this text.
        if len(lines) == 1:
            self[row] = curline[:col] + lines[0] + curline[col:]
            return

        # Multiple lines. Split the current row with no newline:
        self.split_row(row, col, '')
        # Add the first line to the current line:
        self[row] += lines[0]
        del lines[0]

        # If the last line doesn't end with a newline, it should be
        # prepended to the rest of the current line, now newly split:
        if lines[-1][-1] not in NEWLINES:
            self[row + 1] = lines[-1] + self[row + 1]
            del lines[-1]

        # Now insert remaining lines:
        for line in reversed(lines):
            self.insert(row + 1, line)

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
        merged = ''.join(line.rstrip(NEWLINES) for line in self[first:last])
        self[last] = merged + self[last]
        del self[first:last]


class CodeContext(object):
    """A context manager that handles the opening of and saving to the file used
    by a Code instance.
    """

    def __init__(self, filename, filetype):
        self.filename = filename
        self.filetype = filetype

    @contextmanager
    def open(self):
        """Returns a Code instance wrapping the file"""
        with io.open(self.filename, encoding='UTF8') as f:
            self.code = Code(f)
            yield self.code

    def save(self):
        """Saves the content of the code object to the file"""
        # Load to end:
        self.code[-1]
        with io.open(self.filename, 'wt', encoding='UTF8') as f:
            f.writelines(self.code)
