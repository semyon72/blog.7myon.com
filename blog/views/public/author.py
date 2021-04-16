# Project: blog_7myon_com
# Package: 
# Filename: blog.py
# Generated: 2021 Mar 01 at 20:41 
# Description of <blog>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from blog.models import Author

from .common import PublicMostPopularView


class PublicMostPopularAuthorView(PublicMostPopularView):
    template_name = 'blog/public/author_aside.html'
    model = Author
    page_kwarg = 'aap'
