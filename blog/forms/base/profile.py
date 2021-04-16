# Project: blog_7myon_com
# Package: 
# Filename: profile.py
# Generated: 2021 Apr 04 at 13:05 
# Description of <profile>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.forms import Form
from django.forms.models import ModelForm, fields_for_model

from ...models import Author
from sm_flexdata.html.form_elements import FlexFormMixin


class ProfileForm(type('ProfileFormFromModel', (Form,), fields_for_model(Author))):
    pass


class ProfileModelForm(FlexFormMixin, ModelForm):

    class Meta:
        model = Author
        fields = ['name', 'email']
