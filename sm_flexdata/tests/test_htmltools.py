# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2020 Dec 20 at 12:35 
# Description of <test_htmltools>
#
from unittest import TestCase
from ..core.htmltools import HTMLComparer, Tag


# @author Semyon Mamonov <semyon.mamonov@gmail.com>
class TestHTMLComparer(TestCase):

    def setUp(self) -> None:
        self.html_comparer = HTMLComparer()

    def test_isequal(self):
        test_src1 = '<th><label for="id_input">Input:</label></th><td>' \
                    '<input type="text" name="input" maxlength="10" id="id_input" required></td>'
        test_src2 = '<th><label for="id_input">Input:</label></th><td>' \
                    '<input type="text" name="input" maxlength="10" required id="id_input"/></td>'
        self.assertTrue(self.html_comparer.isequal(test_src1, test_src2),
                        'From an HTML point of view these 2 strings are not equal.')

    def test_parse_and_clean(self):
        test_src_str = """<th><label>Select:</label></th><td><ul id="id_select">
    <li><label for="id_select_0"><input type="checkbox" name="select" value="yes" id="id_select_0">
 Yes displayed</label>

</li>
    <li><label for="id_select_1"><input type="checkbox" name="select" value="no" id="id_select_1">
 No displayed</label>

</li>
</ul></td>"""
        test_res_str = '<th><label>Select:</label></th><td><ul id="id_select"><li><label for="id_select_0">' \
                       '<input type="checkbox" name="select" value="yes" id="id_select_0" />Yes displayed</label>' \
                       '</li><li><label for="id_select_1">' \
                       '<input type="checkbox" name="select" value="no" id="id_select_1" />No displayed</label>' \
                       '</li></ul></td>'
        parsed, cleaned = self.html_comparer.parse_and_clean(test_src_str)
        self.assertEqual(test_res_str, cleaned)

    def test_get_diff(self):
        test_src1 = '<th><label for="id_input">Input:</label></th><td>' \
                    '<input type="text" name="input" maxlength="10" id="id_input" required></td>'
        test_src2 = '<th><label for="id_input">Input:</label></th><td>' \
                    '<input type="text" name="input" maxlength="105" required id="id_input"/></td>'
        difs_struct = self.html_comparer.get_diff(test_src1, test_src2)
        comp_str = '"<input type="text" name="input" maxlength="10" id="id_input" required />" != '\
                   '"<input type="text" name="input" maxlength="105" required id="id_input" />"'
        self.assertEqual(comp_str,difs_struct.diffs[0])


class TestTag(TestCase):

    def setUp(self) -> None:
        self.test_src1 = '<th><label for="id_input">Input:</label></th><td>' \
                         '<input type="text" name="input" maxlength="10" id="id_input" required></td>'
        self.test_src2 = '<th><label for="id_input">Input:</label></th><td>' \
                         '<input type="text" name="input" maxlength="10" required id="id_input"/></td>'

    def test_compose(self):
        res_str = '<tr name="somename" class="class_yyy yyyyy" required>'
        tag = Tag(tag='tr', attrs=[('name', 'somename'), ('class', 'class_yyy yyyyy'), ('required', None)],
                  isstart=True)
        self.assertEqual(res_str, str(tag))
        res_str = '<input nam&gt;e="somename" class="class_yyy yyyyy" required />'
        tag = Tag(tag='input', attrs=[('nam>e', 'somename'), ('class', 'class_yyy yyyyy'), ('required', None)],
                  isstart=True)
        self.assertEqual(res_str, str(tag))
        res_str = '<tr>'
        tag = Tag(tag='tr', attrs=[], isstart=True)
        self.assertEqual(res_str, str(tag))
        res_str = '</tr>'
        tag = Tag(tag='tr', attrs=[('required', None)], isstart=False)
        self.assertEqual(res_str, str(tag))
        res_str = ''
        tag = Tag(tag='input', attrs=[('required', None)], isstart=False)
        self.assertEqual(res_str, str(tag))

    def test__compare_attrs(self):
        res_str2 = '<input type="text" name="input" maxlength="10" id="id_input" required />'
        res_str1 = '<input type="text" name="input" maxlength="10" required id="id_input" />'
        tag1 = Tag(tag='input', attrs=[
            ('type', "text"), ('name', "input"), ('maxlength', "10"), ('required', None), ('id', "id_input")
        ])
        self.assertEqual(str(tag1), res_str1)
        tag2 = Tag(tag='input', attrs=[
            ('type', "text"), ('name', "input"), ('maxlength', "10"), ('id', "id_input"), ('required', None)
        ])
        self.assertEqual(str(tag2), res_str2)
        self.assertEqual(tag1, tag2)
        self.assertNotEqual(res_str1, res_str2)
