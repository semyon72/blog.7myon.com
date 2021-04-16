# Project: blog_7myon_com
# Package: 
# Filename: htmltools.py
# Generated: 2020 Dec 20 at 12:04 
# Description of <htmltools>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>


from collections import OrderedDict, namedtuple
from html.parser import HTMLParser
import html

# https://html.spec.whatwg.org/multipage/syntax.html#void-elements
from typing import NamedTuple

HTML_VOID_ELEMENTS = ('area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                      'input', 'link', 'meta', 'param', 'source', 'track', 'wbr')


def isequal_as_html(data1, data2):
    comparer = HTMLComparer()
    return comparer.isequal(data1, data2)


class Tag(NamedTuple):
    """
        str() returns escaped (HTML safe) representation of itself by default
        if you need escape of escaping or make custom translation "tag" and "attrs"
        you need invoke Tag.compose(escape_func = appropriate function).
    """
    tag: str = None
    attrs: list = None
    isstart: bool = True
    """
    "isstart" - indicate that this tag was parsed either as end of tag like </div> or start <div....>
    For example, if you want to say that Tag's instance should be exposed as end of tag like </div>
    then 'isstart' should be False otherwise for exposition <div .... attrs ....> the 'isstart' should be True.
    But exists some exclusions if 'tag' contains in HTML_VOID_ELEMENTS and 'isstart' is False then
    it will return '' (empty string). This behaviour is helpful for using inside HTMLParser.handle_endtag(self, tag).
    It will keep appropriate place but will have not a visual representation.
    """
    def compose(self, escape_func=html.escape):
        tag, attrs, tagender = (escape_func(self.tag), '', '>')

        if not self.isstart:
            if tag in HTML_VOID_ELEMENTS:
                return ''
            tag = '/'+tag
        else:
            if tag in HTML_VOID_ELEMENTS:
                tagender = ' /' + tagender

            if isinstance(self.attrs, list):
                attrs = ' '.join(
                    escape_func(attr) + (''.join(['="', escape_func(val), '"']) if val is not None else '')
                    for attr, val in OrderedDict(self.attrs).items()
                )
                if attrs:
                    attrs = ' '+attrs

        return ''.join(['<', tag, attrs, tagender])

    def __str__(self):
        return self.compose()

    def _is_equal_attrs(self, other):
        one = self.attrs
        if isinstance(one, list):
            one = dict(self.attrs)
        if isinstance(other, list):
            other = dict(other)
        return one == other

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.tag == other.tag and self.isstart == other.isstart and self._is_equal_attrs(other.attrs)

    def __ne__(self, other):
        return not self.__eq__(other)


class HTMLComparer(HTMLParser):

    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.escape = lambda x: x
        if self.convert_charrefs:
            self.escape = html.escape
        self.__data = []  # it is result of parsing

    def handle_starttag(self, tag, attrs):
        """
            This method is called to handle the start of a tag (e.g. <div id="main">).
            For instance, for the tag <A HREF="https://www.cwi.nl/">,
            this method would be called as handle_starttag('a', [('href', 'https://www.cwi.nl/')]).
        """
        _attrs = None
        if len(attrs) > 0:
            _attrs = attrs
        self.__data.append(Tag(tag=tag, attrs=_attrs, isstart=True))

    def handle_endtag(self, tag):
        """
            This method is called to handle the end tag of an element (e.g. </div>).
        """
        if tag not in HTML_VOID_ELEMENTS:
            self.__data.append(Tag(tag=tag, attrs=None, isstart=False))

    def handle_data(self, data):
        """
            This method is called to process arbitrary data
            (e.g. text nodes and the content of <script>...</script> and <style>...</style>).
        """
        data = data.strip()
        if data:
            self.__data.append(data)

    def parse_and_clean(self, src):
        """
            Returns 2-tuple [0] is parsed Tag elements and [1] is string cleaned string that presents "src" string
        """
        self.__data.clear()
        self.feed(src)
        parsed = []
        cleaned = []
        for value in self.__data:  # self.__data looks like [tag,[tag,[(attr,value_str),....]], .....]
            parsed.append(value)
            cleaned.append(str(value))
        return parsed, ''.join(cleaned)

    def isequal(self, src1, src2):
        parsed1, clean1 = self.parse_and_clean(src1)
        parsed2, clean2 = self.parse_and_clean(src2)
        if len(parsed2) != len(parsed1):
            return False

        for idx, tag in enumerate(parsed1):
            if tag != parsed2[idx]:
                return False

        return True

    def get_diff(self, src1, src2):
        res_diff_type = namedtuple('Differences', ['clean1', 'clean2', 'diffs'])
        parsed1, clean1 = self.parse_and_clean(src1)
        parsed2, clean2 = self.parse_and_clean(src2)
        diffs = []
        for idx, tag in enumerate(parsed1):
            if tag != parsed2[idx]:
                diffs.append(''.join(['"', str(tag), '" != "', str(parsed2[idx]), '"']))
        return res_diff_type(clean1=clean1, clean2=clean2, diffs=diffs)
