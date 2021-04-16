# Project: blog_7myon_com
# Package: 
# Filename: middleware.py
# Generated: 2021 Jan 23 at 16:54 
# Description of <middleware>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import abc
import os.path

from django.http.request import HttpRequest

from django.contrib.auth.views import redirect_to_login
from django.urls import reverse, get_script_prefix, path, include, set_urlconf
from django.urls.resolvers import RoutePattern, get_resolver
from django.http import HttpResponse

from . import urls_settings
from . import urls


# Some help...
# django.urls.resolvers.get_resolver() returns resolver for current django project where
# resolver.app_dict contains { app_name: [list namespaces], ... }
# resolver.namesapce_dict contains {namesapce: (url_prefix, URLResolver), ....}
# pattern.match(path) returns 3-tuple ('rest of path from end of matched', re.Match.groups, re.Match.groupdict)
def predict_app_path_prefix(app_name):
    # TODO: not everything was done clearly.
    # app_name is passed from request.resolver_match.app_name
    # sometimes, depends from how many times used include((..., app_name)),
    # app_name can contain 'blog:blog:blog' string. This is confusing.
    resolver = get_resolver()
    urls = []
    for ns in resolver.app_dict[app_name]:
        url, r = resolver.namespace_dict[ns]
        urls.append(str(r.pattern))
    return os.path.commonprefix(urls)


class AbstractRightsChecker(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def is_path_matched(self, request) -> bool:
        return False

    @abc.abstractmethod
    def is_access_allow(self, request) -> bool:
        return True

    @abc.abstractmethod
    def access_allowed(self, request) -> HttpResponse:
        return None

    @abc.abstractmethod
    def access_denied(self, request) -> HttpResponse:
        return None

    @abc.abstractmethod
    def get_response_or_raise_exception(self, request):
        if self.is_path_matched(request):
            if self.is_access_allow(request):
                return self.access_allowed(request)
            else:
                return self.access_denied(request)


class BaseAccessor(AbstractRightsChecker):

    pattern_str = ''

    def get_path_pattern(self, request):
        # pattern_prefix = get_script_prefix()+predict_app_path_prefix(request.resolver_match.app_name)
        return RoutePattern(self.pattern_str)

    def is_path_matched(self, request) -> bool:
        path_pattern = self.get_path_pattern(request)
        return path_pattern.match(request.path) is not None

    def is_access_allow(self, request) -> bool:
        return request.user.is_authenticated

    def access_allowed(self, request) -> HttpResponse:
        return super().access_allowed(request)

    def access_denied(self, request) -> HttpResponse:
        return HttpResponse('You have not access to this area.')

    def get_response_or_raise_exception(self, request):
        return super().get_response_or_raise_exception(request)


class AccessorRedirectToLoginMixin:

    def get_login_url(self):
        return None

    def access_denied(self, request: HttpRequest) -> HttpResponse:
        requested_path = request.get_full_path()
        return redirect_to_login(requested_path, login_url=self.get_login_url())


class BlogBaseAccessor(AccessorRedirectToLoginMixin, BaseAccessor):

    section_name = ''
    allow_also_to = None

    @property
    def pattern_str(self):
        return '/' + urls_settings.construct_default_path_string_for(self.section_name)

    def get_login_url(self):
        return reverse('blog:login')

    def is_access_allow(self, request):
        # for AUTHOR section this almost identically to logic -
        # return super().access_allowed(request)
        # for STAFF section this almost identically to logic -
        # return super().is_access_allow(request) and request.user.is_staff
        compare_with = [self.section_name]
        if hasattr(self, 'allow_also_to'):
            if self.allow_also_to:
                compare_with.append(self.allow_also_to)
        return urls_settings.get_section_for_user(request.user) in compare_with

    def access_allowed(self, request) -> HttpResponse:
        # Now need add appropriate queryset (limited by user) as class attribute
        # and use its in View directly
        view_class = request.resolver_match.func
        # view_class.queryset =

        return super().access_allowed(request)


class AuthorAccessor(BlogBaseAccessor):

    section_name = urls_settings.AUTHOR_NAME
    allow_also_to = urls_settings.STAFF_NAME


class StaffAccessor(BlogBaseAccessor):

    section_name = urls_settings.STAFF_NAME


# it could be inherited from django.utils.deprecation.MiddlewareMixin
class BlogLoginRequiredMiddleware:

    def __init__(self, get_request) -> None:
        # it happens at load middleware stage
        self.get_request = get_request

    def __call__(self, request):
        # it happens at execution of middleware stage
        # right before the next middleware will be executed
        result = self.get_request(request)
        # now we have response that is response
        return result

    @staticmethod
    def _get_accessors():
        accessors = [
            StaffAccessor(),
            AuthorAccessor()
        ]
        return accessors

    def process_view(self, request, view_func, view_args, view_kwargs):
        # it happens right before view will be executed
        # check request path from settings and users.is_staff ....
        for accessor in self._get_accessors():
            if not isinstance(accessor, AbstractRightsChecker):
                raise TypeError('Accessor must implement AbstractRightsChecker type')
            response = accessor.get_response_or_raise_exception(request)
            if response is not None:
                return response
        # if returns None then main flow will not interrupted


class BlogUrlSectionSwitcherMiddleware:

    def __init__(self, get_request) -> None:
        # it happens at load middleware stage
        self.get_request = get_request

    def __call__(self, request):
        # it happens at execution of middleware stage
        # right before the next middleware will be executed

        section = urls_settings.match_sections(request.path)
        if section:
            request.urlconf = (path('', include((urls.urlpatterns_for[section], urls_settings.APP_NAME))),)

        result = self.get_request(request)
        # now, we have response that will be sent back as result of the current request
        return result
