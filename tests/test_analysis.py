# -*- coding: UTF-8 -*-
import io
import unittest
from doctrine.code import Code
from doctrine.code import Analyzer

TEST_CODE = u'''class CodeLayout(TextLayout):
    """This is a docstring"""

    tab_width = 8

    def calculate_text_segments(self, text, width, wrap):
        """
        Calculate the segments of text to display given width screen
        columns to display them.

        text - unicode text or byte string to display
        width - number of available screen columns
        wrap - wrapping mode used

        Returns a layout structure without alignment applied.
        """

        # TODO: This function is a horror and a mess, and really hard to
        # understand. It's based on urwids StandardLayout, which by itself
        # is overly complex, and I added tab handling, which made it worse.
        # It's a prime candidate for refacturing, making easier to understand
        # and as it is heavily used, profiling would be nice too.

        nl, nl_o, sp_o, tab_o = "\n", "\n", " ", "\t"
        if PYTHON3 and isinstance(text, bytes):
            nl = B(nl) # can only find bytes in python3 bytestrings
            nl_o = ord(nl_o) # + an item of a bytestring is the ordinal value
            sp_o = ord(sp_o)
            tab_o = ord(tab_o)
        b = []
        p = 0
        if wrap == 'clip':
            # no wrapping to calculate, so it's easy.
            while p<=len(text):
                n_cr = find_newline(text, p)
                if p == n_cr:
                    # A line with no characters.
                    l.append((0, n_cr))
                    continue

            # force any char wrap
            if l:
                b.append(l)
            p += pt
        return b
'''


# We need a "dummy" analyzer for testing.

class PythonTestAnalyzer(Analyzer):

    def find_block(self, start_row, max_block):
        # This dummy Python analyzer looks for multiline strings
        lines = []
        multiline = None
        for row in range(start_row, start_row + max_block):

            pos = 0
            line = self.code[row]
            lines.append(line)
            l = len(line)

            while pos < l:
                npos = line.find('"""', pos)
                if npos != -1:
                    # A multiline string?
                    if multiline is None:  # Yes, the start!
                        multiline = '"""'
                    elif multiline == '"""':  # Yes, the end!
                        multiline = None

                    pos = npos + 3
                    continue

                npos = line.find("'''", pos)
                if npos != -1:
                    # A multiline string?
                    if multiline is None:  # Yes, the start!
                        multiline = "'''"
                    elif multiline == "'''":  # Yes, the end!
                        multiline = None

                    pos = npos + 3
                    continue

                # Neither were found.
                break

            # We reached the end of the line.
            if multiline is None:
                # We are not in a multiline string at the moment:
                return lines
            # else we read the next row and see if the multiline string ends.

        # And we now reached the maximum lenght we are willing to read
        # before giving up
        return lines


class TestAnalysis(unittest.TestCase):

    def test_blocks(self):
        # One of the primary tasks of the analyzer is to find blocks
        # of code that have valid syntax and can be highlighted.
        f = io.StringIO(TEST_CODE)
        c = Code(f)
        a = PythonTestAnalyzer(c)

        self.assertEqual(a.find_block(0, 10),
                         ['class CodeLayout(TextLayout):\n'])

        self.assertEqual(a.find_block(1, 10),
                         ['    """This is a docstring"""\n'])

        self.assertEqual(a.find_block(6, 10),
                         ['        """\n',
                          '        Calculate the segments of text to display '
                          'given width screen\n',
                          '        columns to display them.\n',
                          '\n',
                          '        text - unicode text or byte string to '
                          'display\n',
                          '        width - number of available screen columns'
                          '\n',
                          '        wrap - wrapping mode used\n',
                          '\n',
                          '        Returns a layout structure without '
                          'alignment applied.\n',
                          '        """\n'])

        self.assertEqual(a.find_block(6, 3),
                         ['        """\n',
                          '        Calculate the segments of text to display '
                          'given width screen\n',
                          '        columns to display them.\n'])
