# Project: blog_7myon_com
# Package: 
# Filename: blog.py
# Generated: 2021 Mar 01 at 20:41 
# Description of <blog>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from blog.models import Blog

from .common import PublicMostPopularView


class PublicMostPopularBlogView(PublicMostPopularView):
    template_name = 'blog/public/blog_aside.html'
    model = Blog
    page_kwarg = 'abp'
