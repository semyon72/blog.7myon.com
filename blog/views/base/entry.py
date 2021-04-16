# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2020 Oct 17 at 18:31 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.base import ContextMixin

from blog.models import Entry
from blog.forms.base.entry import (
    FilterEntryForm, EntryModelForm
)
from sm_flexdata.views import FilteredListView
from . import CommonGenericViewsAttributeMixin


class EntryView(ContextMixin, FilteredListView):

    template_name = 'blog/staff/entry/list.html'
    default_filter_form = FilterEntryForm
    model = Entry

    def modify_queryset(self, queryset, query_data):
        queryset = queryset.select_related('author', 'blog').prefetch_related('coauthors')
        kwargs = {}

        def add_date_conditions(fname, end_range_fname):
            if query_data[fname] and query_data[end_range_fname]:
                kwargs[fname+'__range'] = (query_data[fname], query_data[end_range_fname])
            elif query_data[end_range_fname]:
                kwargs[fname+'__lte'] = query_data[end_range_fname]
            elif query_data[fname]:
                kwargs[fname+'__gte'] = query_data[fname]

        add_date_conditions('pub_date', 'pub_date_end')
        add_date_conditions('mod_date', 'mod_date_end')
        if query_data['coauthors']:
            entry_author_qs = self.model.coauthors.through.objects.filter(author__in=query_data['coauthors'])
            sub_query = entry_author_qs.distinct().values_list('entry_id', flat=True).query
            queryset = queryset.filter(pk__in=sub_query)

        # now it remains to process ('blog', 'authors', 'headline') fields
        exclude_fields = ('pub_date', 'pub_date_end', 'mod_date', 'mod_date_end', 'coauthors')
        remains_qdata = ((k, v) for k, v in query_data.items() if k not in exclude_fields)
        kwargs.update(self._get_default_kwargs_for_filter(remains_qdata))

        return queryset.filter(**kwargs)

    def get_context(self, queryset=None):
        context = super().get_context(queryset)
        # context['filter_form'].helper = FilterEntryBootstrapFormHelper()
        context['form'] = context['filter_form']
        return context


class EntryCommonAttributesMixin(CommonGenericViewsAttributeMixin):
    model = Entry
    form_class = EntryModelForm


class EntryCreateView(EntryCommonAttributesMixin, CreateView):
    template_name = 'blog/base/entry/edit.html'


class EntryDetailView(EntryCommonAttributesMixin, DetailView):
    template_name = 'blog/base/entry/detail.html'


class EntryUpdateView(EntryCommonAttributesMixin, UpdateView):
    template_name = 'blog/base/entry/edit.html'


class EntryDeleteView(EntryCommonAttributesMixin, DeleteView):
    template_name = 'blog/base/entry/delete.html'


class EntryCommentListView(View):
    pass
