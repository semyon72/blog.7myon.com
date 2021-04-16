# Project: blog_7myon_com
# Package: 
# Filename: auth.py
# Generated: 2021 Jan 09 at 22:33 
# Description of <auth>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import views as auth_views, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

from blog.forms.base.auth import (UserCreationModelForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm,
                                  SetPasswordForm)
from blog.models import Author
from ... import urls_settings


UserModel: User = get_user_model()


class LoginView(auth_views.LoginView):

    form_class = AuthenticationForm

    def get_success_url(self):
        url = super().get_success_url()
        return urls_settings.get_url_for_section(self.request.user, url)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['username'] = type(self.request.user).__name__
        if self.request.user.is_authenticated and hasattr(self.request.user, 'get_full_name'):
            kwargs['username'] = self.request.user.get_full_name()
        return kwargs


class RegistrationView(auth_views.PasswordResetView):

    subject_template_name = 'blog/auth/registration/user_registration_subject.txt'
    email_template_name = 'blog/auth/registration/user_registration_email.html'
    # html_email_template_name = None
    # from_email = None
    # extra_email_context = None

    form_class = UserCreationModelForm
    success_url = reverse_lazy('blog:user_registration_done')
    template_name = 'blog/auth/registration/user_registration_form.html'
    title = _('User registration')
    token_generator = default_token_generator


class RegistrationDoneView(auth_views.PasswordResetDoneView):
    template_name = 'blog/auth/registration/user_registration_done.html'
    title = _('User registration request sent')


INTERNAL_REGISTRATION_CONFIRM_SESSION_TOKEN = '_registration_confirm_token'


class RegistrationConfirmView(auth_views.PasswordContextMixin, TemplateView):
    confirm_url_token = 'set-confirmation'
    success_url = reverse_lazy('blog:login')
    template_name = 'blog/auth/registration/user_registration_confirm_error.html'
    title = _('Registration confirmation error')
    token_generator = default_token_generator

    REGISTRATION_FAILED = 0
    REGISTRATION_NEED_COMPLETE = 1
    REGISTRATION_COMPLETE = 2
    REGISTRATION_CONSISTENCY_VIOLATED = 3

    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        user: User = self.get_user(kwargs['uidb64'])
        if user is not None:
            token = kwargs['token']
            if token == self.confirm_url_token:
                session_token = self.request.session.pop(INTERNAL_REGISTRATION_CONFIRM_SESSION_TOKEN)
                if self.token_generator.check_token(user, session_token):
                    rc = self.check_registration(user)
                    if rc in (self.REGISTRATION_NEED_COMPLETE, self.REGISTRATION_COMPLETE):
                        if rc == self.REGISTRATION_NEED_COMPLETE:
                            # need to finish registration
                            # If the token is valid, will store data that marks registration as completed
                            reg = user.registration_set.first()
                            reg.confirmed = timezone.now()
                            reg.is_active = True
                            try:
                                author = Author(
                                    name=user.get_full_name(),
                                    email=getattr(user, user.EMAIL_FIELD),
                                    user=user
                                )
                                author.save()
                                user.is_active = True
                                user.save()
                            except Exception:
                                raise
                            else:
                                reg.save()
                        # now registration is complete and need to redirect to success_url
                        return HttpResponseRedirect(self.success_url)
            else:
                if self.token_generator.check_token(user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_REGISTRATION_CONFIRM_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.confirm_url_token)
                    return HttpResponseRedirect(redirect_url)

        # this case means the url is invalid or user doesn't registered yet
        # or state of tables not in according to registration's logic
        return super().dispatch(*args, **kwargs)

    def check_registration(self, user: User):
        result = self.REGISTRATION_FAILED
        if user.registration_set:
            regs = user.registration_set.all()
            num_regs = len(regs)
            if num_regs > 1:
                result = self.REGISTRATION_CONSISTENCY_VIOLATED
            elif num_regs == 0:
                result = self.REGISTRATION_FAILED
            elif regs[0].confirmed and regs[0].is_active and user.is_active and hasattr(user, 'author'):
                result = self.REGISTRATION_COMPLETE
            elif not regs[0].confirmed and not regs[0].is_active and not user.is_active and not hasattr(user, 'author'):
                result = self.REGISTRATION_NEED_COMPLETE
            else:
                result = self.REGISTRATION_CONSISTENCY_VIOLATED
        return result

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_context_data(self, **kwargs):
        # this case happens always if the confirmation is failed
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _('Registration confirmation unsuccessful'),
        })
        return context


# stub for lazy_reverse-s
class PasswordResetView(auth_views.PasswordResetView):
    success_url = reverse_lazy('blog:password_reset_done')
    form_class = PasswordResetForm


# stub for lazy_reverse-s
class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('blog:password_reset_complete')
    form_class = SetPasswordForm


# stub for lazy_reverse-s
class PasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('blog:password_change_done')
    form_class = PasswordChangeForm
