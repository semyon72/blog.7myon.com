# Project: blog_7myon_com
# Package: 
# Filename: elements.py
# Generated: 2020 Dec 18 at 04:44 
# Description of <elements>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from datetime import date
from typing import Any

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from ..core.basedata import NamedDataMixin, BaseData, ParentedDataMixin


class UnsafeHTMLElementDataError(Exception):
    pass


class BaseHTMLElement(ParentedDataMixin, BaseData):

    max_str_call_num = 100

    unsafe_html_data_default_error_message = 'Value is not marked as safe. Value: "{0}"'

    unsafe_to_safe_converters = {
        # escape() inside conditional_escape() invoke str(x) on its own.
        # Any of converter functions must return html safe string
        # that is marked as safe (has __html__ attribute)
        (int, date, float, str): lambda x: conditional_escape(x),
        type(None): lambda x: mark_safe(''),
        bytes: lambda x: conditional_escape(x.decode()),
    }

    # https://html.spec.whatwg.org/multipage/syntax.html#void-elements
    # Void elements only have a start tag; end tags must not be specified for void elements.
    html_void_elements = ('area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                          'input', 'link', 'meta', 'param', 'source', 'track', 'wbr')

    def __init__(self, data=None, tag=None, attrs=None):
        super().__init__(data)
        self.tag = tag
        self.attrs = attrs
        self.max_str_call_num = self.max_str_call_num

    @property
    def tag(self):
        return self.__tag

    @tag.setter
    def tag(self, value):
        self.__tag = conditional_escape(value if value is not None else '')

    @property
    def attrs(self):
        return self.__attrs

    @attrs.setter
    def attrs(self, attrs):

        def compose_attrs(attrs_dict):
            result = []
            for key, value in attrs_dict.items():
                result.append(conditional_escape(key)+'='+'"'+conditional_escape(value)+'"')
            return mark_safe(' '.join(result))

        _attrs_dict_type = type(self.__class__.__name__+'AttributeComposerDict', (dict,), {'__str__': compose_attrs})
        self.__attrs = _attrs_dict_type(attrs) if attrs is not None else _attrs_dict_type()

    @staticmethod
    def _is_value_safe(value):
        return hasattr(value, '__html__')

    def _value_to_safe_or_exception(self, value):
        """
            Returns safe value or raise Exception
            If value supports SafeData interface (__html__ attribute)
            then will returned at once otherwise it will be try to convert
            in appropriate safe_value. The method does not do any recursions.
        """
        if self._is_value_safe(value):
            return value

        value_type = type(value)
        converter_func = self.unsafe_to_safe_converters.get(value_type)
        # second try to resolve appropriate converter
        # we will suppose that one or more of key(s) is tuple
        if converter_func is None:
            tk = tuple(
                k for k in self.unsafe_to_safe_converters if hasattr(k, '__iter__') and issubclass(value_type, k)
            )
            if len(tk) > 0:
                converter_func = self.unsafe_to_safe_converters.get(tk[0])
            else:
                converter_func = (lambda x: x)

        value = converter_func(value)
        # now, value still can be unsafe
        if not self._is_value_safe(value):
            raise UnsafeHTMLElementDataError(self.unsafe_html_data_default_error_message.format(value))

        return value

    def value_to_safe(self, value) -> str:
        """
            This function is wrapper that use _value_to_safe_or_exception()
            for getting safe value from sequences and sole values.
            The method does not do any recursions.
        """
        if hasattr(value, '__iter__') and not isinstance(value, self.ignore_iterable_types):
            safe_value = ''.join((self._value_to_safe_or_exception(v).__html__() for v in value))
        else:
            safe_value = self._value_to_safe_or_exception(value).__html__()

        return mark_safe(safe_value)

    def _compose_data(self, data):
        return self.value_to_safe(data)

    def _get_tag_start_end(self):
        attrs = str(self.__attrs)
        tag_start, tag_end, attrs_pre_separator = '', '', ''
        if attrs:
            attrs_pre_separator = ' '
        if self.__tag:
            tag_start_parts = ['<', self.__tag, attrs_pre_separator, attrs]
            if str(self.__tag).lower() not in self.html_void_elements:
                tag_end = ''.join(['</', self.__tag, '>'])
                tag_start_parts.append('>')
            else:
                tag_start_parts.append(' />')
            tag_start = ''.join(tag_start_parts)
        return tag_start, tag_end

    def compose(self):
        tag_body = self._compose_data(self.data)
        if not self._is_value_safe(tag_body):
            raise UnsafeHTMLElementDataError(self.unsafe_html_data_default_error_message.format(tag_body))
        tag_start, tag_end = self._get_tag_start_end()
        if tag_end:
            tag_parts = [tag_start, tag_body, tag_end]
        elif tag_start:
            tag_parts = [tag_start]
            if tag_body:
                tag_parts.append(''.join(['<!-- Possible ERROR: tag contain in list of tags that void end of tag ',
                                          str(self.html_void_elements), ' but has tag\'s body. ', " Body of tag is: ",
                                          tag_body, ' //-->']))
        else:
            tag_parts = [tag_body]
        return mark_safe(''.join(tag_parts))

    def __str__(self):
        if self.max_str_call_num < 1:
            erval = {'class': type(self).__name__, 'id': id(self), 'element_name': ''}
            erinfo = '<{class} object at {id}{element_name}>'
            if hasattr(self, 'element_name'):
                erval['element_name'] = ', "element_name" is "{0}"'.format(getattr(self, 'element_name'))
            erinfo = erinfo.format(**erval)
            raise RecursionError(
                'Max number of calls of __str__ are exceeded ({0}) in {1}.'
                ' Probably, your code is not optimal or has a dead loop,'
                ' otherwise increase "max_str_call_num".'.format(type(self).max_str_call_num, erinfo)
            )
        else:
            self.max_str_call_num -= 1
        return self.compose()

    def __html__(self):
        return str(self)


class NamedHTMLElement(NamedDataMixin, BaseHTMLElement):

    def __init__(self, data=None, tag=None, attrs=None, element_name=None):
        BaseHTMLElement.__init__(self, data, tag, attrs)
        NamedDataMixin.__init__(self, element_name)
