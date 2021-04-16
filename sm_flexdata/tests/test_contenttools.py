# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2021 Apr 09 at 22:53 
# Description of <test_contenttools>
#
from unittest import TestCase
from ..html.contenttools import HTMLTruncator, StringTruncator, TextTruncator


# @author Semyon Mamonov <semyon.mamonov@gmail.com>
class TestHTMLTruncator(TestCase):

    def setUp(self) -> None:
        self.test_html = r"""
<div class="col-9 body_content">

<article class="card" data-entry-id="102769" data-entry-url="">
    <section class="card-title entry-info">
        Блог: <a href="/blog/public/index/blog/583/?text=1" class="entry-blog">Heineken</a>
        Автор: <a href="/blog/public/index/author/1451/?text=1" class="entry-author">Wendy Vasquez</a>
        Соавторы: <span>-----</span>
        <span class="entry-published">published: Feb. 25, 2021</span>
        
    </section>
    <header class="card-header entry-headline">Let environment green need interview center break.
Account share water figure term your help. Fish the still. Century hundred sense sing pretty politics push. Deep admit shoulder adult tough ask.
Man other us.</header>
    
    <section class="card-body entry-text">
        

        
        <div class="body-text">
        
        <pre>
<code class="language-python">@requires_authorization(roles=["ADMIN"])
def somefunc(param1='', param2=0):
    r'''A docstring'''
    if param1 &gt; param2: # interesting
        print 'Gre\'ater'
    return (param2 - param1 + 1 + 0b10l) or None

class SomeClass:
    pass

&gt;&gt;&gt; message = '''interpreter
... prompt'''</code></pre>

<p>Black young garden economic. See society speak summer ten. <strong>Car whatever course million main</strong>. This summer he question billion city sport. Ball activity skill.</p>
        
        </div>
        
        
    </section>
    
    
</article>



</div>
"""

    def test_feed(self):

        # main test
        max_text_len = 250
        fparser = HTMLTruncator(max_text_len)
        fparser.feed(self.test_html)
        all_elements = []
        fparser.root_element.get_elements_by(all_elements, comparer=lambda el, val: True)
        total_len = 0
        for el in all_elements:
            for data in el.data_as_list():
                if isinstance(data, str):
                    total_len += len(data)
        self.assertEqual(max_text_len, total_len)
        self.assertTrue(fparser.is_truncated)

        # test is_truncated property when max_plain_text_length more than data
        fparser.reset()
        fparser.max_plain_text_length = max_text_len * 4
        fparser.feed(self.test_html)
        self.assertFalse(fparser.is_truncated)

        # test truncated data for classic case
        fparser.reset()
        fparser.max_plain_text_length = 15
        fparser.feed(
            r'<div class="some classes">Some <strong>te</strong>xt which you <span>need</span> truncate <b>into</b> certain length</div>'
        )
        self.assertEqual(r'Some text which', fparser.text)
        self.assertEqual(r'<div class="some classes">Some <strong>te</strong>xt which</div>', str(fparser))

        # test truncated data that start from plain text and finish by tag
        fparser.reset()
        fparser.max_plain_text_length = 53
        fparser.feed(
            r'Some <strong>te</strong>xt which you <span>need</span> to truncate <b>into</b> certain length<div class="some classes">Last div</div>'
        )
        self.assertEqual(r'Some text which you need to truncate into certain len', fparser.text)
        self.assertEqual(r'Some <strong>te</strong>xt which you <span>need</span> to truncate <b>into</b> certain len',
                         str(fparser))

        # test parsing all data
        fparser.reset()
        fparser.max_plain_text_length = 0
        data = 'Some <strong>te</strong>xt which you <span>need</span> to truncate <b>into</b> certain length<div class="some classes"> with last div</div>'
        fparser.feed(data)
        self.assertEqual(r'Some text which you need to truncate into certain length with last div', fparser.text)
        self.assertEqual(data, str(fparser))


class TestStringTruncator(TestCase):

    def setUp(self):
        self.test_string = '123456789abcdef'
        self.truncator = StringTruncator(self.test_string)

    def test_truncate(self):
        self.assertEqual(self.test_string, str(self.truncator))

        self.truncator.max_length = 5
        self.truncator.truncate_side = self.truncator.TRUNCATE_RIGHT
        self.assertEqual('12345...', str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_LEFT
        self.assertEqual('...bcdef', str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_MIDDLE
        self.assertEqual('12...def', str(self.truncator))

        self.truncator.locked = True
        self.assertEqual(self.test_string, str(self.truncator))
        self.truncator.locked = False

        self.truncator.max_length = 1
        self.truncator.truncate_side = self.truncator.TRUNCATE_RIGHT
        self.assertEqual('1...', str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_LEFT
        self.assertEqual('...f', str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_MIDDLE
        self.assertEqual('1...', str(self.truncator))

        self.truncator.max_length = 0
        self.truncator.truncate_side = self.truncator.TRUNCATE_RIGHT
        self.assertEqual('...', str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_LEFT
        self.assertEqual('...', str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_MIDDLE
        self.assertEqual('...', str(self.truncator))

        self.truncator.max_length = 15
        self.truncator.truncate_side = self.truncator.TRUNCATE_RIGHT
        self.assertEqual(self.test_string, str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_LEFT
        self.assertEqual(self.test_string, str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_MIDDLE
        self.assertEqual(self.test_string, str(self.truncator))

        self.truncator.max_length = 25
        self.truncator.truncate_side = self.truncator.TRUNCATE_RIGHT
        self.assertEqual(self.test_string, str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_LEFT
        self.assertEqual(self.test_string, str(self.truncator))
        self.truncator.truncate_side = self.truncator.TRUNCATE_MIDDLE
        self.assertEqual(self.test_string, str(self.truncator))


class TestTextTruncator(TestCase):

    def setUp(self):
        self.test_string = '123456789 QwErTyUiOp AsDfGhJkL ZxCvBnM'
        self.needles = ('4567', 'UiOp', 'hJkL Zx')
        self.result_parsed_chains = [
            StringTruncator('123', truncate_side=StringTruncator.TRUNCATE_LEFT, key_data=(0, 2)),
            StringTruncator('4567', locked=True, key_data=(3, 6)),
            StringTruncator('89 QwErTy', truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(7, 15)),
            StringTruncator('UiOp', locked=True, key_data=(16, 19)),
            StringTruncator(' AsDfG', truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(20, 25)),
            StringTruncator('hJkL Zx', locked=True, key_data=(26, 32)),
            StringTruncator('CvBnM', truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(33, 37)),
        ]

        self.text_truncator = TextTruncator(self.test_string, self.needles)

    def test_needles(self):
        self.text_truncator.needles = self.needles
        self.assertTupleEqual(self.needles, self.text_truncator.needles)

    def test_haystack(self):
        self.text_truncator.haystack = self.test_string
        self.assertEqual(self.test_string, self.text_truncator.haystack)

    def test_parsed_chains(self):
        self.text_truncator.result_max_length = -1
        result_chains = self.result_parsed_chains
        self.text_truncator.parse_each_after_other_once(self.test_string, self.needles)
        self.assertEqual(len(result_chains), len(self.text_truncator.parsed_chains))
        for i, chain in enumerate(result_chains):
            self.assertEqual(str(chain), str(self.text_truncator.parsed_chains[i]))

        # test where one of needles not found self.needles = ['4567', 'UiOpyy', 'hJkL Zx']
        result_chains = [
            StringTruncator('123', truncate_side=StringTruncator.TRUNCATE_LEFT, key_data=(0, 2)),
            StringTruncator('4567', locked=True, key_data=(3, 6)),
            StringTruncator('89 QwErTyUiOp AsDfG', truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(7, 25)),
            StringTruncator('hJkL Zx', locked=True, key_data=(26, 32)),
            StringTruncator('CvBnM', truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(33, 37)),
        ]

        needles = [*self.needles]
        needles[1] = needles[1]+'yy'
        self.text_truncator.parse_each_after_other_once(self.test_string, needles)

        self.assertEqual(len(result_chains), len(self.text_truncator.parsed_chains))
        for i, chain in enumerate(result_chains):
            self.assertEqual(str(chain), str(self.text_truncator.parsed_chains[i]))

        # test where no one of needles found self.needles = ['4567uu', 'UiOpyy', 'hJkL Zxoo']
        result_chains = [
            StringTruncator(self.test_string, truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(0, 37)),
        ]

        needles = ['4567uu', 'UiOpyy', 'hJkL Zxoo']
        self.text_truncator.parse_each_after_other_once(self.test_string, needles)

        self.assertEqual(len(result_chains), len(self.text_truncator.parsed_chains))
        for i, chain in enumerate(result_chains):
            self.assertEqual(str(chain), str(self.text_truncator.parsed_chains[i]))

        # test for bordered case needles = ['123', 'CvBnM']
        result_chains = [
            StringTruncator('123', truncate_side=StringTruncator.TRUNCATE_LEFT, key_data=(0, 2)),
            StringTruncator('456789 QwErTyUiOp AsDfGhJkL Zx', truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(3, 32)),
            StringTruncator('CvBnM', truncate_side=StringTruncator.TRUNCATE_MIDDLE, key_data=(33, 37)),
        ]
        needles = ['123', 'CvBnM']
        self.text_truncator.parse_each_after_other_once(self.test_string, needles)

        self.assertEqual(len(result_chains), len(self.text_truncator.parsed_chains))
        for i, chain in enumerate(result_chains):
            self.assertEqual(str(chain), str(self.text_truncator.parsed_chains[i]))

    def test__compose_parsed_chains(self):
        self.text_truncator.result_max_length = -1
        wraper_start = type(self.text_truncator).wrapper_before
        wraper_end = type(self.text_truncator).wrapper_after
        test_str = '123456789AbCdEf'
        needles = ['456','bC']
        result_str = '123%s456%s789A%sbC%sdEf' % (wraper_start, wraper_end, wraper_start, wraper_end)

        self.text_truncator.parse_each_after_other_once(test_str, needles)
        self.assertEqual(result_str, self.text_truncator._compose_parsed_chains())


    def test_truncate(self):
        self.text_truncator.haystack = self.test_string
        self.text_truncator.needles = self.needles

        # result can have more than 25 original chars cause the removing is proportional
        # and rounding to the floor is the cause of this effect
        self.text_truncator.result_max_length = 25
        test_string = '...23<span class="found-text">4567</span>89...Ty<span class="found-text">UiOp</span> A...G<span class="found-text">hJkL Zx</span>CvB...'
        self.assertEqual(test_string, self.text_truncator.truncate())

        self.text_truncator.result_max_length = 100
        test_string = '123<span class="found-text">4567</span>89 QwErTy<span class="found-text">UiOp</span> AsDfG<span class="found-text">hJkL Zx</span>CvBnM'
        self.assertEqual(test_string, self.text_truncator.truncate())
        self.text_truncator.result_max_length = -1
        self.assertEqual(test_string, self.text_truncator.truncate())

        self.text_truncator.result_max_length = 0
        test_string = '...<span class="found-text">4567</span>...<span class="found-text">UiOp</span>...<span class="found-text">hJkL Zx</span>...'
        self.assertEqual(test_string, self.text_truncator.truncate())

