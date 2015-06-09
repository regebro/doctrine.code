# -*- coding: UTF-8 -*-
import tempfile
import unittest

from doctrine import code


class TestCodeContext(unittest.TestCase):

    def test_context(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write('This is\na text\n')
            tmp.flush()

            context = code.CodeContext(tmp.name, 'txt')
            with context.open() as c:
                c[-1]  # Load everything
                del c[0]
                context.save()

            tmp.seek(0)
            text = tmp.read()
            self.assertEqual(text, 'a text\n')
