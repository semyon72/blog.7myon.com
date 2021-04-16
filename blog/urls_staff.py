# Project: blog_7myon_com
# Package: 
# Filename: staff_urls.py
# Generated: 2021 Jan 25 at 15:48 
# Description of <staff_urls>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.urls import path, include
from blog.views.staff import (
    author, blog, entry, entrytext, entrytext_by_entry as entriedtext, profile
)


author_urls = [
    path('', author.AuthorView.as_view(), name='author_list'),
    path('create/', author.AuthorCreateView.as_view(), name='author_create'),
    path('<int:id>/read/', author.AuthorDetailView.as_view(), name='author_read'),
    path('<int:id>/update/', author.AuthorUpdateView.as_view(), name='author_update'),
    path('<int:id>/delete/', author.AuthorDeleteView.as_view(), name='author_delete'),
]

blog_urls = [
    path('', blog.BlogView.as_view(), name='blog_list'),
    path('create/', blog.BlogCreateView.as_view(), name='blog_create'),
    path('<int:id>/read/', blog.BlogDetailView.as_view(), name='blog_read'),
    path('<int:id>/update/', blog.BlogUpdateView.as_view(), name='blog_update'),
    path('<int:id>/delete/', blog.BlogDeleteView.as_view(), name='blog_delete'),
]

entry_urls = [
    path('', entry.EntryView.as_view(), name='entry_list'),
    path('create/', entry.EntryCreateView.as_view(), name='entry_create'),
    path('<int:id>/read/', entry.EntryDetailView.as_view(), name='entry_read'),
    path('<int:id>/update/', entry.EntryUpdateView.as_view(), name='entry_update'),
    path('<int:id>/delete/', entry.EntryDeleteView.as_view(), name='entry_delete'),
    path('<int:entry_id>/text/', entriedtext.EntryTextByEntryListView.as_view(), name='entry_text_list'),
    path('<int:entry_id>/text/create/', entriedtext.EntryTextByEntryCreateView.as_view(), name='entry_text_create'),
    path('<int:entry_id>/text/<int:id>/read', entriedtext.EntryTextByEntryDetailView.as_view(), name='entry_text_read'),
    path('<int:entry_id>/text/<int:id>/update', entriedtext.EntryTextByEntryUpdateView.as_view(), name='entry_text_update'),
    path('<int:entry_id>/text/<int:id>/delete', entriedtext.EntryTextByEntryDeleteView.as_view(), name='entry_text_delete'),
    path('<int:id>/comment/', entry.EntryCommentListView.as_view(), name='entry_comment_list'),
]

entrytext_urls = [
    path('', entrytext.EntryTextView.as_view(), name='entrytext_list'),
    path('create/', entrytext.EntryTextCreateView.as_view(), name='entrytext_create'),
    path('<int:id>/read/', entrytext.EntryTextDetailView.as_view(), name='entrytext_read'),
    path('<int:id>/update/', entrytext.EntryTextUpdateView.as_view(), name='entrytext_update'),
    path('<int:id>/delete/', entrytext.EntryTextDeleteView.as_view(), name='entrytext_delete'),
]

profile_urls = [
    path('', profile.ProfileUpdateView.as_view(), name='profile_update')
]

urlpatterns = [
    path('', include(profile_urls)),
    path('author/', include(author_urls)),
    path('blog/', include(blog_urls)),
    path('entry/', include(entry_urls)),
    path('entrytext/', include(entrytext_urls)),
]