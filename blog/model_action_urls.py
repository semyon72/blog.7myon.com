# Project: blog_7myon_com
# Package: 
# Filename: model_action_urls.py
# Generated: 2021 Jan 29 at 21:42 
# Description of <model_action_urls>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import functools
from collections.abc import Mapping

from django.db import models
from django.urls import reverse
from django.utils.module_loading import import_string

from . import middleware_current_request as current_request
from .models_tools import get_full_model_name

from . import urls_settings


URL_ACTION_LIST_KEY = 'list'
URL_ACTION_CREATE_KEY = 'create'
URL_ACTION_READ_KEY = 'read'  # means detail
URL_ACTION_UPDATE_KEY = 'update'
URL_ACTION_DELETE_KEY = 'delete'
URL_ACTION_RELATED_LIST_KEY = 'related_list'
URL_ACTION_RELATED_CREATE_KEY = 'related_create'
URL_ACTION_RELATED_READ_KEY = 'related_read'  # means detail
URL_ACTION_RELATED_UPDATE_KEY = 'related_update'
URL_ACTION_RELATED_DELETE_KEY = 'related_delete'


_MODELNAME_ACTION_URL_NAMES = {
        'blog.models.Blog': {
            URL_ACTION_LIST_KEY: ('blog:blog_list', None),
            URL_ACTION_CREATE_KEY: ('blog:blog_create', None),
            URL_ACTION_READ_KEY: ('blog:blog_read', {'id': 'pk'}),
            URL_ACTION_UPDATE_KEY: ('blog:blog_update', {'id': 'pk'}),
            URL_ACTION_DELETE_KEY: ('blog:blog_delete', {'id': 'pk'}),
        },
        'blog.models.Author': {
            URL_ACTION_LIST_KEY: ('blog:author_list', None),
            URL_ACTION_CREATE_KEY: ('blog:author_create', None),
            URL_ACTION_READ_KEY: ('blog:author_read', {'id': 'pk'}),
            URL_ACTION_UPDATE_KEY: ('blog:author_update', {'id': 'pk'}),
            URL_ACTION_DELETE_KEY: ('blog:author_delete', {'id': 'pk'}),
        },
        'blog.models.Entry': {
            URL_ACTION_LIST_KEY: ('blog:entry_list', None),
            URL_ACTION_CREATE_KEY: ('blog:entry_create', None),
            URL_ACTION_READ_KEY: ('blog:entry_read', {'id': 'pk'}),
            URL_ACTION_UPDATE_KEY: ('blog:entry_update', {'id': 'pk'}),
            URL_ACTION_DELETE_KEY: ('blog:entry_delete', {'id': 'pk'}),
            URL_ACTION_RELATED_LIST_KEY: ('blog:entry_text_list', {'entry_id': 'pk'}),
            URL_ACTION_RELATED_CREATE_KEY: ('blog:entry_text_create', {'entry_id': 'pk'}),
        },
        'blog.models.EntryText': {
            URL_ACTION_LIST_KEY: ('blog:entrytext_list', None),
            URL_ACTION_CREATE_KEY: ('blog:entrytext_create', None),
            URL_ACTION_READ_KEY: ('blog:entrytext_read', {'id': 'pk'}),
            URL_ACTION_UPDATE_KEY: ('blog:entrytext_update', {'id': 'pk'}),
            URL_ACTION_DELETE_KEY: ('blog:entrytext_delete', {'id': 'pk'}),
        },
    }


class ModelActionURLNamesProxy(Mapping):

    def __init__(self) -> None:
        self._modelname_action_url_names_orig = _MODELNAME_ACTION_URL_NAMES
        self._model_action_url_names = None
        self.modelname_to_module_map = {}

    def __lazy_init(self):
        if self._model_action_url_names is None:
            self._model_action_url_names = {}
            for model_name, settings_dict in self._modelname_action_url_names_orig.items():
                model = import_string(model_name)
                self.modelname_to_module_map[model_name] = model
                self._model_action_url_names[model] = settings_dict
        return self

    def __len__(self) -> int:
        return len(self.__lazy_init()._model_action_url_names)

    def __iter__(self):
        return iter(self.__lazy_init()._model_action_url_names)

    def __getitem__(self, item):
        self.__lazy_init()
        if isinstance(item, str):
            if item in self.modelname_to_module_map:
                return self._modelname_action_url_names_orig[item]
            else:
                raise AttributeError('_MODEL_ACTION_URL_NAMES has now item %s' % item)
        elif issubclass(item, models.Model):
            if item in self._model_action_url_names:
                return self._model_action_url_names[item]
            else:
                raise AttributeError('_MODEL_ACTION_URL_NAMES has now item for model %s' % type(item).__qualname__)
        else:
            raise TypeError('Supported types only are str - module name or instances of Model type. '
                            'But gotten type is %s' % type(item).__qualname__)


# MODEL_ACTION_URL_NAMES = ModelActionURLNamesProxy()
MODEL_ACTION_URL_NAMES = _MODELNAME_ACTION_URL_NAMES


class UrlifyModelDescriptor:

    default_action_name = URL_ACTION_LIST_KEY

    def __init__(self):
        self._instance = None
        self._cache = {}  # cache for not parametrized urls, for parametrized using lru_cache ....
        self._owner_checked = False

    def _check_owner(self, owner) -> None:
        if self._owner_checked:
            return

        owner_full_name = '.'.join((owner.__module__, owner.__qualname__))
        if not issubclass(owner, models.Model):
            raise TypeError('It may be applied only to descendants of %s class.' % owner_full_name)
        model_settings = MODEL_ACTION_URL_NAMES.get(owner_full_name, None)
        if model_settings:
            for action_settings in model_settings.values():
                # indexes: 0 - is url_name; 1 - is url_param -> model_field_name map
                if action_settings[1]:
                    for url_param, model_field_name in action_settings[1].items():
                        found_fields = tuple(
                            field for field in owner._meta.fields
                            if field.name == model_field_name or (
                                    getattr(owner._meta, model_field_name).name == field.name
                            )
                        )
                        if len(found_fields) == 0:
                            raise ValueError(
                                'Model %s has no field "%s" that pointed in MODEL_ACTION_URL_NAMES.' %
                                (owner_full_name, model_field_name)
                            )
        else:
            raise ValueError('MODEL_ACTION_URL_NAMES has no information about %s model.' % owner_full_name)

        self._owner_checked = True

    def __get__(self, instance: models.Model, owner=None):
        if not instance:
            # it has invoked in cls context
            self._check_owner(owner)
        else:
            self._check_owner(type(instance))
            self._instance = instance

        return self

    @property
    def model_name(self):
        model_name = get_full_model_name(self._instance)
        assert model_name in MODEL_ACTION_URL_NAMES, 'model "%s" not in MODEL_ACTION_URL_NAMES' % model_name
        return model_name

    def _get_action_settings(self, action_name=None):
        if not action_name:
            action_name = self.default_action_name

        model_name = self.model_name
        assert action_name in MODEL_ACTION_URL_NAMES[model_name],\
            'action "%s" not in MODEL_ACTION_URL_NAMES[%s]' % (action_name, model_name)

        return MODEL_ACTION_URL_NAMES[model_name][action_name]

    def _get_viewname(self, action_key=None):
        action_settings = self._get_action_settings(action_key)
        return action_settings[0] # [0] is viewname

    def _get_reverse_kwargs(self, action_key=None):
        reverse_kwargs = {}

        action_settings = self._get_action_settings(action_key)
        if action_settings[1]:
            for url_param, model_field_name in action_settings[1].items():
                reverse_kwargs[url_param] = getattr(self._instance, model_field_name)

        return reverse_kwargs

    def _get_base_cache_key_parts(self, action_key=None):
        return self._get_viewname(action_key),

    # small trick: _lru_cache_reverse_func works only if invoked like
    # type(self)._lru_cache_reverse_func(without self)
    @functools.lru_cache(1024)
    def _lru_cache_reverse_func(viewname, **kwargs):
        return reverse(viewname, kwargs=kwargs)

    def __getattr__(self, action_key):
        # item is URL_ACTION_****_KEY-s
        base_cache_key_parts = self._get_base_cache_key_parts(action_key)
        reverse_kwargs = self._get_reverse_kwargs(action_key)
        return type(self)._lru_cache_reverse_func(*base_cache_key_parts, **reverse_kwargs)


class SectionedUrlifyModelDescriptor(UrlifyModelDescriptor):

    def _get_base_cache_key_parts(self, action_key=None):
        viewname, = super()._get_base_cache_key_parts(action_key)
        section =  urls_settings.match_sections(current_request.get_current_request().path)
        if section is False:
            section = None
        return section, viewname

    @functools.lru_cache(1024)
    def _lru_cache_reverse_func(*args, **kwargs):
        return reverse(args[1], kwargs=kwargs)


class AbsoluteURLActionAwareModelMixin:

    urls = SectionedUrlifyModelDescriptor()

    def get_absolute_url(self: models.Model):
        try:
            super_get_absolute_url = super().get_absolute_url
        except AttributeError:
            url = getattr(self.urls, URL_ACTION_READ_KEY)
            return url
        else:
            return super_get_absolute_url()
