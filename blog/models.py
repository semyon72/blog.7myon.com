import datetime
import itertools
from collections import OrderedDict
from functools import cached_property

from django.db import models
from django.db.models import Manager
from django.utils.text import Truncator
from django.contrib.auth import get_user_model

from . import model_action_urls
from .models_tools import get_full_model_name


# Create your models here.

TEXTFIELD_TRUNCATION_LENGTH = 100
TEXTFIELD_TRUNCATION_STRING = '...'

# This structure was inspired by Django official documentation

UserModel = get_user_model()


class IterableFieldsModelMixin:

    fields_order = None

    class StringableList(list):

        default_separator = ', '

        def __str__(self):
            return self.default_separator.join((str(item) for item in self))

    def create_fields_item(self, name, verbose_name, value, is_pk=None, field=None):
        return {
            'name': name,
            'verbose_name': verbose_name,
            'value': value,
            'is_pk': is_pk,
            '_field': field  # Safe for rendering in templates. Only for debug purposes
        }

    def __iter__(self):

        def get_ordered_fields_gen(fields: dict, order_list: tuple):
            for fname in order_list:
                if fname in fields:
                    yield fields.pop(fname)
                else:
                    continue
            for field in fields.values():
                yield field

        # editable == True
        fields = OrderedDict((field.name, field) for field in self._meta.get_fields() if field.editable is True)
        order_list = self.fields_order if self.fields_order is not None else ()

        for field in get_ordered_fields_gen(fields, order_list):
            # verbose_name - attribute
            # value_from_object(self)
            try:
                value = getattr(self, field.name)
                if isinstance(value, Manager):
                    value = self.StringableList(value.all())

            except AttributeError:
                value = field.value_from_object(self)

            result = self.create_fields_item(
                field.name, field.verbose_name, value,
                self._meta.pk.name == field.name, field
            )

            yield result

    @cached_property
    def fields(self):
        result = OrderedDict()
        for field in self:
            result[field['name']] = field
        for ek, ev in ((k, v) for k, v in vars(self).items() if k not in result and not k.startswith('_')):
            result[ek] = self.create_fields_item(None, ek.replace('_', ' '), ev)
        return result


class BaseBlogModel(model_action_urls.AbsoluteURLActionAwareModelMixin, IterableFieldsModelMixin, models.Model):

    class Meta:
        abstract = True

    @classmethod
    def get_model_name(cls):
        return get_full_model_name(cls)


class Registration(models.Model):

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    registration_email = type(getattr(UserModel, UserModel.get_email_field_name()).field)(
        editable=False,
        blank=False,
        null=False,
        verbose_name='email used at registration stage'
    )
    requested = models.DateTimeField(
        editable=False,
        blank=False,
        null=False,
        default=datetime.datetime.today,
        verbose_name='registration was requested'
    )
    confirmed = models.DateTimeField(
        editable=False,
        null=True,
        default=None,
        verbose_name='registration was confirmed'
    )
    is_active = models.BooleanField(
        editable=False,
        blank=False,
        null=False,
        default=False,
        verbose_name='registration is active'
    )

    def __str__(self):
        return self.user.name


class Blog(BaseBlogModel):

    fields_order = []

    name = models.CharField(
        max_length=100,
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    tagline = models.TextField(
        verbose_name='слоган',  # слоган will used as label in form. In general it changes the field name.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return self.name


class Author(BaseBlogModel):
    user = models.OneToOneField(
        UserModel,
        on_delete=models.SET_DEFAULT, null=True, blank=True, default=None,
        # # SELECT * FROM django_blog.auth_user u LEFT outer join django_blog.blog_author a on a.user_id = u.id
        # # WHERE u.is_superuser = False and a.user_id is null
        # limit_choices_to= models.Q(is_superuser=False, author__isnull=True) & models.Q(author__user_id__isnull=True)
    )
    name = models.CharField(
        max_length=200,
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    email = models.EmailField(
        verbose_name='почтовый адрес',  # will used as label in form. In general it changes the field name.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return self.name


class Entry(BaseBlogModel):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        verbose_name='Блог',  # will used as label in form. In general it changes the field name.
        help_text='',  # will used as input's title attribute to bring helping information
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name='Автор',  # will used as label in form. In general it changes the field name in admin interface.
        help_text='',  # will used as input's title attribute to bring helping information
    )
    coauthors = models.ManyToManyField(
        Author,
        blank=True,
        default=None,
        related_name='entries_as_coauthor_set',
        verbose_name='Соавторы'
    )
    headline = models.CharField(
        max_length=255,
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    create_date = models.DateField(
        editable=False,
        default=datetime.date.today,
        null=False,
        verbose_name='create',  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    pub_date = models.DateField(
        verbose_name='published',  # will used as label in form. In general it changes the field name.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    mod_date = models.DateField(
        default=datetime.date.today,
        verbose_name='modified',  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    inactive = models.BooleanField(
        null=False,
        default=False,
        verbose_name='inactive',  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return self.headline


class EntryText(BaseBlogModel):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, verbose_name='Entry')
    body_text = models.TextField(
        verbose_name='Text of entry',  # will used as label in form. In general it changes the field name in admin interface.
        help_text='Содержимое статьи'  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return Truncator(self.body_text).chars(TEXTFIELD_TRUNCATION_LENGTH, TEXTFIELD_TRUNCATION_STRING)


class EntryComment(BaseBlogModel):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    pub_date = models.DateField(
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    mod_date = models.DateField(
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    comment = models.TextField(
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    inactive = models.BooleanField(
        null=False,
        default=False,
        verbose_name='inactive',  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return Truncator(self.comment).chars(TEXTFIELD_TRUNCATION_LENGTH, TEXTFIELD_TRUNCATION_STRING)


class EntryStat(models.Model):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE, parent_link=True)
    number_of_comments = models.IntegerField(
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    number_of_pingbacks = models.IntegerField(
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    rating = models.IntegerField(
        verbose_name=None,  # will used as label in form. In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return 'pk:{3} comments:{0} pingbacks:{1} rating:{2}'.format(
            self.number_of_comments,
            self.number_of_pingbacks,
            self.rating,
            self.pk
        )
