# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2020 Dec 10 at 11:01 
# Description of <test_common>
#
import datetime
from collections import OrderedDict
from functools import cached_property
from unittest import TestCase
from ..html.elements import BaseHTMLElement, NamedHTMLElement, UnsafeHTMLElementDataError


# @author Semyon Mamonov <semyon.mamonov@gmail.com>
class TestBaseHTMLElement(TestCase):

    def setUp(self) -> None:
        self.element = BaseHTMLElement()
        # next data copied from body of html.escape(s, quote=True)
        self.unsafe_chars = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", '\'': "&#x27;"}

    @cached_property
    def _get_simple_sequence_2tuple(self):
        """
            It returns 2-tuple (simple_sequence, result_simple_sequence)
            where each element in simple_sequence is not safe and
            result_simple_sequence will contain all elements that were
            string-transformed exclude elements that detected as safe
        """
        simple_sequence = [
            1234, 1.234, '1234', datetime.date.today(), datetime.datetime.today(), self._get_test_safe_3tuple[1]
        ]
        result_simple_sequence = [str(v) if not hasattr(v, '__html__') else v.__html__() for v in simple_sequence]
        return simple_sequence, result_simple_sequence

    def _test_safe_value(self, safe_value, test_type=None):
        """
            It does base 2 tests:
            1 - if test_type is not None then will test assertIsInstance
            2 - In any cases safe_value will be tested on assertTrue(hasattr(safe_value, '__html__')....
            with nicer message
        """
        if test_type is not None:
            if isinstance(test_type, type):
                test_type = (test_type,)
            self.assertIsInstance(safe_value, test_type, 'Value should be of {0}s type(s)'.format(
                str([v.__name__ for v in test_type])
            ))
        self.assertTrue(hasattr(safe_value, '__html__'), 'Value not safe cause has not attribute __html_')

    @cached_property
    def _get_test_safe_3tuple(self):
        """
        Returns 3-tuple TestSafeType, test_safe_data_object, test_safe_data_object.__html__() - safe representation
        """
        test_safe_type = type('TestType__html__', (str,), {
            '__html__': lambda class_self: class_self.__class__.__name__+class_self
           })
        test_safe_data = test_safe_type(': Test safe type value')
        self.assertEqual(test_safe_data.__html__(), 'TestType__html__: Test safe type value')
        # 1 - safe type, 2 - safe instance, 3 - default safe data
        return test_safe_type, test_safe_data, test_safe_data.__html__()

    @cached_property
    def _get_html_test_data(self):
        """
            It returns dict where key is expected string and value BaseHTMLElement
            Something like
            <div ....>...</div>
            <br .... />
            <span ...>...</span>
            <div ....>
                HTML representation of 3 lines above
            </div>
        """

        e_type = self.element.__class__
        result_test_data = OrderedDict()

        test_str = '<div&amp;&lt;&gt;&quot;&#x27; id="div_inner" class_12334="div_class_value">12334'\
                   '</div&amp;&lt;&gt;&quot;&#x27;>'
        ediv = e_type(
            12334,
            tag='div'+''.join(self.unsafe_chars),
            attrs=OrderedDict([('id', 'div_inner'), ('class_12334', "div_class_value")])
        )
        result_test_data[test_str] = ediv

        test_str = '<br id="br_inner" class="br_class&amp;&lt;&gt;&quot;&#x27;" />'
        ebr = e_type(
            tag='br',
            attrs=OrderedDict([('id', 'br_inner'), ('class', "br_class"+''.join(self.unsafe_chars))])
        )
        result_test_data[test_str] = ebr

        test_str = '<span id="span_inner" class="class_span">SPAN text&amp;&lt;&gt;&quot;&#x27;</span>'
        espan = e_type(
            'SPAN text'+''.join(self.unsafe_chars),
            tag='span',
            attrs=OrderedDict([('id', 'span_inner'), ('class', "class_span")])
        )
        result_test_data[test_str] = espan

        test_str = '<div id="div_outer" class="hhh jjj kkk">{0}</div>'.format(''.join(result_test_data))
        ediv_as_outer_for_all = e_type(tag='div', attrs=OrderedDict([('id', 'div_outer'), ('class', "hhh jjj kkk")]))
        ediv_as_outer_for_all.data = [ediv, ebr, espan]
        result_test_data[test_str] = ediv_as_outer_for_all

        return result_test_data

    def test_tag(self):
        self.assertEqual(self.element.tag, '')
        self.element.tag = 'p'
        self._test_safe_value(self.element.tag, str)
        self.assertEqual(self.element.tag, 'p')

    def test_attrs(self):
        e = self.element
        self.assertIsInstance(e.attrs, (dict, ))
        attr_class_name = e.__class__.__name__+'AttributeComposerDict'
        self.assertTrue(e.attrs.__class__.__name__,
                        'Type of element.attrs must be {0}'.format(attr_class_name))
        self.assertEqual(e.attrs, {})
        self.assertEqual(str(e.attrs), '')
        attrs = {'type': 'input', 'class': 'class_one class_two'}
        attrs_str = 'type="input" class="class_one class_two"'
        e.attrs = attrs
        self.assertListEqual(str(e.attrs).split(' '), attrs_str.split(' '))
        self.assertDictEqual(e.attrs, attrs)
        e.attrs['id'] = 'some_id_value'
        attrs_str += ' id="some_id_value"'
        self.assertListEqual(str(e.attrs).split(' '), attrs_str.split(' '))

    def test_data(self):
        e = self.element
        self.assertIsNone(e.data)
        e.data = 12345
        self.assertEqual(12345, e.data)
        simple_sequence, result_simple_sequence = self._get_simple_sequence_2tuple
        e.data = simple_sequence
        self.assertListEqual(e.data, simple_sequence)
        simple_sequence.append(object())
        e.data = simple_sequence
        self.assertListEqual(e.data, simple_sequence)
        with self.assertRaises(UnsafeHTMLElementDataError):
            e._compose_data(simple_sequence)

    def test__test_simple_value_on_safe(self):
        e = self.element
        self.assertFalse(e._is_value_safe(''))
        self.assertFalse(e._is_value_safe(object()))
        self.assertFalse(e._is_value_safe(None))
        self.assertTrue(e._is_value_safe(e.__class__()))
        self.assertTrue(e._is_value_safe(self._get_test_safe_3tuple[1]))

    def test__simple_value_to_safe(self):
        e = self.element
        for value in [1234, 1.234, '1234', datetime.date.today(), datetime.datetime.today()]:
            safe_value = e._value_to_safe_or_exception(value)
            self.assertEqual(safe_value, str(value))
            self._test_safe_value(safe_value, str)

        self.assertRaises(UnsafeHTMLElementDataError, e._value_to_safe_or_exception, object())
        self.assertRaises(UnsafeHTMLElementDataError, e._value_to_safe_or_exception, [object()])
        self.assertEqual(e._value_to_safe_or_exception(self._get_test_safe_3tuple[1]), self._get_test_safe_3tuple[1])

    def test_value_to_safe(self):
        e = self.element
        self.assertEqual('', e.value_to_safe(None))
        self.assertEqual('', e.value_to_safe([]))
        str_val = 'string value'
        safe_value = e.value_to_safe(str_val)
        self.assertEqual(str_val, str_val)
        self._test_safe_value(safe_value, (str,))

    def test_add_data(self):
        e = self.element
        simple_sequence, result_simple_sequence = self._get_simple_sequence_2tuple
        e.data = simple_sequence
        e.add_data(self._get_test_safe_3tuple[1])
        self.assertEqual(len(simple_sequence)+1, len(e.data), 'One safe value was not added.')
        e.add_data('0987654321')
        self.assertEqual(len(simple_sequence)+2, len(e.data), 'One unsafe value was not added.')
        self.assertListEqual(e.data, [*simple_sequence, self._get_test_safe_3tuple[1], '0987654321'])
        #####
        e.data = None
        self.assertIsNone(e.data)
        self.assertEqual(e.add_data('9458362').data, '9458362')
        # data have differences
        with self.assertRaises(AssertionError):
            self.assertListEqual(e.add_data(simple_sequence).data, simple_sequence)
        self.assertListEqual(e.data, ['9458362', *simple_sequence])
        ########
        e.data = None
        for value in simple_sequence:
            e.add_data(value)
        self.assertEqual(len(simple_sequence), len(e.data))
        self.assertListEqual(e.data, simple_sequence)

    def test__compose_data(self):
        e = self.element

        unsafe_sequence, result_sequence = self._get_simple_sequence_2tuple
        unsafe_sequence.extend((None, [], ''))
        result_sequence.extend(('', '', ''))

        for i, unsafe in enumerate(unsafe_sequence):
            safe_value = e._compose_data(unsafe)
            self.assertEqual(result_sequence[i], safe_value)
            self._test_safe_value(safe_value, str)

    def test_compose(self):
        # e, test_result_str, result_inner_test_data = self._get_html_test_data
        # self.assertEqual(e.compose(), test_result_str)
        for expected, e in self._get_html_test_data.items():
            self.assertEqual(expected, e.compose())

        e = self.element
        # below the choices for all are empty, only tag, only attrs, .....
        # all are empty
        e.data, e.tag, e.attrs = (None, None, None)
        self.assertEqual(e.compose(), '')
        e.tag = 'input'
        self.assertEqual(e.compose(), '<input />')
        e.tag = 'div'
        self.assertEqual(e.compose(), '<div></div>')
        e.data = 1234
        self.assertEqual(e.compose(), '<div>1234</div>')
        e.attrs = OrderedDict([('class', 'class value'), ('id', 'id_value')])
        self.assertEqual(e.compose(), '<div class="class value" id="id_value">1234</div>')
        e.data = None
        self.assertEqual(e.compose(), '<div class="class value" id="id_value"></div>')
        e.tag = 'br'
        self.assertEqual(e.compose(), '<br class="class value" id="id_value" />')
        e.tag = None
        self.assertEqual(e.compose(), '')
        e.data = 'simple string'
        self.assertEqual(e.compose(), 'simple string')
        simple_sequence, result_simple_sequence = self._get_simple_sequence_2tuple
        e.data = simple_sequence
        self.assertEqual(e.compose(), ''.join(result_simple_sequence))

    def test__str__(self):
        for expected, e in self._get_html_test_data.items():
            self.assertEqual(str(e), expected)

        self.element.max_str_call_num = 1
        with self.assertRaises(RecursionError):
            for i in range(self.element.max_str_call_num+1):
                str(self.element)
        self.element.max_str_call_num = self.element.__class__.max_str_call_num


class TestNamedHTMLElement(TestCase):

    def setUp(self) -> None:
        self.element = NamedHTMLElement('root')

    def _init_element_test_data(self):
        e = self.element
        e.tag = 'root'
        elref = {
            '1': [
                NamedHTMLElement(element_name='1', tag='1'),
                NamedHTMLElement(element_name='1', tag='11'),
                NamedHTMLElement(element_name='1', tag='111')
            ],
            '2': [NamedHTMLElement(element_name='2', tag='2'), NamedHTMLElement(element_name='2', tag='22')],
            '3': [NamedHTMLElement(element_name='3', tag='3'), NamedHTMLElement(element_name='3', tag='33')],
        }
        e.data = [elref['1'][0], 123, elref['1'][1], elref['2'][0]]
        e.data[0].data = [elref['3'][0], 123, elref['1'][2], elref['2'][1]]
        e.data[2].data = [elref['3'][1], elref['2'][1]]
        e.data[0].data[3].data = 12345

        return elref

    def test_element_name(self):
        e = self.element
        self.assertIsNone(e.element_name)
        with self.assertRaises(TypeError):
            e.element_name = object()
        element_name = str(id(object()))
        e.element_name = element_name
        self.assertEqual(e.element_name, element_name)

    def test_get_elements_by(self):
        elrefs = self._init_element_test_data()
        e = self.element
        for name, els in elrefs.items():
            elres = []
            e.get_elements_by(elres, name)
            # test of all - element with name='2',tag='22' used twice. test this case
            if name == '2':
                self.assertEqual(
                    len(elres)-1, len(els),
                    "Because element with name='2',tag='22' used twice then"
                    " initial and found lists must be differ at 1 by length."
                )
            # test unique
            self.assertEqual(set(elres), set(els), 'Set of elements that were found and initial are not equals.')

    def test__str__(self):
        self.element.max_str_call_num = 1
        with self.assertRaises(RecursionError):
            for i in range(self.element.max_str_call_num + 1):
                str(self.element)
        self.element.max_str_call_num = self.element.__class__.max_str_call_num
