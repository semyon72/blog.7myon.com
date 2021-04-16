# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2021 Mar 13 at 01:12 
# Description of <test_touchabledict>
#

from unittest import TestCase

from ..core.touchabledict import TouchableDict


# @author Semyon Mamonov <semyon.mamonov@gmail.com>
class TestTouchableDict(TestCase):

    def setUp(self) -> None:
        self._dict = {'a': 'aaa', 'b': 'bb', 'a1': 111}
        self._dict_keys_set = set(self._dict)

    def test_base_action(self):
        td = TouchableDict(self._dict)
        td.is_touchable = False
        self.assertEqual(self._dict, td)
        td.is_touchable = True
        self.assertEqual(td.touched_keys, set())
        td = TouchableDict(**self._dict)
        self.assertEqual(td.touched_keys, set())
        self.assertEqual(self._dict, td)
        td = TouchableDict(self._dict.items())
        self.assertEqual(td.touched_keys, set())
        self.assertEqual(self._dict, td)

        td = TouchableDict({})
        td.update(self._dict)
        self.assertEqual(td.touched_keys, self._dict_keys_set)

        td = TouchableDict()
        td.update(**self._dict)
        self.assertEqual(td.touched_keys, self._dict_keys_set)

    def test_touch(self):
        td = TouchableDict(self._dict)

        td.is_touchable = False
        for k, v in td.items():
            pass
        self.assertEqual(td.touched_keys, set())
        td.is_touchable = True

        for k in td.keys():
            pass
        self.assertEqual(td.touched_keys, set())

        for k in td:
            pass
        self.assertEqual(td.touched_keys, set())

    def test_touched_items(self):
        td = TouchableDict()
        td.update(**self._dict)

        od = dict(td.touched_items())
        self.assertEqual(od, self._dict)
        self.assertEqual(td.touched_keys, self._dict_keys_set)
