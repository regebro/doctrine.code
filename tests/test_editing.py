# -*- coding: UTF-8 -*-
import io
import unittest
from doctrine.code import Code


class TestCode(unittest.TestCase):

    def test_lazyness(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        self.assertEqual(c[1], 'with several\n')
        # The third line should not yet have been read:
        self.assertEqual(len(c.lines), 2)

    def test_getlines(self):
        f = io.StringIO(u'A text\nwith several\nlines')
        c = Code(f, 'text')
        self.assertEqual(c[1], 'with several\n')
        self.assertEqual(c[2], 'lines')
        self.assertRaises(IndexError, c.__getitem__, 3)

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

