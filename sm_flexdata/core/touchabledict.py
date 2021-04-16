# Project: blog_7myon_com
# Package: 
# Filename: touchabledict.py
# Generated: 2021 Mar 12 at 23:49 
# Description of <touchabledict>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from collections import UserDict


class TouchableDict(UserDict):

    def __init__(self, *args, **kwargs):
        self.touched_keys = set()
        self.is_touchable = False
        super().__init__(*args, **kwargs)
        self.is_touchable = True

    def touch(self, key):
        if self.is_touchable:
            self.touched_keys.add(key)

    def is_touched(self, key):
        return key in self.touched_keys

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.touch(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.touched_keys.discard(key)

    def __getitem__(self, key):
        try:
            v = super().__getitem__(key)
            self.touch(key)
        except KeyError as err:
            raise err
        else:
            return v

    def touched_items(self):
        result = []
        self.is_touchable = False
        try:
            for key in self.touched_keys:
                result.append((key, self[key]))
        finally:
            self.is_touchable = False
        return result

    def untouched_keys(self):
        return set(self.keys()) - self.touched_keys

    def untouched_items(self):
        result = []
        self.is_touchable = False
        try:
            for key in self.untouched_keys():
                result.append((key, self[key]))
        finally:
            self.is_touchable = False
        return result

    def clean_untouched(self):
        for key in self.untouched_keys():
            del self[key]
        return self

