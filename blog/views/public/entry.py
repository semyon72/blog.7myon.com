# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2021 Mar 03 at 08:37 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import functools
import re

from django.core.paginator import Paginator, Page
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from django.urls import reverse
from django.utils.html import MLStripper

from sm_flexdata.html.contenttools import HTMLTruncator, TextTruncator, StringTruncator
from ...models import Entry


def strip_tags(s, convert_charrefs=False):
    if not isinstance(s, (str, bytes, bytearray)):
        raise TypeError('Parameter should be str type.')
    if not s:
        return ''
    else:
        p = MLStripper()
        p.convert_charrefs = bool(convert_charrefs)
        p.feed(s)
        return p.get_data()


def create_patterns_for_re_sub(texts, text_prefix, text_suffix):
    """
    Returns 2-tuple
       0 - '^(.*)(text1)(.*)(text2)(.*)$' as list
       1 - '\g<1>text_prefix\g<2>text_suffix\g<3>text_prefix\g<4>text_suffix\g<5>' as list

    :param texts: list of texts that should be wrapped into text_prefix and text_suffix parts
    :param text_prefix:
    :param text_suffix:
    :return:
    """
    p_list = ['('+re.escape(str(t).strip())+')' for t in texts if str(t).strip()]
    back_ref = r'\g<%s>'
    pattern, replace = [], []
    for i in range(len(p_list) * 2 + 1):
        p = r'(.*)'
        bp_items = [back_ref % str(i + 1)]
        if i % 2 > 0:
            p = p_list[i // 2]
            bp_items.insert(0, text_prefix)
            bp_items.append(text_suffix)
        pattern.append(p)
        replace.append(''.join(bp_items))

    if pattern:
        pattern.append(r'$')
        pattern.insert(0, r'^')

    return pattern, replace


def highlight_found_text(text: str,
                         search_text,
                         found_text_prefix='<span class="found-text">',
                         found_text_suffix='</span'
                         ):
    if not hasattr(search_text, '__iter__') or isinstance(search_text, str):
        search_text = str(search_text).split()

    result = text
    if search_text:
        pattern, replace = create_patterns_for_re_sub(
            search_text, found_text_prefix, found_text_suffix
        )
        result = mark_safe(
            re.sub(''.join(pattern), ''.join(replace), text, flags=re.I | re.S)
        )

    return result


class PublicEntryDetailView(DetailView):
    template_name = 'blog/public/entry_detail.html'
    model = Entry
    pk_url_kwarg = 'id'

    object_kwarg = 'entry'
    page_kwarg = 'text'  # ListView.page_kwarg  # -> 'page'

    truncate_text_to_length = None
    truncate_text_to_length_url_kwarg = 'tl'

    search_text_url_kwarg = 'q'
    found_text_prefix = '<span class="found-text">'
    found_text_suffix = '</span>'

    _VIEW_NAME_KEY = 'view_name'
    _URL_KEY = 'url'
    _URL_PARAMS_KEY = 'url_params'

    view_names = {
        # 'author': {_VIEW_NAME_KEY: 'blog:public_index_author'},
        # 'blog': {_VIEW_NAME_KEY: 'blog:public_index_blog'},
        'entry': {_VIEW_NAME_KEY: 'blog:public_entry_read'},
    }

    def _common_callback(self, view_name_info, context, object_field_name=None):
        obj = context['object']
        if isinstance(object_field_name, str) and object_field_name:
            obj = getattr(context['object'], object_field_name)
        url_params = {'id': obj.pk}
        view_name_info[self._URL_PARAMS_KEY] = url_params
        view_name_info[self._URL_KEY] = reverse(
            view_name_info[self._VIEW_NAME_KEY],
            kwargs=url_params
        )
        return view_name_info

    def _author_callback(self, view_name_info, context):
        return self._common_callback(view_name_info, context, 'author')

    def _blog_callback(self, view_name_info, context):
        return self._common_callback(view_name_info, context, 'blog')

    def _entry_callback(self, view_name_info, context):
        return self._common_callback(view_name_info, context)

    def _get_view_names(self, context):
        result = {}
        for n, vn in self.view_names.items():
            ncallback = getattr(self, '_%s_callback' % n, None)
            if callable(ncallback):
                vn = ncallback(vn, context)
            result[n] = vn
        return result

    @functools.cached_property
    def get_truncate_text_to_length(self):
        btl = self.truncate_text_to_length
        getbtl = self.request.GET.get(self.truncate_text_to_length_url_kwarg, None)
        return int(getbtl or btl or 0)

    @functools.cached_property
    def search_text(self):
        return self.request.GET.get(self.search_text_url_kwarg, '').strip()

    def get_entrytext_queryset(self, entry):
        qs = entry.entrytext_set.all()
        # tl = self.get_truncate_text_to_length
        # if tl > 0:
        #     qs = qs.annotate(
        #         body_text_truncated=functions.Concat(
        #             functions.Substr('body_text', 1, tl),
        #             Value(' .....'),
        #             output_field=TextField()
        #         )
        #     )
        return qs

    def get_object(self, queryset=None):
        obj = self.kwargs.get(self.object_kwarg)
        if obj is not None and isinstance(obj, self.model):
            return obj
        return super().get_object(queryset)

    def _process_body_text(self, entrytext_page: Page):
        if len(entrytext_page) < 1:
            return

        truncator, tl = (HTMLTruncator(), self.get_truncate_text_to_length)
        truncator.ellipsis.tag = 'span'
        truncator.ellipsis.attrs = {'class': 'truncated-text'}
        truncator.ellipsis.add_data(StringTruncator.ellipsis)

        ellipsis, search_text = (StringTruncator.ellipsis, self.search_text)
        text_truncator = TextTruncator(needles=search_text.split())
        text_truncator.result_max_length = tl if tl > 0 else -1

        if tl > 0:
            truncator.max_plain_text_length = tl
            StringTruncator.ellipsis = '%s%s%s' % ('<span class="truncated-text">', ellipsis, '</span>')

        for i, entrytext in enumerate(entrytext_page.object_list):
            if i > 0:
                truncator.reset()

            if search_text:
                text_truncator.haystack=strip_tags(entrytext.fields['body_text']['value'])
                fk = 'body_text_highlighted'
                fv = mark_safe(str(text_truncator))
                entrytext.fields[fk] = entrytext.create_fields_item(None, fk.replace('_', ' ').capitalize(), fv)

            entrytext.fields['body_text']['value'] = str(truncator.feed(entrytext.fields['body_text']['value']))

        # return to back
        if tl:
            StringTruncator.ellipsis = ellipsis

    def _process_headline(self, entry):
        # headline = strip_tags(entry.fields['headline']['value'])
        headline = entry.fields['headline']['value']
        entry.fields['headline']['value'] = \
            highlight_found_text(headline, self.search_text, self.found_text_prefix, self.found_text_suffix)

    def get_paginated_entrytext(self, entry):
        qs = self.get_entrytext_queryset(entry)
        paginator = Paginator(qs.order_by('pk'), 1)
        return paginator.get_page(self.request.GET.get(self.page_kwarg, 1))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = context['object']
        entrytext_page_obj = self.get_paginated_entrytext(entry)
        context['entrytext_page_obj'] = entrytext_page_obj
        self._process_body_text(entrytext_page_obj)
        self._process_headline(entry)

        context['view_names'] = self._get_view_names(context)
        return context
