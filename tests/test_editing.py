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

        c.delete_characters(1, 2, 1, 3)
        self.assertEqual(c[1], 'wih several\n')

        c.delete_characters(1, 3, 1, 4)
        self.assertEqual(c[1], 'wihseveral\n')

        c.delete_characters(0, 5, 2, 2)
        self.assertEqual(c[0], 'A texnes')
        self.assertRaises(IndexError, c.__getitem__, 1)

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
        self.assertRaises(IndexError, c.__getitem__, 0)
