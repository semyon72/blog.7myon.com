# Project: blog_7myon_com
# Package: 
# Filename: blog_extras.py
# Generated: 2020 Oct 17 at 19:19 
# Description of <blog_extras>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django import template
from django.template import RequestContext

register = template.Library()


@register.filter(name='concat')
def concat(val, arg):
    return ''.join([str(val), str(arg)])


def get_real_value(kv, context):
    if not isinstance(kv, str):
        return kv
    sep = '__'
    kvlist = kv.split(sep)
    if len(kvlist) == 1:  # was nothing split
        return kv

    if not kvlist[0]:
        kvlist.pop(0)

    obj = context
    while len(kvlist) > 0:
        attr = kvlist.pop(0)
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
            if callable(obj):
                obj = obj()
        elif hasattr(obj, '__getitem__'):
            obj = obj[attr]
        else:
            raise KeyError('Context does not contain "%s" attribute' % kv)

    return obj


@register.simple_tag(takes_context=True)
def get_querystring(context, *args, **kwargs):
    query_leader = '?'
    if len(args) > 0:
        if args[0] in ('', '&'):
            query_leader = args[0]
        else:
            raise ValueError (
                '"get_querystring" template tag got not supported leading querystring marks.'
                'Tag supports only next set of leading querystring marks ("?", "", "&").'
                'If first positional argument is omitted then "?" will used by default'
            )

    querystring = ''
    if context.request:
        updated = context.request.GET.copy()
        for k, value in kwargs.items():
            rk = get_real_value(k, context)
            if not rk:
                continue
            rk = str(rk)
            rv = get_real_value(value, context)
            if rv is None:
                if rk in updated:
                    del (updated[rk])
                continue
            updated[rk] = rv
        querystring = updated.urlencode()

    return query_leader+querystring if querystring else ''


@register.simple_tag(takes_context=True)
def change_context(context, **kwargs):
    for k, value in kwargs.items():
        context[k] = get_real_value(value, context)
    return ''



