# Project: blog_7myon_com
# Package: 
# Filename: middleware_current_request.py
# Generated: 2021 Feb 25 at 14:55 
# Description of <middleware_current_request>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import threading

_current_thread_locals = threading.local()


def set_current_request(request):
    _current_thread_locals.request = request


def get_current_request():
    if hasattr(_current_thread_locals, 'request'):
        return _current_thread_locals.request
    raise ValueError('probably you forgot to invoke the "set_current_request" earlier')


# it could be inherited from django.utils.deprecation.MiddlewareMixin
class CurrentRequestMiddleware:

    def __init__(self, get_request) -> None:
        # it happens at load middleware stage
        self.get_request = get_request

    def __call__(self, request) -> None:
        # it happens at load middleware stage
        return self.get_request(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # it happens right before view will be executed
        # check request path from settings and users.is_staff ....
        set_current_request(request)
