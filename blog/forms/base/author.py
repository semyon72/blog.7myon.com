# Project: blog_7myon_com
# Package: 
# Filename: author.py
# Generated: 2020 Oct 11 at 23:05 
# Description of <author>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django import forms
from django.forms import TextInput, fields_for_model, ModelForm
from django.db import models

from sm_flexdata.html.form_elements import FlexFormMixin
from sm_flexdata.views import FilteredListView
from blog.models import Author


class AuthorForm(type('AuthorFormFromModel', (forms.Form,), fields_for_model(Author))):
    """
        Main aim this form is a base for filtering and other action that doesn't imply
        to do something in database
    """
    pass


class AuthorModelForm(FlexFormMixin, ModelForm):
    """
        Main aim this form is editing and adding into database
    """

    class Meta:
        model = Author
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The omit the users from choices, who are coupled already
        user = self.fields['user']
        authorQ = models.Q(is_superuser=False, author__isnull=True)
        if self.instance and self.instance.pk:  # row exists in database already
            # need to add itself user for appear it in selectt
            authorQ = authorQ | models.Q(author__pk=self.instance.pk)
        user.queryset = user.queryset.filter(authorQ)
        # end exclusion


class AuthorFilterForm(FlexFormMixin, AuthorForm):

    field_group = [AuthorForm.base_fields.keys()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reinit()

    def _reinit(self):
        self.fields['user'].required = False
        self.fields['name'].required = False
        email_field = self.fields['email']
        email_field.required = False
        email_field.widget = TextInput(attrs=email_field.widget.attrs)
        FilteredListView.remove_specific_validators(email_field)
