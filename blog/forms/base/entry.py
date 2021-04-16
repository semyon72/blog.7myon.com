# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2020 Oct 17 at 18:27 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
import functools

from django import forms
from django.forms import fields_for_model
from django.utils.text import Truncator

from blog.models import Entry, EntryText, EntryComment, EntryStat
from sm_flexdata.html.form_elements import FlexFormMixin


class WidthLimitedSelect(forms.Select):

    max_label_width = 0

    def __init__(self, attrs=None, choices=(), max_label_width=0):
        self.max_label_width = max_label_width
        super().__init__(attrs, choices)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        if self.max_label_width:
            label = str(Truncator(label).chars(self.max_label_width, ' ...'))
        return super(type(self), self).create_option(name, value, label, selected, index, subindex, attrs)


class EntryForm(type('EntryFormFromModel', (forms.Form,), fields_for_model(Entry))):
    """
        Main aim this form is a base for filtering and other action that doesn't imply
        to do something in database
    """
    pass


class FilterEntryForm(FlexFormMixin, EntryForm):

    field_group = [
        ['blog', 'headline'],
        ['author', 'coauthors'],
        ['pub_date', 'pub_date_end', 'mod_date', 'mod_date_end'],
        'inactive'
    ]

    pub_date_end = forms.DateField(
        label='end of publishing',
        # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    mod_date_end = forms.DateField(
        # will used as label in form. In general it changes the field name in admin interface.
        label='end of modification',
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reinit()

    def _reinit(self):
        for field in self.fields.values():
            field.required = False


class EntryModelForm(FlexFormMixin, forms.ModelForm):

    class Meta:
        model = Entry
        exclude = []


class EntryTextForm(type('EntryTextFormFromModel', (forms.Form,), fields_for_model(EntryText))):
    """
        Main aim this form is a base for filtering and other action that doesn't imply
        to do something in database
    """
    pass


class FilterEntryTextForm(FlexFormMixin, EntryTextForm):

    field_group = [EntryTextForm.base_fields.keys()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reinit()

    def _reinit(self):
        tmpf = self.fields.get('body_text', None)
        tmpf.widget = forms.TextInput(attrs=tmpf.widget.attrs)

        tmpf = self.fields.get('entry', None)
        tmpf.widget.max_label_width = 100
        tmpf.widget.create_option = functools.partial(WidthLimitedSelect.create_option, tmpf.widget)

        for field in self.fields.values():
            field.required = False


class EntryTextModelForm(FlexFormMixin, forms.ModelForm):

    class Meta:
        model = EntryText
        exclude = []
        widgets = {
            'entry': WidthLimitedSelect
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entry'].widget.max_label_width = 100
        self.fields['body_text'].widget.attrs['cols'] = 80


class EntryWithTextModelForm(EntryModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        args_copy = [*args]
        kwargs_copy = kwargs.copy()
        if len(args_copy) > 8:
            del args_copy[8]  # instance
        if hasattr(self.instance, 'entrytext'):
            kwargs_copy['instance'] = self.instance.entrytext
        else:
            kwargs_copy.pop('instance', None)
        kwargs_copy['prefix'] = EntryTextModelForm.__name__.lower()

        self.entrytext_form = EntryTextModelForm(*args_copy, **kwargs_copy)
        for etfield_name, etfield in self.entrytext_form.fields.items():
            self.fields[self.add_prefix(self.entrytext_form.add_prefix(etfield_name))] = etfield

        self.__getitem__handlers = self._get__getitem__handlers()

    def _get__getitem__handlers(self):
        # caller like super().__getitem__ or self.entrytext_form.__getitem__ and original fieldname
        result = {self.add_prefix(field_name): (super(self.__class__, self).__getitem__, self.add_prefix(field_name)) for field_name in self.fields}
        for field_name in self.entrytext_form.fields:
            prefixed_name = self.add_prefix(self.entrytext_form.add_prefix(field_name))
            result[prefixed_name] = (self.entrytext_form.__getitem__, field_name)
        return result

    def __getitem__(self, name):
        func__getitem__, real_fieldname = self.__getitem__handlers[name]
        return func__getitem__(real_fieldname)

    def save(self, commit=True):
        self.entrytext_form.instance.entry = super().save(commit=commit)
        self.entrytext_form.save(commit=commit)
        return self.instance


class EntryCommentForm(type('EntryCommentFormFromModel', (forms.Form,), fields_for_model(EntryComment))):
    """
        Main aim this form is a base for filtering and other action that doesn't imply
        to do something in database
    """
    pass


class FilterEntryCommentForm(EntryCommentForm):
    pass


class EntryCommentModelForm(forms.ModelForm):

    class Meta:
        model = EntryComment
        fields = forms.ALL_FIELDS


class EntryStatForm(type('EntryStatFormFromModel', (forms.Form,), fields_for_model(EntryStat))):
    """
        Main aim this form is a base for filtering and other action that doesn't imply
        to do something in database
    """
    pass


class FilterEntryStatForm(EntryStatForm):
    pass


class EntryStatModelForm(forms.ModelForm):

    class Meta:
        model = EntryStat
        exclude = []
