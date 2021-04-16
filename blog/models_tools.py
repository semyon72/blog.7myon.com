# Project: blog_7myon_com
# Package: 
# Filename: models_tools.py
# Generated: 2021 Feb 25 at 10:13 
# Description of <models_tools>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import functools
from django.db.backends.mysql.compiler import SQLCompiler
from django.db.models import lookups
from django.db.models import fields, Expression
from django.db.models import Value, CharField, TextField


def get_full_model_name(model):
    if not isinstance(model, type):
        model = type(model)

    return '.'.join((model.__module__, model.__qualname__))


# ##### PublicIndexSearchView #####

class LookupedExpression(Expression):
    """
        'lhs command rhs'
    """
    template = '%s%s%s'  # 1-expression, 2-command, 3-value'
    add_brackets = False
    command = None

    def __rand__(self, other):
        super().__rand__(other)

    def __ror__(self, other):
        super().__ror__(other)

    def _is_expression(self, expr, rise_exception=True):
        error_message = '%r is not an Expression'
        result = False
        if not hasattr(expr, 'resolve_expression'):
            if rise_exception:
                raise TypeError(error_message % expr)
        else:
            result = True
        return result

    def __init__(self, expression, value, output_field=None):
        self._is_expression(expression)

        if output_field is None:
            output_field = fields.BooleanField()

        super().__init__(output_field=output_field)
        self.source_expressions = None
        self.set_source_expressions([expression])
        self.value = value

    def copy(self):
        clone = super().copy()
        clone.set_source_expressions(self.get_source_expressions())
        clone.value = self.value
        return clone

    def get_source_expressions(self):
        return self.source_expressions

    def set_source_expressions(self, expressions):
        self.source_expressions = self._parse_expressions(*expressions)

    def get_template(self, compiler, connection):
        return self.template

    def get_command(self, compiler, connection):
        return self.command

    def process_command(self, compiler, connection):
        command = self.get_command(compiler, connection)
        if command is None:
            command = ''

        sql_part, params = '', []
        if hasattr(command, 'resolve_expression'):
            sql_part, params = compiler.compile(command)
        elif isinstance(command,str):
            command = command.strip()
            if command:
                sql_part = ' '+command.upper()+' '
        else:
            raise TypeError('Command is not Expression or string')
        return sql_part, params

    def _prepare_value(self, value, compiler, connection ):
        """
            Must return Expression
        """
        if isinstance(value, str):
            value = Value(value)
        return value

    def as_sql(self, compiler: SQLCompiler, connection):
        lhs, lhs_params = compiler.compile(self.get_source_expressions()[0])

        value = self._prepare_value(self.value, compiler, connection)
        self._is_expression(value)
        rhs, rhs_params = compiler.compile(value)

        cmd, cmd_params = self.process_command(compiler, connection)

        sql_parts = (lhs, rhs)
        sql_params = lhs_params + rhs_params
        if cmd:
            sql_parts = (lhs, cmd, rhs)
            sql_params = lhs_params + cmd_params + rhs_params

        return self.get_template(compiler, connection) % sql_parts, sql_params


class Regexp(LookupedExpression):

    def get_template(self, compiler, connection):
        return '('+connection.ops.regex_lookup('regexp')+')'


class IContains(LookupedExpression):

    def _prepare_value(self, value, compiler, connection):
        value = super()._prepare_value(value, compiler, connection)
        if self._is_expression(value, False):
            return value
        elif isinstance(value, (tuple, list)):
            safe_values_for_like = []
            for v in value:
                safe_values_for_like.append(connection.ops.prep_for_like_query(v))
            value = '_%'.join(safe_values_for_like)
        return Value(value)

    # copied from lookups.PatternLookup.get_rhs_op() and customized for our case
    def _get_rhs_op(self, connection, rhs, original_self = None):
        # all cases that different from our case, when rhs is expression always, were removed
        # Cause that _prepare_value always returns Value()
        pattern = connection.pattern_ops[original_self.lookup_name].format('{}')
        return pattern.format(rhs)

    # copied from lookups.PatternLookup.process_rhs() and customized for our case
    def _process_rhs(self, qn, connection, original_self = None):
        # all cases that different from our case, when rhs is expression always, were removed
        # Cause that _prepare_value always returns Value()
        return super(type(original_self), original_self).process_rhs(qn, connection)

    def as_sql(self, compiler: SQLCompiler, connection):
        rhs = self._prepare_value(self.value, compiler, connection)
        icontains = lookups.IContains(self.get_source_expressions()[0], rhs)
        # redefinition of instance methods
        icontains.get_rhs_op = functools.partial(self._get_rhs_op, original_self=icontains)
        icontains.process_rhs = functools.partial(self._process_rhs, original_self=icontains)
        # invoke icontains.as_sql() or as_vendor_name()
        # with redefined get_rhs_op and process_rhs methods
        return compiler.compile(icontains)

class StripTags(lookups.Transform):
    lookup_name = 'striptags'
    function = 'STRIP_TAGS'

    def __rand__(self, other):
        super().__rand__(other)

    def __ror__(self, other):
        super().__ror__(other)


CharField.register_lookup(StripTags)
TextField.register_lookup(StripTags)


