# Project: blog_7myon_com
# Package: 
# Filename: contenttools.py
# Generated: 2021 Apr 09 at 19:25 
# Description of <contenttools>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from functools import reduce
from html import unescape
from html.parser import HTMLParser

from .elements import BaseHTMLElement, NamedHTMLElement


def wrap_texts(text: str, needles, wrapper_begin, wrapper_end, max_text_length, ellipsis='...'):
    """
    This function does not limit result in the max_text_length length.
    max_text_length indicate how many chars from original text will be included in result
    but not include length of all wrapper_begin, wrapper_end, and ellipsis elements.
    Also, total number chars from original text can exceed max_text_length
    because result will be aligned on whole word.

    :param text: str - haystack
    :param needles: iterable - needles
    :param wrapper_begin: str
    :param wrapper_end: str
    :param max_text_length: int
    :param ellipsis: str
    :return: str
    """

    def find_and_wrap_all_needles_in_all_words(word_list, needles, wrapper_begin, wrapper_end):
        lower = str.lower
        flist, pos_in_text = ([], 0)
        for wrd_idx, wrd in enumerate(word_list):
            for needle in needles:
                pos_in_word = lower(wrd).find(lower(needle))
                if pos_in_word > -1:
                    pos_in_text += pos_in_word
                    flist.append((needle, wrd_idx, pos_in_word, pos_in_text))
                    wrd_lst = [*wrd]
                    wrd_lst.insert(pos_in_text + len(needle), wrapper_end)
                    wrd_lst.insert(pos_in_text, wrapper_begin)
                    word_list[wrd_idx] = ''.join(wrd_lst)
                else:
                    pos_in_text += len(wrd)
        return flist

    def find_and_wrap_sequence_needles_in_words(word_list, needles, wrapper_begin, wrapper_end):
        lower = str.lower
        flist, pos_in_text, cur_needle_idx, needles_len = ([], 0, 0, len(needles))
        for wrd_idx, wrd in enumerate(word_list):
            if cur_needle_idx < needles_len:
                needle = needles[cur_needle_idx]
                pos_in_word = lower(wrd).find(lower(needle))
                if pos_in_word > -1:
                    pos_in_text += pos_in_word
                    flist.append((needle, wrd_idx, pos_in_word, pos_in_text))
                    wrd_lst = [*wrd]
                    wrd_lst.insert(pos_in_text + len(needle), wrapper_end)
                    wrd_lst.insert(pos_in_text, wrapper_begin)
                    word_list[wrd_idx] = ''.join(wrd_lst)
                    cur_needle_idx += 1
                else:
                    pos_in_text += len(wrd)
            else:
                break

        return flist

    word_list = text.split()
    flist = find_and_wrap_sequence_needles_in_words(word_list, needles, wrapper_begin, wrapper_end)
    flist_len = len(flist)
    if flist_len == 0:
        return text

    text_len = len(text)
    if max_text_length > text_len:
        return ''.join(word_list)

    fword_info = flist[0]
    lword_info = flist[flist_len - 1]
    bidx = fword_info[3] - len(word_list[fword_info[1]]) + fword_info[2]  # aligned at first char of word in text
    eidx = lword_info[3] + len(lword_info[0])  # aligned at last char+1 of word in text
    word_list_len = len(word_list)
    if max_text_length > eidx - bidx:
        # we need to expand up to max_text_length range in word_list from both sides
        # and at final add ellipsis on ends of both sides
        current_length, min_word_idx, max_word_idx = (eidx-bidx, fword_info[1], lword_info[1])
        while current_length < max_text_length:
            if min_word_idx <= 0 and max_word_idx >= word_list_len-1:
                raise AssertionError('We never should be here.')
            for side in (0, 1):
                if side == 0:
                    # expands to left
                    if min_word_idx > 0:
                        min_word_idx -= 1
                        current_length += len(word_list[min_word_idx])
                else:
                    # expands to right
                    if max_word_idx < word_list_len-1:
                        max_word_idx += 1
                        current_length += len(word_list[max_word_idx])

                if current_length >= max_text_length:
                    break

        return ''.join((ellipsis, ' ', *word_list[min_word_idx:max_word_idx+1], ' ', ellipsis))

    else:
        # we need to collapse the range in word_list from both sides
        # and remove some data but not those in the flist
        # and at final add ellipsis on ends of both sides and between
        current_length, word_idxs = (eidx-bidx, [f[1] for f in flist])
        # TODO: Need finish
        raise NotImplementedError('TODO: Need to finish.')


class StringTruncator:

    TRUNCATE_LEFT = 0
    TRUNCATE_MIDDLE = 1
    TRUNCATE_RIGHT = 2
    # order of functions must correspond to the indices above and in meaning
    TRUNCATE_FUNC = ('truncate_left', 'truncate_middle', 'truncate_right')

    ellipsis = '...'

    def __init__(self, text, max_length=-1, locked=False, truncate_side=TRUNCATE_RIGHT, key_data=None):
        self.text = str(text)
        self.locked = bool(locked)
        self.max_length = max_length
        self.truncate_side = truncate_side

        # It does not use internally but it can be useful for sorting a list of StringTruncator-s for example
        # Inside TextTruncator it stores (begin_index_in original_text, end_index_in original_text)
        self.key_data = key_data

    @property
    def max_length(self):
        return self.__max_length

    @max_length.setter
    def max_length(self, max_length):
        max_length = int(max_length)
        if max_length < 0:
            max_length = len(self.text)
        self.__max_length = max_length

    @property
    def truncate_side(self):
        return self.__truncate_side

    @truncate_side.setter
    def truncate_side(self, truncate_side):
        truncate_side = int(truncate_side)
        if truncate_side not in (self.TRUNCATE_LEFT, self.TRUNCATE_MIDDLE, self.TRUNCATE_RIGHT):
            truncate_side = self.TRUNCATE_RIGHT
        self.__truncate_side = truncate_side

    def __str__(self) -> str:
        return self.truncate()

    def __get_trunc_length(self):
        txtl = len(self.text)
        assert self.max_length >= 0, 'max length must be >= 0'
        if txtl <= self.max_length:
            return 0
        dif = txtl - self.max_length
        return dif

    def truncate_left(self):
        trl = self.__get_trunc_length()
        if trl == 0:
            return self.text
        return '%s%s' % (self.ellipsis, self.text[trl:])

    def truncate_right(self):
        trl = self.__get_trunc_length()
        if trl == 0:
            return self.text
        return '%s%s' % (self.text[0:-trl], self.ellipsis)

    def truncate_middle(self):
        tl = len(self.text)
        trl = self.__get_trunc_length()
        if trl == 0:
            return self.text
        if trl == tl:
            return self.ellipsis

        text_middle = tl // 2
        lc_num = text_middle - (trl // 2)
        if lc_num < 1:
            lc_num = 1 # fix for flooring
        lst = self.text[0:lc_num]
        rc_num = tl - trl - lc_num
        rst = ''
        if rc_num > 0:
            rst = self.text[-rc_num:]
        return '%s%s%s' % (lst, self.ellipsis, rst)

    def truncate(self):
        if self.locked:
            return self.text
        return getattr(self, self.TRUNCATE_FUNC[self.truncate_side])()


class TextTruncator:
    """

    If result_max_length < than length of haystack (for example - 25)
    then parts that were not found will be truncated
    (at left, right sides or middle - depends from places).
    Main logic try to do it proportional but it leads to
    the result can have more than 25 original chars cause the removing is proportional
    and rounding to the floor is the cause of this effect
    """

    result_max_length = -1  # < 0 - means the whole haystack will be returned with wrapped needles
    wrapper_before = '<span class="found-text">'
    wrapper_after = '</span>'
    default_parser = 'parse_each_after_other_once'

    def __init__(self, haystack: str = '', needles='' ):
        super().__init__()
        self.haystack = haystack
        self.needles = needles
        self.__parsed_chains: list = []

    @property
    def needles(self) -> tuple:
        return self.__needles

    @needles.setter
    def needles(self, needles):
        if hasattr(needles, '__iter__') and not isinstance(needles, str):
            self.__needles = tuple(needles)
        else:
            self.__needles = tuple(str(needles).split()) if needles is not None else tuple()

    @property
    def haystack(self):
        return self.__haystack

    @haystack.setter
    def haystack(self, haystack):
        self.__haystack = str(haystack)

    @property
    def parsed_chains(self):
        return self.__parsed_chains

    def _calc_spacings(self, haystack, needle_positions):
        """
        It computes 4 cases
        1: ********needle*******
        2: needle*********needle
        3: needle*****needle****
        4: *****needle****needle

        :param haystack: original text
        :param needle_positions: should be sorted list of instances of StringTruncator
         which have corresponding positions of "needles" within haystack
        :return spacings: list of instances of StringTruncator which have corresponding positions
         within haystack but not for found "needles" - places between needles
        """
        spacings, hl, chi = ([], len(haystack), 0)
        for text_truncator in needle_positions:
            bi, ei = text_truncator.key_data
            if chi > hl:
                raise AssertionError(
                    'It never should happen. Probably exists the range intersections or list is unsorted'
                )
            if bi == 0:  # 2,3 cases
                chi = ei + 1
                continue
            elif ei == hl: # 2,4 cases
                chi = hl + 1
                continue
            if chi >= bi:
                raise AssertionError(
                    'Probably exists the range intersections or positions list was not sorted.'
                )
            str_trunc = StringTruncator(haystack[chi:bi], key_data=(chi, bi-1))
            spacings.append(str_trunc)  # general case *****Needle. 1,2,3,4 cases
            chi = ei+1

        if chi < hl:  # post processing for 1,3 cases
            str_trunc = StringTruncator(haystack[chi:], key_data=(chi, hl-1))
            spacings.append(str_trunc)  # 1,3 cases

        return spacings

    def __initial_parse_action(self, haystack, needles):
        if haystack:
            self.haystack = haystack
        if needles:
            self.needles = needles

        if not self.haystack or not self.needles:
            raise ValueError('Needles and haystack must not be empty')

    def parse_each_after_other_once(self, haystack='', needles=None):
        lower = str.lower
        find = str.find
        self.__initial_parse_action(haystack, needles)
        needles = self.needles
        haystack = lower(self.haystack)
        prev_char_i, found_idx, hlen = 0, -1, len(haystack)
        self.parsed_chains.clear()
        result = []
        for needle in needles:
            needle_len = len(needle)
            found_idx = find(haystack, lower(needle), prev_char_i)
            if found_idx > -1:
                prev_char_i = found_idx + needle_len
                str_trunc = StringTruncator(
                    self.haystack[found_idx:prev_char_i],
                    locked=True,
                    key_data=(found_idx, prev_char_i-1)
                )
                result.append(str_trunc)

        if not result:
            spacings = [StringTruncator(self.haystack, key_data=(0, hlen-1))]
        else:
            spacings = self._calc_spacings(self.haystack, result)
        result.extend(spacings)
        self.__parsed_chains = sorted(result, key=lambda str_trunc: str_trunc.key_data)

        return self

    def _compose_parsed_chains(self):
        result = []
        parsed_chains_len = len(self.__parsed_chains)
        for chain in self.__parsed_chains:
            if chain.locked:
                result.extend((str(self.wrapper_before), str(chain), str(self.wrapper_after)))
            else:
                if parsed_chains_len == 1:
                    chain.truncate_side = chain.TRUNCATE_RIGHT
                result.append(str(chain))
        return ''.join(result)

    def truncate(self):
        getattr(self, self.default_parser)()
        haystack_len = len(self.__haystack)
        if self.result_max_length < 0 or self.result_max_length >= haystack_len:
            return self._compose_parsed_chains()

        spaces, space_total_len, parsed_chains_num = ([], 0, len(self.__parsed_chains))
        for i, chain in enumerate(self.__parsed_chains):
            if not chain.locked:
                if i == 0:
                    chain.truncate_side = chain.TRUNCATE_LEFT
                elif i == parsed_chains_num - 1 :
                    chain.truncate_side = chain.TRUNCATE_RIGHT
                else:
                    chain.truncate_side = chain.TRUNCATE_MIDDLE
                spaces.append(chain)
                space_total_len += len(chain.text)

        truncate_len = haystack_len - self.result_max_length
        if truncate_len >= space_total_len:
            for space in spaces:
                space.max_length = 0
        else:
            percent_in_all = truncate_len / space_total_len
            for space in spaces:
                space.max_length -= int(percent_in_all * len(space.text))

        return self._compose_parsed_chains()

    def __str__(self) -> str:
        return self.truncate()


class FlexHTMLParserError(Exception):
    pass


class FlexHTMLStopParseError(Exception):
    """
    This exception is using as as indicator only in FlexHTMLParser.feed and
    FlexHTMLParser.close and only for one purpose -
    to stop parsing process when FlexHTMLParser.current_plain_text_length
    has reached a limit that defined in FlexHTMLParser.max_plain_text_length
    """
    pass


class HTMLTruncator(HTMLParser):
    """
    This class is mix of HTMLParser and BaseHTMLElement.
    One main purpose is limit a plain text content to a specified number of characters
    without violating the HTML integrity. For example, if you have some HTML tags in the text
    <div class="some classes">Some <strong>text</strong> which you <span>need</span> truncate into certain length</div>
    and you need to take 15 chars then the result will look like
    <div class="some classes">Some <strong>text</strong> which</div>.
    Length of 'Some text which' is 15 chars.

    Attention: because handle_data executes right after handle_starttag for next tag
    if parsing stopped due max_plain_text_length was reached then self.current_element
    (last element in elements tree) will be empty.
    To clear this case, likely we should be remove current_element from element tree
    but it will violence class data integrity.
    Of cause It could be manually do but simpler way is to assign the
    self.current_element.tag empty string. This is what we will do in __str__ method.
    """

    def __init__(self, max_plain_text_length=0, *, convert_charrefs=True):
        self.__root: NamedHTMLElement = NamedHTMLElement(element_name='root')
        self.__current: NamedHTMLElement = self.__root
        self.__max_plain_text_length = int(max_plain_text_length)
        self.__current_plain_text_length = 0
        self.__ellipsis: NamedHTMLElement = NamedHTMLElement(element_name='ellipsis')
        super().__init__(convert_charrefs=convert_charrefs)

    def __str__(self) -> str:
        current_tag = self.__current.tag
        if self.is_truncated:
            self.__current.tag = ''

        result = str(self.__root)
        self.__current.tag = current_tag
        return result

    @property
    def ellipsis(self):
        return self.__ellipsis

    @property
    def max_plain_text_length(self):
        return self.__max_plain_text_length

    @max_plain_text_length.setter
    def max_plain_text_length(self, value):
        self.__max_plain_text_length = int(value)

    @property
    def current_plain_text_length(self):
        return self.__current_plain_text_length

    @property
    def is_truncated(self):
        rdlen = len(self.rawdata)
        return 0 < rdlen > self.max_plain_text_length == self.current_plain_text_length

    @property
    def text(self):
        result = []

        def element_walker(element: BaseHTMLElement):
            for eld in element.data_as_list():
                if not isinstance(eld, BaseHTMLElement):
                    result.append(str(eld))
                else:
                    element_walker(eld)

        element_walker(self.root_element)
        return ''.join(result)

    @property
    def current_element(self) -> NamedHTMLElement:
        return self.__current

    @property
    def root_element(self) -> NamedHTMLElement:
        return self.__root

    def reset(self):
        super().reset()
        self.__current = self.__root
        self.__root.data = None
        self.__current_plain_text_length = 0

    def error(self, message):
        raise FlexHTMLParserError(message, self.getpos())

    def feed(self, data):
        try:
            super().feed(data)
        except FlexHTMLStopParseError as err:
            pass  # self.current_plain_text_length has reached a limit defined in self.max_plain_text_length
        return self

    def close(self):
        try:
            super().close()
        except FlexHTMLStopParseError as err:
            pass  # self.current_plain_text_length has reached a limit defined in self.max_plain_text_length
        return self

    def _get_necessary_copy_length(self, data):
        copy_len = len(data) # by default we will copy all data
        if self.__max_plain_text_length > 0:
            # case when we need make some calculation
            max_copy_len = self.__max_plain_text_length - self.__current_plain_text_length
            if max_copy_len <= 0:
                raise FlexHTMLStopParseError('It is no longer necessary to parse the string.')
            copy_len = min(max_copy_len, copy_len)
        return copy_len

    @staticmethod
    def strip_redundant_space(data: str, strip_right=True):
        """
        This function / method removes extra space at the ends of a string 
        if there is more than one space character in it.
        'strip_right' defines the side where it will be.

        :param data: source data string 
        :param strip_right: bool value that specify a direction, if True then 
         trailing extra spaces will be removed, otherwise leading extra spaces 
        :return: result data string
        """
        dlen = len(data)
        if dlen < 1:
            return ''

        strip_func = str.lstrip
        if bool(strip_right):
            strip_func = str.rstrip

        cdata = strip_func(data)
        cdlen = len(cdata)
        if cdlen < 1:
            return ''

        if dlen - cdlen > 1:
            if bool(strip_right):
                data = cdata+' '
            else:
                data = ' '+cdata

        return data

    def handle_data(self, data):
        data = self.strip_redundant_space(self.strip_redundant_space(data, True), False)
        if data:
            copy_len = self._get_necessary_copy_length(data)
            self.__current_plain_text_length += copy_len
            self.current_element.add_data(data[:copy_len])
            if copy_len < len(data):
                self.current_element.add_data(self.ellipsis)

    def handle_starttag(self, tag, attrs):
        cur_el = self.current_element
        if cur_el is None:
            raise FlexHTMLParserError('Internal error: current element is None. Possible, error of code logic.')

        el: NamedHTMLElement = type(cur_el)(tag=tag, attrs=attrs)
        cur_el.add_data(el)
        self.__current = el

    def handle_endtag(self, tag):
        self.__current = self.current_element.parent

    def __char_entity_ref_handler(self, name, is_char=True):
        # each time name is represent one char, therefore we can use any one char
        # for recalculation copy length and increment processed length on 1
        data = ' '
        copy_len = self._get_necessary_copy_length(data)
        self.__current_plain_text_length += copy_len
        char = ''
        if bool(is_char):
            char = '#'
        self.current_element.add_data(unescape(''.join(['&', char, name, ';'])))
        if copy_len < len(data):
            self.current_element.add_data(self.ellipsis)

    def handle_charref(self, name):
        """
        This handler is necessary only if convert_charrefs is False
        """
        # name is only numeric representation of special char
        self.__char_entity_ref_handler(name, True)

    def handle_entityref(self, name):
        """
        This handler is necessary only if convert_charrefs is False
        """
        # name is only html entity representation of special char
        self.__char_entity_ref_handler(name, False)
