# Project: blog_7myon_com
# Package: 
# Filename: index.py
# Generated: 2021 Mar 10 at 16:03 
# Description of <index>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db.models import fields, Case, When, F, Value, Subquery, OuterRef, Sum, functions
from django.shortcuts import get_object_or_404
from django.utils.html import mark_safe
from django.views.generic import ListView, DetailView

from .author import PublicMostPopularAuthorView
from .blog import PublicMostPopularBlogView
from .entry import PublicEntryDetailView
from ...models import Entry, Author, Blog, EntryText
from ...models_tools import Regexp, IContains, StripTags


class PublicIndexAsideContentMixin:

    def _get_aside_content(self, view_class, daydelta=None):
        kwargs = {
            view_class.daydelta_kwargs: daydelta
        }
        template_response = view_class.as_view()(self.request, **kwargs)
        return mark_safe(
            template_response.render().content.decode(encoding=template_response.charset)
        )

    def _get_aside_context_data(self, view_class, context_key='aside', daydeltas=None):
        """
        :param context_key: something like - 'blog_aside'
        :param daydeltas: something like (None, 7, 30, 365)
        :return:
        """
        if not daydeltas:
            daydeltas = (None,)

        context_kwargs = (
            (context_key+'_'+('full' if not daydelta else (str(daydelta)+'days')), daydelta)
            for daydelta in daydeltas
        )
        aside_context_data = {}
        for ckey, daydelta in context_kwargs:
            aside_context_data[ckey] = self._get_aside_content(view_class, daydelta)

        return aside_context_data

    def get_aside_context(self):
        view_settings = (
            # (PublicMostPopularBlogView, (None, 7, 30, 365)), # (...7, 30, 365) 'redundant information'
            (PublicMostPopularBlogView, None),
            (PublicMostPopularAuthorView, None)
        )
        result = {}
        for view_class, daydeltas in view_settings:
            context_key = view_class.model.__name__.lower()+'_aside'
            result.update(self._get_aside_context_data(view_class, context_key, daydeltas))
        return result

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['aside_content'] = self.get_aside_context()
        return context


class PublicIndexView(PublicIndexAsideContentMixin, ListView):
    template_name = 'blog/public/index.html'
    paginate_by = 10
    model = Entry
    ordering = ['-pub_date']

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):
        paginator = super().get_paginator(queryset, per_page, orphans, allow_empty_first_page, **kwargs)
        paginator._page = paginator.page

        # copied from Paginator.get_page(self, number):
        def _get_page(page_number=1):
            try:
                number = paginator.validate_number(page_number)
            except PageNotAnInteger:
                number = 1
            except EmptyPage:
                number = paginator.num_pages
            return paginator._page(number)

        paginator.page = _get_page
        return paginator

    def get_entry_detail_content(self, entry, truncate_text_to_length=None):
        view_names = {
            'author': {PublicEntryDetailView._VIEW_NAME_KEY: 'blog:public_index_author'},
            'blog': {PublicEntryDetailView._VIEW_NAME_KEY: 'blog:public_index_blog'},
            'entry': {PublicEntryDetailView._VIEW_NAME_KEY: 'blog:public_index_entry'},
        }
        template_response = PublicEntryDetailView.as_view(
            truncate_text_to_length=truncate_text_to_length,
            view_names=view_names,
        )(self.request, **{PublicEntryDetailView.object_kwarg: entry})

        return mark_safe(template_response.render().content.decode(encoding=template_response.charset))

    def entry_detail_contents_to_entries(self, entries, truncate_text_to_length=256):
        if len(entries) > 0:
            orig_mutable = self.request.GET._mutable
            if not orig_mutable:
                self.request.GET._mutable = True
            page_kwarg = PublicEntryDetailView.page_kwarg
            orig_page = self.request.GET.pop(page_kwarg, None)

            for entry in entries:
                entry.entry_detail_content = self.get_entry_detail_content(entry, truncate_text_to_length)

            if orig_page is not None:
                self.request.GET.setlist(page_kwarg, orig_page)
            self.request.GET._mutable = orig_mutable

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        entries = context.get('object_list', [])
        self.entry_detail_contents_to_entries(entries)

        return context


class PublicIndexByAuthorView(PublicIndexView):
    object_kwarg = 'id'
    object_model = Author

    def get_object(self):
        obj = self.kwargs.get(self.object_kwarg)
        if obj is not None and isinstance(obj, self.model):
            return obj
        return get_object_or_404(self.object_model, pk=obj)

    def get_queryset(self):
        queryset = self.get_object().entry_set.all().filter(inactive=False)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


class PublicIndexByBlogView(PublicIndexByAuthorView):
    object_model = Blog


class PublicIndexEntryView(PublicIndexAsideContentMixin, DetailView):

    template_name = PublicIndexView.template_name
    model = Entry
    pk_url_kwarg = 'id'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        entry = context.get('object')
        entry.entry_detail_content = PublicIndexView.get_entry_detail_content(self, entry)  # None or 0 means the all content
        return context


class PublicIndexSearchView(PublicIndexView):
    """ This view needs in stored function 'strip_tags'
        Implementation for MySQL

        /* https://stackoverflow.com/a/13346684 */
        DROP FUNCTION IF EXISTS strip_tags;
        DELIMITER |
        CREATE FUNCTION strip_tags($str text) RETURNS text
        BEGIN
            DECLARE $start, $end INT DEFAULT 1;
            LOOP
                SET $start = LOCATE("<", $str, $start);
                IF (!$start) THEN RETURN $str; END IF;
                SET $end = LOCATE(">", $str, $start);
                IF (!$end) THEN SET $end = $start; END IF;
                SET $str = INSERT($str, $start, $end - $start + 1, "");
            END LOOP;
        END; |
        DELIMITER ;

        Test
        SELECT STRIP_TAGS('<span>hel<b>lo <a href="world">wo<>rld</a> <<x>again<.') REGEXP '.*Hello.+wo.+ag.*' as `clean_text`;
    """
    search_kwarg = 'q'
    headline_cost = 50
    body_text_cost = 35

    def _get_value_expression(self):
        q = self.request.GET.get(self.search_kwarg, None)
        if q:
            return [v for v in q.split() if v]

    def get_queryset(self):
        # Need to implement - This more optimized query -
        # duration of execution on 100.000 rows of entries and 160.713 rows of entrytext is 10.593 sec - 11.109 sec
        # if to make use LIKE '%on_%world%' instead of REGEXP '.*on.+world.*' then will be faster, in practice
        # SELECT *
        # FROM (
        # SELECT `blog_entry`.`id`, `blog_entry`.`blog_id`, `blog_entry`.`author_id`,
        #  `blog_entry`.`headline`, `blog_entry`.`create_date`, `blog_entry`.`pub_date`,
        #  `blog_entry`.`mod_date`, `blog_entry`.`inactive`,
        #  COALESCE((
        #     SELECT SUM(0.35) AS `rank`
        #     FROM `blog_entrytext` U0
        #     WHERE (
        #         (STRIP_TAGS(U0.`body_text`) REGEXP '.*on.+world.*')
        #         AND U0.`entry_id` = `blog_entry`.`id`
        #     ) GROUP BY U0.`entry_id` ORDER BY NULL
        # ), 0.0) AS `text_rank`,
        # CASE WHEN (`blog_entry`.`headline` REGEXP '.*on.+world.*') THEN 0.5 ELSE 0.0 END AS `entry_rank`
        # FROM `blog_entry`
        # WHERE NOT `blog_entry`.`inactive`
        # ) as r
        # WHERE r.text_rank + r.entry_rank > 0
        # ORDER BY r.text_rank + r.entry_rank DESC, r.pub_date DESC
        val = self._get_value_expression()
        qs = super().get_queryset()
        if val is not None:
            sq_bt_rank = EntryText.objects.filter(
                # body_text__striptags__iregex=val,
                # Regexp(StripTags(F('body_text')), val),
                IContains(StripTags(F('body_text')), val),
                entry=OuterRef('pk')
            ).values('entry').annotate(rank=Sum(self.body_text_cost, output_field=fields.IntegerField())).values('rank')

            qs = qs.annotate(
                text_rank=functions.Coalesce(Subquery(sq_bt_rank), 0, output_field=fields.IntegerField()),
                # entry_rank=Case(When(Regexp(F('headline'), val), then=Value(50)), default=Value(0), output_field=fields.IntegerField()),
                entry_rank=Case(When(IContains(F('headline'), val), then=Value(self.headline_cost)), default=Value(0), output_field=fields.IntegerField()),
                total_rank=F('text_rank')+F('entry_rank')
            ).filter(inactive=False, total_rank__gt=0).order_by('-total_rank', '-pub_date')

            # Now query is - But this query is less optimized than above "Need to implement" -
            # duration of execution on 100.000 rows of entries and 160.713 rows of entrytext is 24.719 sec - 29.219 sec
            # SELECT `blog_entry`.`id`, `blog_entry`.`blog_id`, `blog_entry`.`author_id`,
            # `blog_entry`.`headline`, `blog_entry`.`create_date`, `blog_entry`.`pub_date`,
            # `blog_entry`.`mod_date`, `blog_entry`.`inactive`,
            # COALESCE((SELECT SUM(0.35e0) AS `rank` FROM `blog_entrytext` U0 WHERE ((STRIP_TAGS(U0.`body_text`) REGEXP '.*ce.+pl.*') AND U0.`entry_id` = `blog_entry`.`id`) GROUP BY U0.`entry_id` ORDER BY NULL), 0.0e0) AS `text_rank`,
            # CASE WHEN (`blog_entry`.`headline` REGEXP '.*ce.+pl.*') THEN 0.5e0 ELSE 0.0e0 END AS `entry_rank`,
            # (COALESCE((SELECT SUM(0.35e0) AS `rank` FROM `blog_entrytext` U0 WHERE ((STRIP_TAGS(U0.`body_text`) REGEXP '.*ce.+pl.*') AND U0.`entry_id` = `blog_entry`.`id`) GROUP BY U0.`entry_id` ORDER BY NULL), 0.0e0) + CASE WHEN (`blog_entry`.`headline` REGEXP '.*ce.+pl.*') THEN 0.5e0 ELSE 0.0e0 END) AS `total_rank`
            # FROM `blog_entry`
            # WHERE (
            # NOT `blog_entry`.`inactive`
            # AND (COALESCE((SELECT SUM(0.35e0) AS `rank` FROM `blog_entrytext` U0 WHERE ((STRIP_TAGS(U0.`body_text`) REGEXP '.*ce.+pl.*') AND U0.`entry_id` = `blog_entry`.`id`) GROUP BY U0.`entry_id` ORDER BY NULL), 0.0e0)
            #     + CASE WHEN (`blog_entry`.`headline` REGEXP '.*ce.+pl.*') THEN 0.5e0 ELSE 0.0e0 END) > 0.0e0
            # )
            # ORDER BY `total_rank` DESC, `blog_entry`.`pub_date` DESC

        return qs.prefetch_related('author', 'blog', 'coauthors')

    def add_found_info(self, entry):
        found_entries = entry.fields.get('entry_rank', {}).get('value', 0) // self.headline_cost
        found_entrytexts = entry.fields.get('text_rank', {}).get('value', 0) // self.body_text_cost
        if found_entries + found_entrytexts > 0:
            fi = {'found_entries': found_entries, 'found_entrytexts': found_entrytexts}
            k = 'rank_info'
            entry.fields[k] = entry.create_fields_item(None, k.replace('_', ' '), fi)

    def get_entry_detail_content(self, entry, truncate_text_to_length=None):
        self.add_found_info(entry)
        return super().get_entry_detail_content(entry, truncate_text_to_length)
