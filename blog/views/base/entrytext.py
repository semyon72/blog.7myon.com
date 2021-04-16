# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2020 Oct 17 at 18:31 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.base import ContextMixin

from blog.models import EntryText
from blog.forms.base.entry import (
    FilterEntryTextForm, EntryTextModelForm
)
from sm_flexdata.views import FilteredListView
from . import CommonGenericViewsAttributeMixin


class EntryTextView(ContextMixin, FilteredListView):

    template_name = 'blog/staff/entrytext/list.html'
    default_filter_form = FilterEntryTextForm
    model = EntryText

    def modify_queryset(self, queryset, query_data):
        # SELECT `blog_entrytext`.`id`, `blog_entrytext`.`entry_id`, `blog_entrytext`.`body_text`,
        #  (SELECT COUNT(*) AS `cnt`
        #   FROM `blog_entrytext` U0
        #   WHERE U0.`entry_id` = `blog_entrytext`.`entry_id`
        #   GROUP BY U0.`entry_id` ORDER BY NULL) AS `text_for_entry_count`
        # FROM `blog_entrytext`
        # implementation of above SQL
        # subq = EntryText.objects.values('entry').annotate(cnt=Count('*')).values('cnt').filter(entry=OuterRef('entry'))
        # resqs = qs.annotate(text_for_entry_count=Subquery(subq))
        return super().modify_queryset(queryset, query_data)

    def get_context(self, queryset=None):
        context = super().get_context(queryset)
        context['form'] = context['filter_form']
        return context


class EntryTextCommonAttributesMixin(CommonGenericViewsAttributeMixin):
    model = EntryText
    form_class = EntryTextModelForm


class EntryTextCreateView(EntryTextCommonAttributesMixin, CreateView):
    template_name = 'blog/staff/entrytext/edit.html'


class EntryTextDetailView(EntryTextCommonAttributesMixin, DetailView):
    template_name = 'blog/staff/entrytext/detail.html'


class EntryTextUpdateView(EntryTextCommonAttributesMixin, UpdateView):
    template_name = 'blog/staff/entrytext/edit.html'


class EntryTextDeleteView(EntryTextCommonAttributesMixin, DeleteView):
    template_name = 'blog/staff/entrytext/delete.html'
