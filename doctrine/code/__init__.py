# -*- coding: UTF-8 -*-
import collections


# Although Code is mutable, and a sequence, but does not implement all methods
# of MutableSequence or Sequence. It only implements all methods from
# Sized and Iterable.

class Code(collections.Sized, collections.Iterable):
    """A lazy list interface for a file with code in it."""

    def __init__(self, file, filetype, read_ahead=50, newline='\n'):
        self.file = file
        self.filetype = filetype
        self.lines = []
        self.widgets = [] # Cache for widgets
        self.read_ahead = read_ahead
        self.newline = newline

    def __setitem__(self, index, value):
        self.lines[index] = value
        self.widgets[index] = None

    def __delitem__(self, index):
        del self.lines[index]
        del self.widgets[index]

    def __getitem__(self, index):
        if index < 0:
            # We must now read in the whole file:
            while True:
                line = self.file.readline()
                if not line:
                    break
                self.lines.append(line)
                self.widgets.append(None)

        while index >= len(self):
            line = self.file.readline()
            if not line:
                raise IndexError
            self.lines.append(line)
            self.widgets.append(None)

        return self.lines[index]

    def __iter__(self):
        return iter(self.lines)

    def __len__(self):
        return len(self.lines)

    def insert(self, index, value):
        'S.insert(index, value) -- insert value before index'
        # First we have to make sure that the line where we want to
        # insert a line exists:
        self[index]
        # Now we can insert:
        self.lines.insert(index, value)
        self.widgets.insert(index, None)

    def append(self, value):
        'S.append(value) -- append value to the end of the sequence'
        if not self[-1][-1] in ('\n', '\r'):
            self[-1] = self[-1] + self.newline
        self.lines.append(value)
        self.widgets.append(None)

    def clear(self):
        'S.clear() -> None -- remove all items from S'
        self.lines = []
        self.widgets = []
        self.file.seek(0, 2)

    def extend(self, values):
        'S.extend(iterable) -- extend sequence by appending elements from the iterable'
        if not self[-1][-1] in ('\n', '\r'):
            self[-1] = self[-1] + self.newline
        self.lines.extend(values)
        self.widgets.extend([None for x in values])

    def delete_characters(self, fromrow, fromcol, torow, tocol):
        start = self[fromrow][:fromcol]
        end = self[torow][tocol:]
        for row in range(torow, fromrow, -1):
            del self[row]
        self[fromrow] = start + end
