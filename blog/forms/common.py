# Project: blog_7myon_com
# Package: 
# Filename: base.py
# Generated: 2020 Oct 13 at 22:02 
# Description of <base>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from collections.abc import Sized, Generator
from functools import cached_property
from datetime import date

from django import forms
from django.db import models

# next part is used inside BaseHtmlOutput
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe, SafeString
from django.utils.translation import gettext as _
# end part of BaseHtmlOutput


class ModelFormIdFieldMixin(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        k = 'initial'
        if k in kwargs and kwargs[k] is not None and isinstance(kwargs[k], models.Model):
            kwargs['initial'] = forms.model_to_dict(kwargs['initial'])
        super().__init__(*args, **kwargs)


class DeleteForm(ModelFormIdFieldMixin, forms.Form):
    pass
