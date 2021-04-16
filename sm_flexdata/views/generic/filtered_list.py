# Project: blog_7myon_com
# Package: 
# Filename: filtered_list.py
# Generated: 2021 Jan 01 at 10:11 
# Description of <filtered_list>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
import datetime

from django.core.paginator import Paginator
from django.db.models import Model, QuerySet
from django.forms import Form, Field

from django.forms.models import fields_for_model

from django.shortcuts import render, redirect
from django.views.generic import View


class FilteredListView(View):
    default_filter_form = None
    model = None
    page_kwarg = 'page'
    per_page = 20
    session_key = None
    template_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__filter_form = None

    def get_session_key(self):
        return self.session_key or self.__class__.__name__

    def page_number(self):
        # serve session data
        page = self.request.GET.get(self.page_kwarg)
        if page is None:
            sesdata = self.request.session.get(self.get_session_key())
            if sesdata is not None:
                page = sesdata.get(self.page_kwarg)
        else:
            self.request.session.setdefault(self.get_session_key(), {})[self.page_kwarg] = page
            self.request.session.modified = True

        return page

    @staticmethod
    def remove_specific_validators(field: Field):
        # Field.default_validators is default set of validators that specific for certain Field
        # For example: EmailField has as default_validators the EmailValidator
        default_validators_types = tuple(type(validator) for validator in field.default_validators)
        if len(default_validators_types) > 0:
            idx_for_remove = [i for i, v in enumerate(field.validators) if isinstance(v, default_validators_types)]
            for idx in idx_for_remove:
                del field.validators[idx]

    def setup_autogenerated_filter_form(self, fields):
        for field in fields.values():
            field.required = False
            self.remove_specific_validators(field)

    def _get_filter_form(self, *args, **kwargs):
        if self.default_filter_form is not None:
            if isinstance(self.default_filter_form, type):
                form_type = self.default_filter_form
            elif isinstance(self.default_filter_form, (Form,)):
                form_type = type(self.default_filter_form)
            else:
                raise ValueError('"default_filter_form" attribute must be class or instance derived from Form or None')
        else:
            form_fields = fields_for_model(self.model)
            self.setup_autogenerated_filter_form(form_fields)
            form_type = type(''.join(['FilterForm', self.model.__name__, 'Autogenerated']), (Form,), form_fields)

        return form_type(*args, **kwargs) if form_type is not None else None

    def get_session_filter_form(self):
        """
        Returns filter form that bounded data from session and cleaned, or if session data is corrupted
        then clean session and throw exception. If filter form session data is not valid then
        session data will be reset in None also and will be returned filter form with empty bounded data

        :return: Filter form
        """
        session_data = self.request.session.get(self.get_session_key(), {})
        try:
            assert session_data is None or isinstance(session_data, (dict,)), \
                'Session data for {0} is corrupted.' \
                'Session data {1} will be reset to None'.format(self.get_session_key(), session_data)
        except AssertionError as err:
            self.request.session[self.get_session_key()] = None
            self.request.session.save()
            raise err

        form = self._get_filter_form(session_data)
        if not form.is_valid():
            self.request.session[self.get_session_key()] = None
            form = self._get_filter_form({})
            form.is_valid()

        return form

    @property
    def filter_form(self):
        return self.__filter_form

    @filter_form.setter
    def filter_form(self, form: Form):
        if not isinstance(form, (Form,)):
            raise TypeError('"filter_form" attribute must be instance of Form')
        self.__filter_form = form

    @staticmethod
    def serialize_form(form: Form):
        result = {}
        for field_name, value in form.cleaned_data.items():
            html_field_name = form.add_prefix(field_name)
            serialized_value = form.fields[field_name].prepare_value(value)
            if not isinstance(serialized_value, (str, int, float, list, tuple, dict, type(None))):
                serialized_value = str(serialized_value)
            result[html_field_name] = serialized_value
        return result

    def _get_default_kwargs_for_filter(self, query_data):
        kwargs = {}
        if isinstance(query_data, dict):
            query_data = query_data.items()

        for k, v in query_data:
            if not v:
                continue
            key = k
            if isinstance(v, (list, tuple)):
                key += '__in'
            elif isinstance(v, (int, float, datetime.date, bool)):
                pass
            else:
                key += '__icontains'
            kwargs[key] = v

        return kwargs

    def modify_queryset(self, queryset, query_data):
        kwargs = self._get_default_kwargs_for_filter(query_data)
        return queryset.filter(**kwargs)

    @staticmethod
    def form_to_query_data(form: Form):
        result = {}
        for field_name, value in form.cleaned_data.items():
            if isinstance(value, (Model, QuerySet,)):
                value = form.fields[field_name].prepare_value(value)
            result[field_name] = value
        return result

    def get_queryset(self, form=None):
        form = form if form is not None else self.filter_form
        query_data = self.form_to_query_data(form)
        queryset = self.model.objects.all()
        if query_data is not None:
            queryset = self.modify_queryset(queryset, query_data)

        if not queryset.ordered:
            queryset = queryset.order_by(queryset.model._meta.pk.name)

        return queryset

    def get_context(self, queryset=None):
        queryset: QuerySet = queryset if queryset is not None else self.get_queryset()
        paginator = Paginator(object_list=queryset, per_page=self.per_page)
        page_obj = paginator.get_page(self.page_number())
        for idx, obj in enumerate(page_obj.object_list,1):
            obj.object_index = idx

        return {
            'page_obj': page_obj,
            'filter_form': self.filter_form
        }

    def _support_contextmixin(self, current_context, **kwargs):
        # support of django.views.generic.base.ContextMixin
        if hasattr(self,'get_context_data'):
            extra_context = self.get_context_data(**kwargs)
            current_context.update(extra_context)

    def get(self, request, *args, **kwargs):
        self.filter_form = self.get_session_filter_form()
        # context = self.get_context(self.get_queryset(self.filter_form))
        context = self.get_context()
        self._support_contextmixin(context, **kwargs)
        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.filter_form = self._get_filter_form(request.POST)
        if self.filter_form.is_valid():
            # store to session and redirect to myself into get method
            request.session[self.get_session_key()] = self.serialize_form(self.filter_form)
            # redirect to get for clear browser url line
            return redirect('./')

        # have validation error
        context = self.get_context(
            self.get_queryset(self.get_session_filter_form())
        )
        self._support_contextmixin(context, **kwargs)
        return render(self.request, self.template_name, context=context)
