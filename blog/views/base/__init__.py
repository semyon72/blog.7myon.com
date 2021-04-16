# Project: blog_7myon_com
# Package: 
# Filename: __init__.py
# Generated: 2021 Jan 26 at 17:30 
# Description of <__init__.py>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from urllib.parse import urlparse

from django.urls import reverse_lazy

from ...models_tools import get_full_model_name
from ...model_action_urls import (
    MODEL_ACTION_URL_NAMES as MODEL_ACTION_URLS,
    URL_ACTION_LIST_KEY as URL_LIST_ACTION_KEY,
    URL_ACTION_CREATE_KEY, URL_ACTION_UPDATE_KEY, URL_ACTION_DELETE_KEY, URL_ACTION_READ_KEY,
)


LAST_VISITED_URL_USING_GET_METHOD_SESSION_KEY = 'last_visited_url_using_get_method'


class CommonGenericViewsAttributeMixin:
    pk_url_kwarg = 'id'
    success_url = None

    def setup(self, request, *args, **kwargs):
        if request.method == 'GET' :
            referer = request.headers.get('referer')
            purl = urlparse(referer)
            skips = (URL_ACTION_CREATE_KEY, URL_ACTION_UPDATE_KEY, URL_ACTION_DELETE_KEY, URL_ACTION_READ_KEY)
            if not any(1 for sufix in skips if purl.path.endswith('/'+sufix.rstrip('/'))):
                request.session[LAST_VISITED_URL_USING_GET_METHOD_SESSION_KEY] = referer
        super().setup(request, *args, **kwargs)

    def get_success_url(self, model=None):
        if not self.success_url:
            if model is None:
                if self.request.method == 'POST':
                    lsgurl = self.request.session.get(LAST_VISITED_URL_USING_GET_METHOD_SESSION_KEY)
                    if lsgurl:
                        return lsgurl

                model = self.model

            self.success_url = reverse_lazy(MODEL_ACTION_URLS[get_full_model_name(model)][URL_LIST_ACTION_KEY][0])
        return super().get_success_url()

