# -*- coding: utf-8 -*-

class UNException(Exception):
    pass


class OutsideBoundryError(UNException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return (repr(self.value))
