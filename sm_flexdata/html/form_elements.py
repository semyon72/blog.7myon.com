# Project: blog_7myon_com
# Package: 
# Filename: form_elements.py
# Generated: 2020 Dec 18 at 05:40 
# Description of <form_elements>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from collections import OrderedDict, Generator

from django.forms import BoundField, Form
from django.forms.utils import ErrorList
from django.urls import ResolverMatch
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .elements import NamedHTMLElement, BaseData


def add_ignore_iterable_types(ignore_iterable_types):
    """
        Class decorator that add parameter "ignore_iterable_types"
        to class attribute ignore_iterable_types
    """
    def real_decorator(cls):
        if not issubclass(cls, BaseData):
            raise TypeError('This class decorator applied to descendants of BaseData only.')
        cls.ignore_iterable_types = (*super(cls, cls).ignore_iterable_types, *ignore_iterable_types)
        return cls
    return real_decorator


@add_ignore_iterable_types((BoundField, ))
class DefaultFormElement(NamedHTMLElement):

    element_name_pattern = '%s'

    render_as = ''

    def __init__(self, data=None, tag=None, attrs=None, element_name=None):
        if not DefaultFormElement.render_as:
            DefaultFormElement.render_as = next(iter(DEFAULT_CONFIG_DATA))

        kwargs = DEFAULT_CONFIG_DATA[self.render_as].get(self.__class__)
        if kwargs is not None:
            kwargs = kwargs.copy()
        else:
            kwargs = {}
        kwargs.update(
            [(arg, val) for arg, val in (
                ('data', data), ('tag', tag), ('attrs', attrs), ('element_name', element_name)
            ) if val is not None]
        )
        super().__init__(**kwargs)

    @staticmethod
    def set_default_render_as(render_as=None):
        if not render_as:
            render_as = next(iter(DEFAULT_CONFIG_DATA))
        elif render_as not in DEFAULT_CONFIG_DATA:
            raise KeyError('DEFAULT_CONFIG_DATA does not contain "{}" key.'.format(render_as))
        DefaultFormElement.render_as = render_as

    def on_get_element_name(self, name):
        if self.element_name_pattern and '%' in self.element_name_pattern:
            name = self.element_name_pattern % name
        return super(DefaultFormElement, self).on_get_element_name(name)

    def set_data(self, data, name):
        self.element_name = name
        self.data = data
        return self

    @property
    def original_name(self):
        return getattr(self, '_NamedDataMixin__element_name')

    def swap_data_in_order(self, *comparers):
        """
        Will swap field data elements in order defined comparer functions inside self.data (their places)
        Other elements inside self.data will not be touched
        :return: self
        """
        comparer_indexes = {}
        data_list = self.data_as_list()
        for eli, el in enumerate(data_list):
            for ci, comparer in enumerate(comparers):
                if bool(comparer(el)):
                    comparer_indexes[ci] = eli
                    break;
        sort_list = [eli for ci, eli in sorted(comparer_indexes.items(), key=lambda tpl: tpl[0])]
        sort_list_len = len(sort_list)
        cidx = 0
        while cidx < sort_list_len-1:
            if sort_list[cidx] > sort_list[cidx+1]:
                # change order in real data
                cv = data_list[sort_list[cidx]]
                data_list[sort_list[cidx]] = data_list[sort_list[cidx+1]]
                data_list[sort_list[cidx+1]] = cv
                # change order in sorted list
                cv = sort_list[cidx]
                sort_list[cidx] = sort_list[cidx+1]
                sort_list[cidx+1] = cv
                # start from begin
                cidx = 0
            else:
                cidx += 1

        if not isinstance(self.data, list):
            self.data = data_list

        return self


class FormHiddenFields(DefaultFormElement):

    def on_set_element_name(self, name):
        if not name:
            name = 'hidden_fields'
        return super().on_set_element_name(name)


@add_ignore_iterable_types((ErrorList, ))
class FormNoneFieldErrors(DefaultFormElement):

    def on_set_element_name(self, name):
        if not name:
            name = 'non_field_errors'
        return super().on_set_element_name(name)


class FormFieldLabel(DefaultFormElement):

    element_name_pattern = 'field_%s_label'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__label_attrs = None
        self.__label_suffix = None
        self._bound_filed = None

    def _compose_data(self, data):
        if self._bound_filed is not None:
            data = self._bound_filed.label_tag(attrs=self.label_attrs, label_suffix=self.label_suffix)
        return super()._compose_data(data)

    def set_from(self, bf: BoundField):
        if not isinstance(bf, (BoundField,)):
            raise TypeError('"bf" must be instance of BoundField')
        self._bound_filed = bf

        return self.set_data(None, bf.name)

    @property
    def label_attrs(self):
        return self.__label_attrs

    @label_attrs.setter
    def label_attrs(self, value):
        if not isinstance(value, (dict, type(None))):
            raise TypeError('label_attrs should be dictionary or None.')
        self.__label_attrs = value
        if value is not None:
            self.__label_attrs = {self.value_to_safe(k): self.value_to_safe(v) for k, v in value.items()}

    @property
    def label_suffix(self):
        return self.__label_suffix

    @label_suffix.setter
    def label_suffix(self, value):
        self.__label_suffix = value if value is None else self.value_to_safe(value)


class FormFieldDataHelpText(DefaultFormElement):

    element_name_pattern = 'field_%s_help_text'

    prefix_html_content = mark_safe('<br/>')

    def compose(self):
        return self.value_to_safe(self.prefix_html_content)+super().compose()

    def set_from(self, bf: BoundField):
        if not isinstance(bf, (BoundField,)):
            raise TypeError('"bf" must be instance of BoundField')
        # str casting needs for cases when bf.help_text is lazy object of safe string with HTML tags
        return self.set_data(str(bf.help_text), bf.name)


@add_ignore_iterable_types((ErrorList, ))
class FormFieldDataErrors(DefaultFormElement):

    element_name_pattern = 'field_%s_errors'

    def set_from(self, bf: BoundField):
        if not isinstance(bf, (BoundField,)):
            raise TypeError('"bf" must be instance of BoundField')
        return self.set_data(bf.errors, bf.name)


@add_ignore_iterable_types((ErrorList, ))
class FormFieldData(DefaultFormElement):

    element_name_pattern = 'field_%s_data'
    show_errors = True
    show_helptext = True

    def __init__(self, data=None, tag=None, attrs=None, element_name=None):
        super().__init__(data, tag, attrs, element_name)
        self.__show_errors = self.__class__.show_errors
        self.__errors = None
        self.__show_helptext = self.__class__.show_helptext
        self.__helptext = None

    @property
    def bound_field(self):
        for el in self.data_as_list():
            if isinstance(el, BoundField):
                return el

    def set_from(self, bf: BoundField):
        if not isinstance(bf, (BoundField,)):
            raise TypeError('"bf" must be instance of BoundField')
        return self.set_data(bf, bf.name)

    def _compose_data(self, data):
        result_data = []
        for el in self.data_as_list(data):
            if isinstance(el, BoundField):
                # test on errors and insert on begin
                errors = self.errors
                if bool(errors) and self.show_errors:
                    result_data.append(errors)
                # bound field itself
                result_data.append(el)
                # if exists help_text then append on end
                helptext = self.helptext
                if bool(helptext) and self.show_helptext:
                    result_data.append(helptext)
            else:
                result_data.append(el)

        return super()._compose_data(result_data)

    @property
    def show_errors(self):
        return self.__show_errors

    @show_errors.setter
    def show_errors(self, value):
        self.__show_errors = bool(value)

    def _fallback_errors(self) -> FormFieldDataErrors:
        bf = self.bound_field
        if bf is not None and len(bf.errors) > 0:
            return FormFieldDataErrors().set_from(bf)

    @property
    def errors(self):
        if bool(self.__errors):
            return self.__errors
        else:
            return self._fallback_errors()

    def __default_errors_helptext_setter(self, attribute, result_type, value):
        realattr_name = ''.join(['_', self.__class__.__name__, attribute])
        setattr(self, realattr_name, None)
        if not bool(value):
            return

        if isinstance(value, result_type):
            if len(value.data_as_list()) > 0:
                setattr(self, realattr_name, value)
            return

        result_obj = result_type()
        result_obj.data = value
        bf = self.bound_field
        if bf:
            result_obj.element_name = bf.name
        setattr(self, realattr_name, result_obj)

    @errors.setter
    def errors(self, errors) -> FormFieldDataErrors:
        self.__default_errors_helptext_setter('__errors', FormFieldDataErrors, errors)

    def _fallback_helptext(self) -> FormFieldDataHelpText:
        bf = self.bound_field
        if bf is not None and bool(bf.help_text):
            return FormFieldDataHelpText().set_from(bf)

    @property
    def show_helptext(self):
        return self.__show_helptext

    @show_helptext.setter
    def show_helptext(self, value):
        self.__show_helptext = bool(value)

    @property
    def helptext(self) -> FormFieldDataHelpText:
        if bool(self.__helptext):
            return self.__helptext
        else:
            return self._fallback_helptext()

    @helptext.setter
    def helptext(self, helptext) -> FormFieldDataHelpText:
        self.__default_errors_helptext_setter('__helptext', FormFieldDataHelpText, helptext)


class FormField(DefaultFormElement):

    element_name_pattern = 'field_%s'

    def __init__(self, data=None, tag=None, attrs=None, element_name=None):
        self.visible = True
        super().__init__(data, tag, attrs, element_name)

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = bool(value)

    def _compose_data(self, data):
        if not self.visible:
            return mark_safe('')

        return super()._compose_data(data)

    def set_from(self, bf: BoundField):
        if not isinstance(bf, (BoundField,)):
            raise TypeError('"bf" must be instance of BoundField')
        self.visible = not bf.is_hidden
        return self.set_data([FormFieldLabel().set_from(bf), FormFieldData().set_from(bf)], bf.name)

    def set_from_group(self, label: str, group):
        if not isinstance(group, (FormGroup,)):
            raise TypeError('"group" must be instance of {}'.format(FormGroup.__name__))
        self.visible = True
        data = [
            FormFieldLabel().set_data(label, group.element_name),
            FormFieldData().set_data(group, group.element_name)
        ]
        return self.set_data(data, group.element_name)

    @property
    def field_label(self) -> FormFieldLabel:
        for el in self.data_as_list():
            if isinstance(el, FormFieldLabel):
                return el

    @property
    def field_data(self) -> FormFieldData:
        for el in self.data_as_list():
            if isinstance(el, FormFieldData):
                return el


class FormRow(DefaultFormElement):

    element_name_pattern = 'row_%s'

    def __init__(self, data=None, tag=None, attrs=None, element_name=None):
        self.__visible = True
        super().__init__(data, tag, attrs, element_name)

    def compose(self):
        if not self.visible:
            return mark_safe('')
        return super().compose()

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = bool(value)

    def __getitem__(self, field_name):
        for el in self.data_as_list():
            if isinstance(el, FormField) and el.original_name == field_name:
                return el

        raise KeyError('Field "{}" not found.'.format(field_name))

    @property
    def field_names(self):
        return [el.original_name for el in self.data_as_list() if isinstance(el, FormField)]

    @property
    def fields_num(self):
        return len(self.field_names)

    def set_from(self, bfields):
        """
            By default it sets element name in id(self) value.
            If you need more sophisticated name then you can reset element_name at once after
            this method was invoked - form_group.set_from(bfields).element_name = 'liked name'
        """
        err_msg = '"bfields" must be or instance of BoundField or iterable value of BoundField values.'
        if isinstance(bfields, Generator) or not (hasattr(bfields, '__iter__') or isinstance(bfields, BoundField)):
            raise TypeError(err_msg)

        if isinstance(bfields, (BoundField,)):
            bfields = (bfields,)

        if sum((1 for bf in bfields if not isinstance(bf, (BoundField,)))) > 0:
            raise TypeError(err_msg)

        self.set_data((FormField().set_from(bf) for bf in bfields), str(id(self)))
        self.visible = sum((1 for el in self.data_as_list() if isinstance(el, (FormField, )) and el.visible)) > 0

        return self


class FormGroup(DefaultFormElement):
    element_name_pattern = 'group_%s'

    def max_fields_num_in_row(self):
        """
            Returns max number of visible fields in row
        """
        max_fnum = 0
        for row in self.data_as_list():
            if isinstance(row, FormRow):
                fnum = row.fields_num
                if fnum > max_fnum:
                    max_fnum = fnum
        return max_fnum

    def add_row(self, row: FormRow):
        if not (isinstance(row, FormRow)):
            raise TypeError('"row" must be instance of {}.'.format(FormRow.__name__))
        self.add_data(row)

    def set_from(self, bfields):
        """
            "bfields" must be iterable like [bf1, [bf2, bf3], .... ].
            Based on this example it will generate
                Row(bf1) -> render_as = 'table' -> <tr><th>[bf1.label_tag]</th><td>[bf1]</td></tr>
                Row(bf2,bf3) -> render_as = 'table' ->
                    <tr><th>[bf2.label_tag]</th><td>[bf2]</td><th>[bf3.label_tag]</th><td>[bf3]</td></tr>

            By default it sets element name in id(self) value.
            If you need more sophisticated name then you can reset element_name at once after
            this method has been invoke - form_group.set_from(bfields).element_name = 'liked name'
        """
        err_msg = '"bfields" must be iterable like [bf, [bf, bf], .... ].'
        if not (hasattr(bfields, '__iter__')):
            raise TypeError(err_msg)
        return self.set_data((FormRow().set_from(bf) for bf in bfields), str(id(self)))


class FlexFormMixin:

    field_group = None

    @staticmethod
    def _return_last_field_data_element(group_element: FormGroup):
        """
            This method could be helpful in future and was used in first version.
        """
        for row in reversed(group_element.data_as_list()):
            if not isinstance(row, FormRow) or not row.visible:
                continue
            for field in reversed(row.data_as_list()):
                if not isinstance(field, FormField) or not field.visible:
                    continue
                for field_data in reversed(field.data_as_list()):
                    if not isinstance(field_data, FormFieldData):
                        continue
                    else:
                        return field_data
        return None

    def _get_prepared_data_for_form_rendering(self, field_group=None):

        class PreparedDataForFormRendering:

            def __init__(self, rows, hidden_fields, top_errors_row, last_visible_field_data, max_fields_in_row) -> None:
                self.rows = rows
                self.hidden_fields = hidden_fields
                self.top_errors_row = top_errors_row
                self.last_visible_field_data = last_visible_field_data
                self.max_fields_in_row = max_fields_in_row

        def add_top_error(bf: BoundField):
            if bf.is_hidden and len(bf.errors) > 0:
                top_errors.extend([
                    _('(Hidden field %(name)s) %(error)s') % {'name': bf.name, 'error': str(e)} for e in bf.errors]
                )

        def add_form_field_to_row(row: FormRow, field_name):
            bf: BoundField = self[field_name]
            if bf.is_hidden:
                add_top_error(bf)
                hidden_fields.append(bf)
            else:
                row.add_data(FormField().set_from(bf))
                # Next 3 lines were repeated like in original code
                # This html_class_attr will be added as a class into <tr ....> | <ul ...> etc.
                css_classes = bf.css_classes()
                if css_classes:
                    attrs = row.attrs.get('class', '')
                    row.attrs['class'] = ' '.join((*attrs.split(), *css_classes.split()))

        field_group = field_group or self.field_group or [bf for bf in self.fields]

        top_errors = self.non_field_errors().copy()

        last_visible_field_data = None
        hidden_fields, rows, max_fields_in_row = ([], [], 0)
        for field_names in field_group:
            row = FormRow()
            row.element_name = str(id(row))
            if not isinstance(field_names, str) and hasattr(field_names, '__iter__'):
                for field_name in field_names:
                    add_form_field_to_row(row, field_name)
            else:
                add_form_field_to_row(row, field_names)

            num_ff = len(row.data_as_list())
            if num_ff > 0:
                if max_fields_in_row < num_ff:
                    max_fields_in_row = num_ff

                last_visible_field_data = row.data_as_list()[num_ff-1].data_as_list()[1]  # FormFieldData
                rows.append(row)

        # create top_errors_row element
        top_errors_row = None
        if len(top_errors) > 0:
            top_errors_row = FormRow(data=FormNoneFieldErrors(
                data=top_errors,
            ), element_name='non_field_errors')
            rows.insert(0, top_errors_row)  # insert at top of rows

        return PreparedDataForFormRendering(
            rows=rows,
            hidden_fields=hidden_fields,
            top_errors_row=top_errors_row,
            last_visible_field_data=last_visible_field_data,
            max_fields_in_row=max_fields_in_row
        )

    def _put_hidden_fields_in_appropriate_place(self, root, prepared_data):
        # puts content of hidden fields into appropriate place
        if len(prepared_data.hidden_fields) > 0:
            hidden_fields_element = FormHiddenFields(data=prepared_data.hidden_fields)
            if prepared_data.last_visible_field_data is not None:
                prepared_data.last_visible_field_data.add_data(hidden_fields_element)
            else:
                if prepared_data.top_errors_row is not None:
                    prepared_data.top_errors_row.data.add_data(hidden_fields_element)
                else:
                    root.data = hidden_fields_element

    def _get_root_form_group(self, prepared_data, callback):
        root = FormGroup(data=prepared_data.rows, element_name='root')
        # to clean <table> | '<ul>' etc. tag
        root.tag = ''
        self._put_hidden_fields_in_appropriate_place(root, prepared_data)

        if callable(callback):
            res = callback(root)
            if res is not None:
                root = res
        return root

    def as_table(self, field_group=None, *, callback=None):
        FormGroup.set_default_render_as('table')
        prepared_data = self._get_prepared_data_for_form_rendering(field_group)

        # need adjust the colspan-s for tabled data
        row: FormRow
        for idx, row in enumerate(prepared_data.rows):
            if prepared_data.top_errors_row is not None and idx == 0:
                # skip top_errors_row if was added inside _get_prepared_data_for_form_rendering
                continue

            num_fields = len(row.data_as_list())
            dif = prepared_data.max_fields_in_row - num_fields
            if dif > 0:
                for i in range(dif):
                    row.add_data(FormField(
                        data=[
                            FormFieldLabel(data=mark_safe('&nbsp;'), element_name='stub'),
                            FormFieldData(data=mark_safe('&nbsp;'), element_name='stub')
                        ]
                    ))

        # if prepared_data.top_errors_row need adjust colspan-s
        if prepared_data.top_errors_row is not None and prepared_data.max_fields_in_row > 0:
            attrs = {'colspan': prepared_data.max_fields_in_row * 2}  # only for 'table' etc. for alignment
            non_field_error_row = prepared_data.top_errors_row.data
            if non_field_error_row.attrs is not None:
                non_field_error_row.attrs.update(attrs)
            else:
                non_field_error_row.attrs = attrs

        return str(self._get_root_form_group(prepared_data, callback))

    def as_bootstrap4(self, field_group=None, *, callback=None):

        def _checkbox_process(form_filed):
            # 1 need swap field_label with field_data inside form_field.data
            # label should be after
            form_filed.swap_data_in_order(
                lambda el: isinstance(el, FormFieldData),
                lambda el: isinstance(el, FormFieldLabel)
            )
            # 2 need remove label_sufix
            form_filed.field_label.label_suffix = ''
            # 3 label attrs => class="form-check-label"
            field_label_class = "form-check-label"
            # 4 bf.field.widjet.attrs => class="form-check-input"
            field_data_class = 'form-check-input'
            # 5 form_filed.attrs['class'] = "form-check" instead "form-group"
            parent_row = form_filed.parent
            pd = parent_row.data_as_list()
            try:
                fi = pd.index(form_filed)
            except ValueError as err:
                raise ValueError(
                    '{child} has parent, but parent {parent} has not {child} in data property. {err}'.format(
                        child=form_filed, parent=parent_row, err=''.join(err.args)
                    )
                )

            pd[fi] = DefaultFormElement(
                tag='div', data=form_filed,
                attrs={'class': form_filed.attrs.get('class', '')},
                element_name=form_filed.element_name+'_wrapper'
            )
            form_filed.attrs.update({'class': 'form-check'})
            parent_row.data = pd

            return field_label_class, field_data_class

        def _form_field_process(form_filed: FormField):
            fd = form_filed.field_data
            bf = fd.bound_field
            # general case
            field_label_class = 'col-form-label'
            field_data_class = 'form-control'
            if bf.widget_type == 'checkbox':
                field_label_class, field_data_class = _checkbox_process(form_filed)

            # move errors into form field node
            errors = fd.errors
            if bool(errors):
                form_filed.add_data(errors)
                fd.show_errors = False
                field_data_class += ' is-invalid'

            # general case
            form_filed.field_label.label_attrs = {'class': field_label_class}
            css_class = bf.field.widget.attrs.get('class', '')
            if field_data_class not in css_class.split():
                bf.field.widget.attrs['class'] = css_class + ' '+field_data_class if css_class else field_data_class

        def _internal_callback(callback):
            def wrapper(root):
                elements = []
                root.get_elements_by(elements, value=FormField, comparer=lambda el, v: isinstance(el, v))
                for form_field in elements:
                    _form_field_process(form_field)
                r = None
                if callable(callback):
                    r = callback(root)
                return r
            return wrapper

        FormGroup.set_default_render_as('bootstrap4')
        FormFieldDataHelpText.prefix_html_content = ''  # remove <br/> from help_texts
        prepared_data = self._get_prepared_data_for_form_rendering(field_group)
        root = self._get_root_form_group(prepared_data, callback=_internal_callback(callback))

        return str(root)

    def as_ul(self, *, callback=None):
        FormGroup.set_default_render_as('ul')
        # remove <br/> from help_texts
        prev_prefix_value = FormFieldDataHelpText.prefix_html_content
        try:
            FormFieldDataHelpText.prefix_html_content = ''
            prepared_data = self._get_prepared_data_for_form_rendering()
            # replace field data errors before label
            for row in prepared_data.rows:
                for field in row.data_as_list():
                    if isinstance(field, FormField):
                        field_data = field.data[1]
                        errors = field_data.errors
                        if bool(errors) > 0:
                            field_data.show_errors = False
                            field.data = [*errors.data_as_list(), *field.data_as_list()]

            result = str(self._get_root_form_group(prepared_data, callback))
        finally:
            # restore default <br/> - helpful for unit testing
            FormFieldDataHelpText.prefix_html_content = prev_prefix_value

        return result

    def as_p(self, *, callback=None):
        FormGroup.set_default_render_as('p')
        # remove <br/> from help_texts
        prev_prefix_value = FormFieldDataHelpText.prefix_html_content
        try:
            FormFieldDataHelpText.prefix_html_content = ''
            prepared_data = self._get_prepared_data_for_form_rendering()
            result_rows = []
            # replace field data errors before label
            for idx, row in enumerate(prepared_data.rows):
                # fix for case - if top errors exists then top row must be without tag
                if idx == 0 and prepared_data.top_errors_row is not None:
                    row.tag = ''

                # place all errors on previous row
                for field in row.data_as_list():
                    if isinstance(field, FormField):
                        field_data = field.data[1]
                        errors = field_data.errors
                        if bool(errors) > 0:
                            result_rows.append(FormRow(tag='', data=errors, element_name='errors_on_separate_row'))
                            field_data.show_errors = False
                result_rows.append(row)

            prepared_data.rows = result_rows

            # fix for case all data is hidden and has errors
            if prepared_data.top_errors_row and prepared_data.max_fields_in_row == 0:
                row = FormRow(element_name='all_hidden_fields')
                prepared_data.rows.append(row)
                prepared_data.last_visible_field_data = row

            result = str(self._get_root_form_group(prepared_data, callback))
        finally:
            # restore default <br/> - helpful for unit testing
            FormFieldDataHelpText.prefix_html_content = prev_prefix_value

        return result

    def as_dl(self, *, callback=None):
        FormGroup.set_default_render_as('dl')
        prepared_data = self._get_prepared_data_for_form_rendering()

        if prepared_data.top_errors_row is not None and prepared_data.max_fields_in_row == 0:
            # this means exist no real fields (possible all are hidden) but we have
            # global errors and we do not need to enclose errors into div tag that configured
            # by default
            prepared_data.top_errors_row.data.tag = ''

        return str(self._get_root_form_group(prepared_data, callback))


class FlexForm(FlexFormMixin, Form):
    pass


# must be last in module
DEFAULT_CONFIG_DATA = OrderedDict([
        # All empty values can be omitted
        # Available keys: {'tag': str, 'attrs': {}, data: int, str, SafeStr, ....}
        # This values are values by default and can or will be redefined in according to the logic
        ('table', {
            FormNoneFieldErrors: {'tag': 'td'},
            FormFieldDataErrors: {'tag': '', },
            FormFieldDataHelpText: {'tag': 'span', 'attrs': {'class': 'helptext'}},
            FormFieldLabel: {'tag': 'th', },
            FormFieldData: {'tag': 'td', },
            FormField: {'tag': '', },
            FormRow: {'tag': 'tr', },
            FormGroup: {'tag': 'table', 'attrs': {'border': '0'}},
        }),
        ('ul', {
            FormNoneFieldErrors: {'tag': ''},
            FormFieldDataErrors: {'tag': '', },
            FormFieldDataHelpText: {'tag': 'span', 'attrs': {'class': 'helptext'}},
            FormFieldLabel: {'tag': '', },
            FormFieldData: {'tag': '', },
            FormField: {'tag': '', },
            FormRow: {'tag': 'li', },
            FormGroup: {'tag': 'ul', },
        }),
        ('dl', {
            FormNoneFieldErrors: {'tag': 'div'},
            FormFieldDataErrors: {'tag': '', },
            FormFieldDataHelpText: {'tag': 'span', 'attrs': {'class': 'helptext'}},
            FormFieldLabel: {'tag': 'dt', },
            FormFieldData: {'tag': 'dd', },
            FormField: {'tag': '', },
            FormRow: {'tag': '', },
            FormGroup: {'tag': 'dl', },
        }),
        ('p', {
            FormNoneFieldErrors: {'tag': ''},
            FormFieldDataErrors: {'tag': '', },
            FormFieldDataHelpText: {'tag': 'span', 'attrs': {'class': 'helptext'}},
            FormFieldLabel: {'tag': '', },
            FormFieldData: {'tag': '', },
            FormField: {'tag': '', },
            FormRow: {'tag': 'p', },
            FormGroup: {'tag': 'p', },
        }),
        ('bootstrap4', {
            FormNoneFieldErrors: {'tag': 'div', 'attrs': {'class': 'alert alert-danger', 'role': "alert"}},
            FormFieldDataErrors: {'tag': 'div', 'attrs': {'class': 'invalid-feedback'}},
            FormFieldDataHelpText: {'tag': 'span', 'attrs': {'class': 'form-text text-muted'}},
            FormFieldLabel: {'tag': '', },
            FormFieldData: {'tag': '', },
            FormField: {'tag': 'div', 'attrs': {'class': 'form-group col-auto'}},
            FormRow: {'tag': 'div', 'attrs': {'class': 'form-row'}},
            FormGroup: {'tag': ''},
        }),
    ])
