# Project: blog_7myon_com
# Package: 
# Filename: profile.py
# Generated: 2021 Feb 22 at 22:50 
# Description of <profile>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

from ...forms.base.profile import ProfileModelForm
from ...models import Author
from django.contrib.messages.views import SuccessMessageMixin


class ProfileUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'blog/base/profile/edit.html'
    model = Author
    form_class = ProfileModelForm
    # fields = ['name', 'email']
    success_url = reverse_lazy('blog:profile_update')
    success_message = 'Profile was successfully saved.'

    def get_object(self, queryset=None):

        if queryset is None:
            queryset = self.get_queryset()

        queryset = queryset.filter(user=self.request.user.pk)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj



