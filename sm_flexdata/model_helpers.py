# Project: blog_7myon_com
# Package: 
# Filename: model_helpers.py
# Generated: 2021 Jan 27 at 14:16 
# Description of <model_helpers>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.db.models import Model, QuerySet
from django.forms.utils import pretty_name
from django.db.models.manager import Manager


def model_to_data(instance: Model, include_pk=False, include_hidden=False):
    """
        Returns list of 2-tuples [pretty_name(model_field.verbose_name), [value,...]), ]
    :param instance:
    :param include_pk:
    :param include_hidden:
    :return: Returns list of 2-tuples [pretty_name(model_field.verbose_name), [value,...]), ]
    """
    opts = instance._meta
    data = []
    for f in opts.get_fields(include_hidden=include_hidden):
        if opts.pk.name == f.name and not include_pk:
            continue
        if not getattr(f, 'editable', False):
            continue
        attr = getattr(instance, f.name)
        rv = []
        if isinstance(attr, Manager):
            for sv in attr.all():
                rv.append(str(sv))
        elif isinstance(attr, (Model, bool)):
            rv.append(str(attr))
        else:
            rv.append(attr if attr else '')

        data.append((pretty_name(f.verbose_name),rv))
    return data


def queryset_to_data(queryset: QuerySet, omit_duplicates=False, include_pk=False, include_hidden=False):
    """
        Returns the list of 2-tuple where each element is pk value and result of get_widget_data_from_form(...)
        In other words [(pk, [pretty_name(model_field.verbose_name), [value,...]), ]), .... ]

    :param queryset: Iterable where each item is instance of some Model
    :param include_hidden: Boolean value. If False (by default) then hidden fields will not be included in result
    :param include_pk: Boolean value. If False (by default) then pk field will not be included in result
    :return: Returns the list of 2-tuple [(pk, [pretty_name(model_field.verbose_name), [value,...]), ]), .... ]
    """
    pk_name = None
    ids = set()
    data = []
    for idx, inst in enumerate(queryset):
        if idx == 0:
            pk_name = inst._meta.pk.name

        pk_value = idx
        if pk_name:
            pk_value = getattr(inst,pk_name)
            if omit_duplicates and pk_value in ids:
                continue

        ids.add(pk_value)
        data.append((pk_value, model_to_data(inst, include_pk, include_hidden)))

    return data
