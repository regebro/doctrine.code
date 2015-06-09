# -*- coding: UTF-8 -*-


# I'm not using abc's, because I want to be able for plugins to implement the
# API only partially.

class Analyzer(object):
    def __init__(self, code):
        self.code = code

    def find_block(self, start_row, max_block):
        raise NotImplementedError
