# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2020 Oct 17 at 18:31 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.forms.models import ModelForm
from blog.models import Entry, EntryText
from blog.forms.base.entry import (
    EntryTextModelForm,
)

from sm_flexdata.html.form_elements import FlexFormMixin
from . import CommonGenericViewsAttributeMixin


class EntryTextByEntryCommonMixin(CommonGenericViewsAttributeMixin):
    model = EntryText
    pk_url_kwarg = 'id'
    pk_url_entry_id_kwarg = 'entry_id'
    current_entry = None

    def _test_queryset_more_than_one(self, qs: QuerySet):
        if qs.count() < 1:
            raise Http404('No %s matches the given query.' % qs.model._meta.object_name)
        return qs

    def get_queryset(self):
        qs = super().get_queryset()
        entry_id = self.kwargs.get(self.pk_url_entry_id_kwarg)
        return qs.filter(entry=entry_id)

    def get_current_entry(self):
        if self.current_entry is None:
            self.current_entry = get_object_or_404(Entry, pk=self.kwargs.get(self.pk_url_entry_id_kwarg))
        return self.current_entry

    def get_context_data(self, *, object_list=None, **kwargs):
        rkwargs = super().get_context_data(object_list=object_list, **kwargs)
        if 'current_entry' not in rkwargs:
            rkwargs['current_entry'] = self.get_current_entry()
        return rkwargs


class EntryTextByEntryListView(EntryTextByEntryCommonMixin, ListView):
    template_name = 'blog/base/entrytext_by_entry/list.html'
    paginate_by = 2
    ordering = None
    allow_empty = True

    # def get_queryset(self):
    #     return self._test_queryset_more_than_one(super().get_queryset())

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):
        paginator = super().get_paginator(queryset, per_page, orphans, allow_empty_first_page, **kwargs)

        def get_page(number):
            try:
                number = paginator.validate_number(number)
            except PageNotAnInteger:
                number = 1
            except EmptyPage:
                number = paginator.num_pages
            return type(paginator).page(paginator, number)

        paginator.page = get_page
        return paginator


class BodytextOnlyEntryTextModelForm(FlexFormMixin, ModelForm):
    # Exclusion of general rules
    # fields = ['body_text'] is not using together with form_class in ModelFormMixin
    # but we need use FlexFormMixin for form bootstrap4 representation
    # therefore we need hide all fields exclude 'body_text'
    class Meta(EntryTextModelForm.Meta):
        model = EntryText
        fields = ['body_text']


class EntryTextByEntryCreateView(EntryTextByEntryCommonMixin, CreateView):
    template_name = 'blog/base/entrytext_by_entry/edit.html'
    form_class = BodytextOnlyEntryTextModelForm
    # fields = ['body_text']

    def get_queryset(self):
        return self._test_queryset_more_than_one(super().get_queryset())

    def get_context_data(self, **kwargs):
        rkwargs = super().get_context_data(**kwargs)
        if 'form' in rkwargs and not hasattr(rkwargs['form'].instance, 'entry'):
            setattr(rkwargs['form'].instance, 'entry', rkwargs['current_entry'])

        return rkwargs

    def form_valid(self, form):
        if not hasattr(form.instance, 'entry'):
            form.instance.entry = self.get_current_entry()

        return super().form_valid(form)


class EntryTextByEntryDetailView(EntryTextByEntryCommonMixin, DetailView):
    template_name = 'blog/base/entrytext_by_entry/detail.html'


class EntryTextByEntryUpdateView(EntryTextByEntryCommonMixin, UpdateView):
    template_name = 'blog/base/entrytext_by_entry/edit.html'
    form_class = BodytextOnlyEntryTextModelForm
    # fields = ['body_text']


class EntryTextByEntryDeleteView(EntryTextByEntryCommonMixin, DeleteView):
    template_name = 'blog/base/entrytext_by_entry/delete.html'
