# -*- coding: UTF-8 -*-
import io
import unittest
from doctrine.code import Code


class TestCodeEditing(unittest.TestCase):

    def test_lazyness(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        self.assertEqual(c[1], 'with several\n')
        # The third line should not yet have been read:
        self.assertEqual(len(c.lines), 2)

    def test_getlines(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        # Test that you can get lines out of order:
        self.assertEqual(c[2], 'lines')
        self.assertEqual(c[0], 'A text\n')
        self.assertEqual(c[1], 'with several\n')

        # And you get an error if the line doesn't exist.
        self.assertRaises(IndexError, c.__getitem__, 3)

        # You can iterate:
        i = 0
        for x in c:
            i += 1
        self.assertEqual(i, 3)

    def test_delete_code(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')

        t = c.delete_text(1, 2, 1, 3)
        self.assertEqual(c[1], 'wih several\n')
        self.assertEqual(t, 't')

        t = c.delete_text(1, 3, 1, 4)
        self.assertEqual(c[1], 'wihseveral\n')
        self.assertEqual(t, ' ')

        t = c.delete_text(0, 5, 2, 2)
        self.assertEqual(c[0], 'A texnes')
        self.assertRaises(IndexError, c.__getitem__, 1)
        self.assertEqual(t, 't\nwihseveral\nli')

    def test_add_lines(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        c.insert(1, 'New line\n')
        self.assertEqual(c[1], 'New line\n')
        self.assertEqual(c[2], 'with several\n')

        # If you add lines and the last line doesn't have
        # a line feed, it must get one:
        c.extend(['More\n', 'text'])
        self.assertEqual(len(c), 6)
        self.assertEqual(c[3], 'lines\n')

        self.assertEqual(c[5], 'text')
        c.append('A last line')
        self.assertEqual(c[5], 'text\n')
        self.assertEqual(len(c), 7)

    def test_clear(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        self.assertEqual(c[0], 'A text\n')
        c.clear()
        self.assertEqual(c[0], '')
        self.assertRaises(IndexError, c.__getitem__, 1)

    def test_ending_newline(self):
        f = io.StringIO(u'A text\nwith several\nlines\n')
        c = Code(f, 'text')
        # If the last line ends with a newline, there should
        # be an extra empty line.
        self.assertEqual(c[3], '')

    def test_len(self):
        # Getting the length should read in the whole file.
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        self.assertEqual(len(c), 3)

    def test_merge_split(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        # Let's stick a silly newline in, just because:
        c.split_row(1, 5, '\r\n')
        self.assertEqual(len(c), 4)
        self.assertEqual(c[1], u'with \r\n')
        self.assertEqual(c[2], u'several\n')

        c.merge_rows(1, 2)
        self.assertEqual(len(c), 3)
        self.assertEqual(c[1], u'with several\n')

    def test_empty_file(self):
        f = io.StringIO(u'')
        c = Code(f, 'text')
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0], '')
        # Pressing enter in an empty file:
        c.split_row(0, 0, '\n')
        self.assertEqual(c[0], '\n')
        self.assertEqual(c[1], '')

    def test_insert_row(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')

        c.insert_text(1, 5, u'some inserted text ')
        self.assertEqual(len(c), 3)
        self.assertEqual(c[1], u'with some inserted text several\n')

        c.insert_text(2, 0, u'bop')
        self.assertEqual(len(c), 3)
        self.assertEqual(c[2], u'boplines')

        c.insert_text(2, 8, u'iolo')
        self.assertEqual(len(c), 3)
        self.assertEqual(c[2], u'boplinesiolo')

    def test_insert_rows(self):
        f = io.StringIO(u'A text\nwith several\nlines\n')
        c = Code(f, 'text')

        c.insert_text(1, 5, u'some inserted\r\ntext between\n')
        self.assertEqual(len(c), 6)
        self.assertEqual(c[1], u'with some inserted\r\n')
