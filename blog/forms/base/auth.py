# Project: blog_7myon_com
# Package: 
# Filename: auth.py
# Generated: 2021 Jan 09 at 22:32 
# Description of <auth>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from collections import OrderedDict

from django.contrib.auth import forms, get_user_model
from django.forms.models import ModelFormMetaclass

from sm_flexdata.html.form_elements import FlexFormMixin
from blog.models import Registration

UserModel = get_user_model()


class UserCreationModelFormMetaclass(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        ext_attrs = OrderedDict(((UserModel.EMAIL_FIELD, None), ('first_name', None), ('last_name', None)))
        for field_name in ext_attrs:
            ext_attrs[field_name] = getattr(UserModel, field_name).field.formfield()
        email = ext_attrs[UserModel.EMAIL_FIELD]
        email.required = True
        email.widget.attrs['autocomplete'] = 'email'

        super_meta = [base for base in bases if hasattr(base, 'Meta')]
        fields_names = (*ext_attrs,)
        if super_meta:
            meta_base = super_meta[0].Meta
            fields_names = (*meta_base.fields, *ext_attrs)
        else:
            meta_base = object
        ext_attrs['Meta'] = type(name + '.Meta', (meta_base,), {'fields': fields_names})
        ext_attrs['field_order'] = (*fields_names, 'password1', 'password2')

        attrs.update(ext_attrs)
        return super().__new__(mcs, name, bases, attrs)


class UserCreationModelForm(FlexFormMixin, forms.UserCreationForm, forms.PasswordResetForm,
                            metaclass=UserCreationModelFormMetaclass):

    # def clean_username(self):
    #     # TODO: Needs to remove right after all of auth parts will be done
    #     """
    #         Only for development purposes
    #     """
    #     try:
    #         user = self._meta.model.objects.get(username=self.cleaned_data['username'])
    #     except self._meta.model.DoesNotExist:
    #         pass
    #     else:
    #         if user.registration_set.count() > 0:
    #             user.registration_set.clear()
    #         user.delete()
    #
    #     return self.cleaned_data['username']

    def save(self, *args, **kwargs):
        user = super().save(False)
        user.is_active = False
        user.email = type(user).objects.normalize_email(self.cleaned_data[UserModel.EMAIL_FIELD])
        user.save()
        if self.instance.pk:
            try:
                registration = Registration(
                    registration_email=getattr(user, UserModel.EMAIL_FIELD),
                    user=user,
                    requested=user.date_joined,
                    is_active=False,
                )
                registration.save()
                forms.PasswordResetForm.save(self, **kwargs)
            except Exception:
                if registration.pk:
                    registration.delete()
                user.delete()
                raise
        return user

    def get_users(self, email):
        return (self.instance, )


class AuthenticationForm(FlexFormMixin, forms.AuthenticationForm):
    pass


class PasswordChangeForm(FlexFormMixin, forms.PasswordChangeForm):
    pass


class PasswordResetForm(FlexFormMixin, forms.PasswordResetForm):
    pass


class SetPasswordForm(FlexFormMixin, forms.SetPasswordForm):
    pass
