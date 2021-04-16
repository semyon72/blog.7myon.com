# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2020 Dec 18 at 17:23 
# Description of <test_html_form_elements>
#
import datetime
from functools import cached_property

from unittest import TestCase
import django.forms as forms

from ..html.form_elements import *
from ..core.htmltools import isequal_as_html


def _get_test_form_class(parent, all_are_hidden = False, extra_fields = None):

    # next lines work but if to try dynamically to change widget
    # like - for fn, field in form.fields.items(): field.widget = forms.HiddenInput
    # it raises TypeError: value_from_datadict() missing 1 required positional argument: 'name'
    # looks like bug
    kwargs = {'max_length': 15, 'help_text': 'INPUT_HELP_TEXT'}
    if all_are_hidden:
        kwargs['widget'] = forms.HiddenInput
    input_field = forms.CharField(**kwargs)

    kwargs = {'initial': datetime.date.today(), 'help_text': 'DATE_HELP_TEXT'}
    if all_are_hidden:
        kwargs['widget'] = forms.HiddenInput
    date_field = forms.DateField(**kwargs)

    fields = {
        'input': input_field,
        'date': date_field,
        'hidden_input': forms.CharField(
            initial='HIDDEN_INITIAL_VALUE',
            help_text='HIDDEN_INPUT_HELP_TEXT',
            # show_hidden_initial=True,
            widget=forms.HiddenInput,
        ),
    }
    if extra_fields and isinstance(extra_fields, dict):
        fields.update(extra_fields)

    return type('TestForm', (parent,), fields)


SimpleFormForTests = _get_test_form_class(Form)
SimpleFlexFormForTests = _get_test_form_class(FlexForm)

class ComplexFormForTests(forms.Form):
    # Form parameters #######
    # data = None, files = None, auto_id = 'id_%s', prefix = None, initial = None,
    # error_class = ErrorList, label_suffix = None, empty_permitted = False,
    # field_order = None, use_required_attribute = None, renderer = None

    # Field parameters #######
    # required = True, widget = None, label = None, initial = None,
    # help_text = '', error_messages = None, show_hidden_initial = False,
    # validators = (), localize = False, disabled = False, label_suffix = None

    # Widget parameters
    # attrs=None

    input = forms.CharField(max_length=20)
    email = forms.EmailField()
    date = forms.DateField()
    select = forms.MultipleChoiceField(choices=(('yes', 'Yes displayed'), ('no', 'No displayed')),
                                       widget=forms.CheckboxSelectMultiple)
    checkbox = forms.ChoiceField(choices=(('chb1', 'Checkbox #1'), ('chb2', 'Checkbox #2')))
    radio = forms.ChoiceField(choices=(('rb1', 'Radiobutton #1'), ('rb2', 'Radiobutton #2')), widget=forms.RadioSelect)


# @author Semyon Mamonov <semyon.mamonov@gmail.com>
class TestDefaultFormElement(TestCase):

    def setUp(self) -> None:
        self.form_element = DefaultFormElement()

    @cached_property
    def _get_test_data(self):
        return OrderedDict({
            FormFieldLabel: {'table': '<th></th>', 'ul': '', 'dl': '<dt></dt>', 'p': ''},
            FormFieldData: {'table': '<td></td>', 'ul': '', 'dl': '<dd></dd>', 'p': ''},
            FormField: {'table': '<th></th><td></td>', 'ul': '', 'dl': '<dt></dt><dd></dd>', 'p': ''},
            FormRow: {
                'table': '<tr><th></th><td></td></tr>',
                'ul': '<li></li>',
                'dl': '<dt></dt><dd></dd>',
                'p': '<p></p>'},
            FormGroup: {
                'table': '<table border="0"><tr><th></th><td></td></tr></table>',
                'ul': '<ul><li></li></ul>',
                'dl': '<dl><dt></dt><dd></dd></dl>',
                'p': '<p><p></p></p>'},
        })

    def test_set_default_render_as(self):
        fe = self.form_element
        # default -> ''
        self.assertEqual(str(fe), '')
        for elType, prms in self._get_test_data.items():
            for _as, resstr in prms.items():
                elType.set_default_render_as(_as)
                obj = elType()
                if isinstance(obj, (FormFieldData, FormFieldLabel)):
                    self.assertEqual(resstr, str(obj))
                    continue

                if isinstance(obj, (FormField,)):
                    obj.data = (FormFieldLabel(), FormFieldData())
                    self.assertEqual(resstr, str(obj))
                    continue

                if isinstance(obj, (FormRow,)):
                    ff = FormField()
                    ff.data = (FormFieldLabel(), FormFieldData())
                    obj.data = ff
                    self.assertEqual(resstr, str(obj))
                    continue

                if isinstance(obj, (FormGroup,)):
                    ff = FormField()
                    ff.data = (FormFieldLabel(), FormFieldData())
                    fr = FormRow()
                    fr.data = ff
                    obj.data = fr
                    self.assertEqual(resstr, str(obj))
                    continue


class TestFormFieldLabel(TestCase):

    def setUp(self) -> None:
        self.form = ComplexFormForTests()

    def test_set_from(self):
        test_results = {
            'table': '<th>%s</th>',
            'ul': '%s',
            'p': '%s',
            'dl': '<dt>%s</dt>',
            'bootstrap4': '%s'
        }

        f = self.form
        for render_as in DEFAULT_CONFIG_DATA:
            FormFieldLabel.set_default_render_as(render_as)
            ffl = FormFieldLabel()
            for bf in f:
                ffl.set_from(bf)
                self.assertEqual('field_%s_label' % bf.name, ffl.element_name)
                self.assertEqual(bf.name, ffl.original_name)
                self.assertEqual(test_results[render_as] % bf.label_tag(), str(ffl))


class TestFormFieldData(TestCase):

    def setUp(self) -> None:
        self.form = ComplexFormForTests()

    def test_set_from(self):
        test_results = {
            'table': '<td>%s</td>',
            'ul': '%s',
            'p': '%s',
            'dl': '<dd>%s</dd>',
            'bootstrap4': '%s'
        }

        f = self.form
        for render_as in DEFAULT_CONFIG_DATA:
            FormFieldData.set_default_render_as(render_as)
            ffl = FormFieldData()
            for bf in f:
                ffl.set_from(bf)
                self.assertEqual('field_%s_data' % bf.name, ffl.element_name)
                self.assertEqual(bf.name, ffl.original_name)
                self.assertEqual(test_results[render_as] % str(bf), str(ffl))


class TestFormField(TestCase):

    def setUp(self) -> None:
        self.form = ComplexFormForTests()
        self.simple_form = SimpleFormForTests()
        self.test_results = {
            'table': '<th>{0}</th><td>{1}</td>',
            'ul': '{0}{1}',
            'p': '{0}{1}',
            'dl': '<dt>{0}</dt><dd>{1}</dd>',
            'bootstrap4': '{0}{1}'
        }

    def test_set_from_only_structure(self):
        # simple test (just formatting of th, td ....) for complex form
        f = self.form
        for render_as in DEFAULT_CONFIG_DATA:
            FormField.set_default_render_as(render_as)
            ff = FormField()
            for bf in f:
                ff.set_from(bf)
                self.assertEqual(bf.name, ff.original_name)
                self.assertEqual('field_%s' % bf.name, ff.element_name)
                # self.assertEqual(
                #   set(test_results[render_as].format(bf.label_tag(), str(bf)).split(' ')),
                #   set(str(ffl).split(' '))
                # )
                # direct comparison of results does not work because in practice it can give next results
                # '<th>[58 chars]text" name="input" maxlength="10" required id="id_input"/></td>'
                # !=
                # '<th>[58 chars]text" name="input" maxlength="10" id="id_input" required></td>'
                # this is good from HTML point of view but not comparable
                str2 = str(ff)
                str1 = self.test_results[render_as].format(bf.label_tag(), str(bf))
                self.assertTrue(
                    isequal_as_html(str1, str2),
                    'From an HTML point of view {0} and {1} these strings are not equal.'.format(str1, str2)
                )

    def _test_set_form_with_hidden_help_text_errors(self, form_data):
        # TODO: Need to understanding how happens a rendering if show initial hidden is True.
        #  Now, probably, this case is not tested.
        sf = self.simple_form
        sf.data = form_data
        sf.is_bound = True
        sf._errors = None
        sf.is_valid()
        for render_as in DEFAULT_CONFIG_DATA:
            FormField.set_default_render_as(render_as)
            ff = FormField()
            for bf in sf:
                ff.set_from(bf)
                str1 = ''
                if not bf.is_hidden:
                    str1 = self.test_results[render_as].format(
                        bf.label_tag(),
                        '{0}{1}{2}'.format(
                            str(bf.errors), str(bf),
                            '<br/><span class="helptext">{0}</span>'.format(bf.help_text) if bf.help_text else ''
                        )
                    )
                self.assertEqual(str1, str(ff))

    def test_set_from_with_hidden_help_text(self):
        # complex test for simple form (help_text, rendering of hidden, rendering show initial hidden)
        now_date = datetime.date.today()
        form_data = {'input': 'input data', 'date': now_date, 'hidden_input': 'hidden input data'}
        self._test_set_form_with_hidden_help_text_errors(form_data)

    def test_set_from_with_errors(self):
        # complex test for simple form (help_text, rendering of hidden, rendering show initial hidden)
        form_data = {
            'input': 'input data 1234567890 More than 15 chars',
            'date': 'Wrong Date',
            'hidden_input': 'hidden input data'}
        self._test_set_form_with_hidden_help_text_errors(form_data)


def _get_test_result_for_row(render_as, bound_fields):
    test_results = {
        'table': ('<tr>{fields}</tr>', '<th>{label}</th><td>{data}</td>'),
        'ul': ('<li>{fields}</li>', '{label}{data}'),
        'p': ('<p>{fields}</p>', '{label}{data}'),
        'dl': ('{fields}', '<dt>{label}</dt><dd>{data}</dd>'),
        'bootstrap4': ('{fields}', '{label}{data}'),
    }

    if isinstance(bound_fields, BoundField):
        bound_fields = [bound_fields]
    fields = ''.join(
        test_results[render_as][1].format(**label_and_data) for label_and_data in
        ({'label': bf.label_tag(), 'data': str(bf)} for bf in bound_fields)
    )
    return test_results[render_as][0].format(fields=fields)


class TestFormRow(TestCase):

    def setUp(self) -> None:
        self.form = ComplexFormForTests()

    def test_set_from(self):
        f = self.form
        bfs = [bf for bf in f]
        ffr = FormRow().set_from(bfs)
        self.assertEqual(len(bfs), len(ffr.field_names))

        for render_as in DEFAULT_CONFIG_DATA:
            FormRow.set_default_render_as(render_as)
            ffr = FormRow().set_from(bfs)
            original_name = str(id(ffr))
            self.assertEqual('row_%s' % original_name, ffr.element_name)
            self.assertEqual(original_name, ffr.original_name)
            self.assertEqual(_get_test_result_for_row(render_as, bfs), str(ffr))

        # test - when used generator for bounded fields (no real gotten bounded fields)
        with self.assertRaises(TypeError):
            FormRow().set_from((bf for bf in f))


class TestFormGroup(TestCase):

    def setUp(self) -> None:
        self.form = ComplexFormForTests()

    def test_set_from(self):
        f = self.form

        # test default form
        FormGroup.set_default_render_as('table')
        form_group = FormGroup().set_from(f)
        form_group.tag = ''
        str1 = str(f)
        str2 = str(form_group)
        self.assertTrue(
            isequal_as_html(str1, str2),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(str1, str2)
        )

        # test initialized default form
        f.data = {
            'input': 'input content', 'email': 'email@email.com',
            'date': '2020-02-20', 'checkbox': 'chb1', 'radio': 'rb1', 'select': ['yes']
        }
        f.is_bound, f._errors = True, None
        f.is_valid()
        str1 = str(f)
        str2 = str(form_group)
        self.assertTrue(
            isequal_as_html(str1, str2),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(str1, str2)
        )

        # test not base case but in all representations
        f.data = {}
        f.is_bound, f._errors = False, None

        for render_as in DEFAULT_CONFIG_DATA:
            FormRow.set_default_render_as(render_as)

            bfsg = [[f['input'], f['email']], f['date'], [f['select'], f['checkbox']], f['radio']]
            ffg = FormGroup().set_from(bfsg)
            ffg.tag = ''

            # issue with multi fields row
            test_res = []
            for bfs in bfsg:
                test_res.append(_get_test_result_for_row(render_as, bfs))

            str1 = ''.join(test_res)
            str2 = str(ffg)
            self.assertTrue(
                isequal_as_html(str1, str2),
                'From the HTML point of view {0} and {1} these strings are not equal.'.format(str1, str2)
            )


class TestFormFieldDataErrors(TestCase):

    def setUp(self) -> None:
        self.test_form = SimpleFormForTests({'input': "eroroororororoorororororo"})

    def test_set_from(self):
        FormFieldDataHelpText.set_default_render_as()
        bf = self.test_form['input']
        ffde = FormFieldDataErrors().set_from(bf)
        self.assertEqual(str(bf.errors), str(ffde))


class TestFormFieldDataHelpText(TestCase):

    def setUp(self) -> None:
        self.test_form = SimpleFormForTests({'input': "eroroororororoorororororo"})

    def test_set_from(self):
        FormFieldDataHelpText.set_default_render_as()
        bf = self.test_form['input']
        ffdht = FormFieldDataHelpText().set_from(bf)
        # Expected string depends from form_elements.DEFAULT_CONFIG_DATA....FormFieldDataHelpText
        # but <br/> is hard coded inside FormFieldDataHelpText.prefix_html_content class attribute
        self.assertEqual('<br/><span class="helptext">%s</span>' % str(bf.help_text), str(ffdht))


class TestMixedFormElements(TestCase):

    def test_mixed_form_elements(self):
        FormGroup.set_default_render_as('table')

        attrs = {'colspan': '2'}
        str_data = 'somethng safe'
        expect_str = '<tr><td colspan="2">{}</td></tr>'.format(str_data)
        actual_row = FormRow(data=NamedHTMLElement(tag='td', data=mark_safe(str_data), attrs=attrs))
        self.assertEqual(expect_str, str(actual_row))
        actual_row.visible = False
        self.assertEqual('', str(actual_row))

        actual_row = FormRow(data=FormFieldData(data=mark_safe(str_data), attrs=attrs))
        self.assertEqual(expect_str, str(actual_row))

        actual_row = FormRow(data=FormField(data=FormFieldData(data=mark_safe(str_data), attrs=attrs)))
        self.assertEqual(expect_str, str(actual_row))


class TestFlexForm(TestCase):

    def _test_as(self, _as = 'table'):

        method_name = 'as_'+_as

        # test empty form
        flexform = SimpleFlexFormForTests()
        testform = SimpleFormForTests()

        flexform_str = str(getattr(flexform,method_name)())
        testform_str = str(getattr(testform,method_name)())
        self.assertTrue(
            isequal_as_html(testform_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(testform_str, flexform_str)
        )

        # test not all data are hidden and has no errors
        data = {'input': 'input DATA', 'date': datetime.date.today(), 'hidden_input': 'HIDDEN DATA'}
        initial = {'input': 'initial input', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        flexform = SimpleFlexFormForTests(data, initial=initial)
        testform = SimpleFormForTests(data, initial=initial)

        flexform_str = str(getattr(flexform,method_name)())
        testform_str = str(getattr(testform,method_name)())
        self.assertTrue(
            isequal_as_html(testform_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(testform_str, flexform_str)
        )

        # test not all data are hidden and has errors
        data = {'input': 'input DATA', 'date': 'Wrong DATE_DATA'}
        initial = {'input': 'initial input content', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        flexform = SimpleFlexFormForTests(data, initial=initial)
        testform = SimpleFormForTests(data, initial=initial)

        flexform_str = str(getattr(flexform,method_name)())
        testform_str = str(getattr(testform,method_name)())
        self.assertTrue(
            isequal_as_html(testform_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(testform_str, flexform_str)
        )

        # test all data are hidden and errors
        testform = _get_test_form_class(Form, True)(data, initial=initial)
        flexform = _get_test_form_class(FlexForm, True)(data, initial=initial)

        testform_str = str(getattr(testform,method_name)()).replace(' colspan="2"', '', 1)  # fixed the hardcoded difference
        flexform_str = str(getattr(flexform,method_name)())
        self.assertTrue(
            isequal_as_html(testform_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(testform_str, flexform_str)
        )

        # test all data are hidden and no errors
        data = {'input': 'input DATA', 'date': datetime.date.today(), 'hidden_input': 'HIDDEN DATA'}
        initial = {'input': 'initial input', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        testform = _get_test_form_class(Form, True)(data, initial=initial)
        flexform = _get_test_form_class(FlexForm, True)(data, initial=initial)

        testform_str = str(getattr(testform,method_name)())
        flexform_str = str(getattr(flexform,method_name)())
        self.assertTrue(
            isequal_as_html(testform_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(testform_str, flexform_str)
        )

    def test_as_table(self):
        self._test_as()

    def test_as_multifield_table(self):
        # test not all data are hidden and has errors
        data = {'input': 'input DATA', 'date': 'Wrong DATE_DATA', 'input_single': 'input single DATA' }
        initial = {'input': 'initial input content', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        extra_fields = {
            'input_single': forms.CharField(max_length=25, help_text='INPUT_SINGLE_HELP_TEXT')
        }
        multicolumn_flex_form_type = _get_test_form_class(FlexForm, extra_fields=extra_fields)

        flexform = multicolumn_flex_form_type(data, initial=initial)
        flexform_str = flexform.as_table([['input','date'], 'hidden_input', 'input_single'])
        result_test_str = '<tr><td colspan="4"><ul class="errorlist nonfield">'\
            '<li>(Hidden field hidden_input) This field is required.</li></ul></td></tr>'\
            '<tr><th><label for="id_input">Input:</label></th><td>'\
            '<input type="text" name="input" value="input DATA" maxlength="15" required id="id_input">'\
            '<br/><span class="helptext">INPUT_HELP_TEXT</span></td><th><label for="id_date">Date:</label>'\
            '</th><td><ul class="errorlist"><li>Enter a valid date.</li></ul>'\
            '<input type="date" name="date" value="Wrong DATE_DATA" required id="id_date">'\
            '<br/><span class="helptext">DATE_HELP_TEXT</span></td></tr><tr><th>'\
            '<label for="id_input_single">Input single:</label></th><td>'\
            '<input type="text" name="input_single" value="input single DATA" maxlength="25" '\
            'required id="id_input_single"><br/><span class="helptext">INPUT_SINGLE_HELP_TEXT</span>'\
            '<input type="hidden" name="hidden_input" id="id_hidden_input"></td>'\
            '<th>&nbsp;</th><td>&nbsp;</td></tr>'

        self.assertTrue(
            isequal_as_html(result_test_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(result_test_str, flexform_str)
        )

    def test_as_ul(self):
        self._test_as('ul')

    def test_as_p(self):
        self._test_as('p')

    def test_as_dl(self):
        method_name = 'as_dl'

        # test empty form
        flexform = SimpleFlexFormForTests()

        flexform_str = str(getattr(flexform,method_name)())
        result_test_str = '<dt><label for="id_input">Input:</label></dt>'\
        '<dd><input type="text" name="input" maxlength="15" required id="id_input">'\
        '<br/><span class="helptext">INPUT_HELP_TEXT</span></dd>'\
        '<dt><label for="id_date">Date:</label></dt>'\
        '<dd><input type="date" name="date" value="{0}" required id="id_date">'\
        '<br/><span class="helptext">DATE_HELP_TEXT</span>'\
        '<input type="hidden" name="hidden_input" value="HIDDEN_INITIAL_VALUE" id="id_hidden_input">'\
        '</dd>'.format(datetime.date.today())

        self.assertTrue(
            isequal_as_html(result_test_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(result_test_str, flexform_str)
        )

        # test not all data are hidden and has no errors
        data = {'input': 'input DATA', 'date': datetime.date.today(), 'hidden_input': 'HIDDEN DATA'}
        initial = {'input': 'initial input', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        flexform = SimpleFlexFormForTests(data, initial=initial)
        result_test_str = '<dt><label for="id_input">Input:</label></dt>'\
        '<dd><input type="text" name="input" value="input DATA" maxlength="15" required id="id_input">'\
        '<br/><span class="helptext">INPUT_HELP_TEXT</span></dd>'\
        '<dt><label for="id_date">Date:</label></dt>'\
        '<dd><input type="date" name="date" value="{0}" required id="id_date">'\
        '<br/><span class="helptext">DATE_HELP_TEXT</span>'\
        '<input type="hidden" name="hidden_input" value="HIDDEN DATA" id="id_hidden_input"></dd>'\
        .format(datetime.date.today())

        flexform_str = str(getattr(flexform,method_name)())
        self.assertTrue(
            isequal_as_html(result_test_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(result_test_str, flexform_str)
        )

        # test not all data are hidden and has errors
        data = {'input': 'input DATA', 'date': 'Wrong DATE_DATA'}
        initial = {'input': 'initial input content', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        flexform = SimpleFlexFormForTests(data, initial=initial)
        result_test_str = '<div><ul class="errorlist nonfield">'\
            '<li>(Hidden field hidden_input) This field is required.</li></ul></div>'\
            '<dt><label for="id_input">Input:</label></dt><dd>'\
            '<input type="text" name="input" value="input DATA" maxlength="15" required id="id_input">'\
            '<br/><span class="helptext">INPUT_HELP_TEXT</span></dd>'\
            '<dt><label for="id_date">Date:</label></dt>'\
            '<dd><ul class="errorlist"><li>Enter a valid date.</li></ul>'\
            '<input type="date" name="date" value="Wrong DATE_DATA" required id="id_date"><br/>'\
            '<span class="helptext">DATE_HELP_TEXT</span>'\
            '<input type="hidden" name="hidden_input" id="id_hidden_input"></dd>'

        flexform_str = str(getattr(flexform,method_name)())
        self.assertTrue(
            isequal_as_html(result_test_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(result_test_str, flexform_str)
        )

        # test all data are hidden and errors
        flexform = _get_test_form_class(FlexForm, True)(data, initial=initial)
        result_test_str = '<ul class="errorlist nonfield"><li>(Hidden field date) Enter a valid date.</li>'\
                          '<li>(Hidden field hidden_input) This field is required.</li></ul>'\
                          '<input type="hidden" name="input" value="input DATA" id="id_input">'\
                          '<input type="hidden" name="date" value="Wrong DATE_DATA" id="id_date">'\
                          '<input type="hidden" name="hidden_input" id="id_hidden_input">'\

        flexform_str = str(getattr(flexform,method_name)())
        self.assertTrue(
            isequal_as_html(result_test_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(result_test_str, flexform_str)
        )

        # test all data are hidden and no errors
        data = {'input': 'input DATA', 'date': datetime.date.today(), 'hidden_input': 'HIDDEN DATA'}
        initial = {'input': 'initial input', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        flexform = _get_test_form_class(FlexForm, True)(data, initial=initial)
        result_test_str = '<input type="hidden" name="input" value="input DATA" id="id_input">'\
            '<input type="hidden" name="date" value="{0}" id="id_date">'\
            '<input type="hidden" name="hidden_input" value="HIDDEN DATA" id="id_hidden_input">'\
            .format(datetime.date.today())

        flexform_str = str(getattr(flexform,method_name)())
        self.assertTrue(
            isequal_as_html(result_test_str, flexform_str),
            'From the HTML point of view {0} and {1} these strings are not equal.'.format(result_test_str, flexform_str)
        )

    def _test_of_performance_speed(self):
        data = {'input': 'input DATA', 'date': 'Wrong DATE_DATA'}
        initial = {'input': 'initial input content', 'date': '2020-02-20', 'hidden_input': 'HIDDEN INITIAL DATA'}

        start = datetime.datetime.now()
        for i in range(100):
            str(SimpleFlexFormForTests(data, initial=initial))
        flexform_dif = datetime.datetime.now() - start

        start = datetime.datetime.now()
        for i in range(100):
            str(SimpleFormForTests(data, initial=initial))
        form_dif = datetime.datetime.now() - start

        self.assertEqual(flexform_dif, form_dif)
        #AssertionError: datetime.timedelta(microseconds=214652) != datetime.timedelta(microseconds=118421)



