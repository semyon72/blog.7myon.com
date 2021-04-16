# Project: blog_7myon_com
# Package: 
# Filename: author_urls.py
# Generated: 2021 Jan 25 at 21:52 
# Description of <author_urls>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from pprint import pprint

from django.urls import path, include
from blog.views.base import entry, entrytext_by_entry as entriedtext, entrytext

entry_urls = [
    path('', entry.EntryView.as_view(), name='entry_list'),
    path('create/', entry.EntryCreateView.as_view(), name='entry_create'),
    path('<int:id>/read/', entry.EntryDetailView.as_view(), name='entry_read'),
    path('<int:id>/update/', entry.EntryUpdateView.as_view(), name='entry_update'),
    path('<int:id>/delete/', entry.EntryDeleteView.as_view(), name='entry_delete'),
    path('<int:entry_id>/text/', entriedtext.EntryTextByEntryListView.as_view(), name='entry_text_list'),
    path('<int:entry_id>/text/create/', entriedtext.EntryTextByEntryCreateView.as_view(), name='entry_text_create'),
    path('<int:entry_id>/text/<int:id>/read', entriedtext.EntryTextByEntryDetailView.as_view(), name='entry_text_read'),
    path('<int:entry_id>/text/<int:id>/update', entriedtext.EntryTextByEntryUpdateView.as_view(),
         name='entry_text_update'),
    path('<int:entry_id>/text/<int:id>/delete', entriedtext.EntryTextByEntryDeleteView.as_view(),
         name='entry_text_delete'),
    path('<int:id>/comment/', entry.EntryCommentListView.as_view(), name='entry_comment_list'),
]

entrytext_urls = [
    path('', entrytext.EntryTextView.as_view(), name='entrytext_list'),
    path('create/', entrytext.EntryTextCreateView.as_view(), name='entrytext_create'),
    path('<int:id>/read/', entrytext.EntryTextDetailView.as_view(), name='entrytext_read'),
    path('<int:id>/update/', entrytext.EntryTextUpdateView.as_view(), name='entrytext_update'),
    path('<int:id>/delete/', entrytext.EntryTextDeleteView.as_view(), name='entrytext_delete'),
]


urlpatterns = [
    path('entry/', include(entry_urls)),
    path('entrytext/', include(entrytext_urls)),
    path('debug/', include((
        [
            path('test', lambda request: pprint(request), name='author_test'),
            path('test1', lambda request: pprint(request), name='author_test1')
        ], 'app_name'), namespace='ns'
    ))
]