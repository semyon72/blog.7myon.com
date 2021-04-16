# Project: blog_7myon_com
# Package: 
# Filename: urls_public.py
# Generated: 2021 Mar 01 at 20:53 
# Description of <urls_public>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.urls import path, include
from .views.public import author, blog, entry, index

blog_urls = [
    path('aside/', blog.PublicMostPopularBlogView.as_view(), name='public_blog_aside'),
]

author_urls = [
    path('aside/', author.PublicMostPopularAuthorView.as_view(), name='public_author_aside'),
]

entry_urls = [
    path('<int:id>/read/', entry.PublicEntryDetailView.as_view(), name='public_entry_read'),
]

index_urls = [
    path('', index.PublicIndexView.as_view(), name='public_index'),
    path('search/', index.PublicIndexSearchView.as_view(), name='public_index_search'),
    path('author/<int:id>/', index.PublicIndexByAuthorView.as_view(), name='public_index_author'),
    path('blog/<int:id>/', index.PublicIndexByBlogView.as_view(), name='public_index_blog'),
    path('entry/<int:id>/', index.PublicIndexEntryView.as_view(), name='public_index_entry'),
]

urlpatterns = [
    path('blog/', include(blog_urls)),
    path('author/', include(author_urls)),
    path('entry/', include(entry_urls)),
    path('index/', include(index_urls)),
]
