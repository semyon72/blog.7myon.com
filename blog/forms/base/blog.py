# Project: blog_7myon_com
# Package: 
# Filename: blog.py
# Generated: 2020 Oct 11 at 20:44 
# Description of <blog>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django import forms

from blog.models import Blog
from sm_flexdata.html.form_elements import FlexFormMixin


class BlogForm(type('BlogFormFromModel', (forms.Form,), forms.models.fields_for_model(Blog))):
    """
        Main aim this form is a base for filtering and other action that doesn't imply
        to do something in database
    """
    pass


class BlogModelForm(FlexFormMixin, forms.ModelForm):

    class Meta:
        model = Blog
        exclude = []


class BlogFilterForm(FlexFormMixin, BlogForm):

    field_group = [BlogForm.base_fields.keys()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reinit()

    def _reinit(self):
        self.fields['name'].required = False
        tagline = self.fields['tagline']
        tagline.required = False
        tagline.widget = forms.widgets.TextInput(attrs=tagline.widget.attrs)
