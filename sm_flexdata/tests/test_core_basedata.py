# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2020 Dec 10 at 11:01 
# Description of <test_common>
#
import datetime
from functools import cached_property
from unittest import TestCase

from ..html.elements import BaseData


class TestBaseData(TestCase):

    def setUp(self) -> None:
        self.bd = BaseData()

    @cached_property
    def _get_test_data(self):
        # (value, result)
        o, d, dt = (object(), datetime.date.today(), datetime.datetime.today())
        result = [
            (o, o), (d, d), (dt, dt), ('string', 'string'), (1, 1), (2.3, 2.3), (None, None),
            (b'abcd', [ord('a'), ord('b'), ord('c'), ord('d')]),
            ([1, 2, 3], [1, 2, 3]),
            ((v for v in range(1, 4)), [1, 2, 3]),
            ((2, 3, 4), [2, 3, 4]),
            ({'k': 'k', 3: 3, 4.2: 4.2}, ['k', 3, 4.2])
        ]

        return result

    def test__value_to_list(self):
        for tv, rtv in self._get_test_data:
            rv = self.bd._process_value(tv)
            self.assertEqual(rv, rtv)

    def test_set_data(self):
        self.test__value_to_list()

    def test_data(self):
        self.bd.data = None
        self.assertIsNone(self.bd.data)
        for tv, rtv in self._get_test_data:
            self.bd.data = tv
            self.assertEqual(self.bd.data, rtv)

    def test_is_sole_data(self):
        sdl = ('string is sole data', None, 1, 2, object(), datetime.date.today())
        for tv in sdl:
            self.bd.data = tv
            self.assertTrue(self.bd.is_sole_data(), 'Value {} tested as not sole data'.format(tv))
        not_sdl = ([], (), {}, b'', (v for v in range(5)))
        for tv in not_sdl:
            self.bd.data = tv
            self.assertFalse(self.bd.is_sole_data(), 'Value {} tested as sole data'.format(tv))

    def test_set_data_as_is(self):
        for tv, rv in self._get_test_data:
            self.bd.set_data_as_is(tv)
            self.assertEqual(self.bd.data, tv)
