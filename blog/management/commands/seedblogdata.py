# Project: blog_7myon_com
# Package: 
# Filename: seedblogdata.py
# Generated: 2021 Jan 17 at 08:52 
# Description of <seedblogdata>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import random
import math
import functools
import datetime as dt

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Model
from django.contrib.auth.models import User
from faker import Faker

import blog.models as blm


class Command(BaseCommand):

    help = 'Seeds, random generated data into database of blog application.'

    fake = Faker()
    default_users_filter_kwargs = {'is_staff': False, 'is_superuser': False}

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self._data_were_cleared = False

    def is_data_were_cleared(self):
        return self._data_were_cleared

    def _get_as_need(self, model, creator, num=0, filter_kwargs=None):
        if not num:
            return tuple()
        kwargs = {}
        if filter_kwargs is not None:
            kwargs.update(filter_kwargs)
        qs = model.objects.filter(**kwargs)
        cnt = qs.count()
        result = random.sample(list(qs), min(cnt, num))
        if len(result) < num:
            result.extend(creator(num - len(result)))
        return result

    def _create_users(self,num=0):
        for i in range(num):
            user_name = self.fake.unique.user_name()
            yield User.objects.create_user(
                username=user_name,
                email= user_name+'@'+self.fake.free_email_domain(),
                password='!2QwAsZx',
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
            )

    def _get_users(self,num=0):
        return self._get_as_need(User, self._create_users, num, self.default_users_filter_kwargs)

    @functools.cached_property
    def users(self, num=12):
        users = {}
        for user in self._get_users(num):
            users[user.username] = user
        return users

    def _create_authors(self, num=0):
        r_num = range(num)
        need_user_relations = (random.randint(0, 1) for x in r_num)
        iusers = iter(self.users.values())
        for i in r_num:
            user, author = (None, None)
            if next(need_user_relations, None):
                user = next(iusers, None)

            if not author:
                email = user.email if user is not None else self.fake.free_email()
                name = user.get_full_name().title() if user is not None else self.fake.name()
                author = blm.Author(email = email, name= name, user=user)
                author.save()
            yield author

    def _get_authors(self, num=0):
        return self._get_as_need(blm.Author, self._create_authors, num)

    @functools.cached_property
    def authors(self, num=15):
        return self._get_authors(num)

    def _create_blogs(self, num=0):
        # elements = ('PHP', 'Python', 'C#', 'C++', 'Java', 'C', 'JavaScript')
        from ._blog_name_tagline_provider import blog_name_tagline_generator
        blog_name_tagline_cache = []
        blog_name_tagline_gen = blog_name_tagline_generator()
        for i in range(num):
            try:
                tagline, blog_name = next(blog_name_tagline_gen)
                blog_name_tagline_cache.append((tagline, blog_name))
            except StopIteration:
                self.fake.random_element(blog_name_tagline_cache)
            blog = blm.Blog(name=blog_name, tagline = tagline)
            blog.save()
            yield blog

    def _get_blogs(self, num=0):
        return self._get_as_need(blm.Blog, self._create_blogs, num)

    @functools.cached_property
    def blogs(self, num=15):
        return self._get_blogs(num)

    def _create_registration(self, num=0):
        authors_ready_for_registration = [*blm.Author.objects.exclude(
            email__in=blm.Registration.objects.values_list('registration_email'),
        ).filter(user__isnull=False)]
        assert len(authors_ready_for_registration) >= num, 'available authors ready for registration less than need'

        for i in range(num):
            author = authors_ready_for_registration[i]
            requested = self.fake.past_date(dt.date.today()-dt.timedelta(days=45))
            confirmed = requested + dt.timedelta(minutes=random.randint(5, 25))
            is_active = True  # probably it can be randomized
            user = author.user

            assert user is not None, 'something went wrong. user must be'

            requested = user.date_joined
            confirmed = user.date_joined + dt.timedelta(minutes= random.randint(5,25))

            kwargs = {
                'registration_email': author.email,
                'requested': requested,
                'confirmed': confirmed,
                'is_active': is_active,
                'user': user,
            }
            registration = blm.Registration(**kwargs)
            registration.save()
            yield registration

    def _get_registrations(self):
        # at this stage
        # registrations must contain as many rows as Authors table contains
        # if author exists then he must be inside those that are registered
        authors_for_filter = tuple(filter(
                None, map(lambda author: author.email if author.user else None, self.authors)
            )
        )

        num = len(authors_for_filter)
        filter_kwargs = {
            'registration_email__in': authors_for_filter,
        }

        # It is necessary to create a separate mode to create additional unregistered users
        return self._get_as_need(blm.Registration, self._create_registration, num, filter_kwargs)

    @functools.cached_property
    def registrations(self):
        return self._get_registrations()

    def _create_entry_items(self, entry, get_entry_item_object_func, max_num=5):
        r_max_num = range(1, max_num+1)
        weights = tuple(map(lambda v: math.ceil(1/math.exp(v)*100), r_max_num))
        _100weights = tuple(map(lambda v: math.ceil(v/sum(weights)*100), weights))
        rnum = random.choices(r_max_num, _100weights, k=1)[0]
        get_entry_item_objects = []
        for i in range(rnum):
            get_entry_item_object = get_entry_item_object_func(entry)
            get_entry_item_object.entry = entry
            get_entry_item_object.save()
            get_entry_item_objects.append(get_entry_item_object)

        return get_entry_item_objects

    def create_entry_texts(self, entry: blm.Entry, max_num=5):
        # create EntryText and relate it with entry
        return self._create_entry_items(
            entry,
            lambda entry: blm.EntryText(body_text=self.fake.text(random.randint(250,750))),
            max_num
        )

    def create_entry_comments(self, entry: blm.Entry, max_num=5):
        # create EntryText and relate it with entry
        def create_comment(entry):
            pub_date = max(entry.pub_date, entry.create_date)
            kwargs = {
                'pub_date': pub_date,
                'mod_date': pub_date + dt.timedelta(days=random.randint(0,15)),
                'inactive': random.choices((False, True), (85, 15))[0],
                'comment': self.fake.text(),
            }
            return blm.EntryComment(**kwargs)

        return self._create_entry_items(
            entry,
            create_comment,
            max_num
        )

    def create_entry_stat(self, entry:blm.Entry, number_of_comments=None):
        entry_stat = blm.EntryStat(
            entry=entry,
            number_of_comments= entry.entrycomment_set.count() if number_of_comments is None else number_of_comments,
            number_of_pingbacks = random.randint(0,15),
            rating = random.randint(0,100)
        )
        entry_stat.save()
        return entry_stat

    def _get_entry_dates(self, default_interval = dt.timedelta(days=45)):
        pub_date = mod_date = create_date = self.fake.past_date(dt.date.today() - default_interval)
        if random.choices((False, True), (55, 45)):  # all dates are not same as create_date - 45%
            if random.choices((False, True), (65, 35)):  # mod_date > pub_date - was edited after publication
                mod_date = self.fake.past_date(create_date)
                pub_date = self.fake.date_between(create_date, mod_date)
            elif random.choices((False, True), (85, 15)):  # mod_date < pub_date - publication in future - 15%
                pub_date = self.fake.future_date(dt.date.today() + default_interval)
                mod_date = self.fake.date_between(create_date, pub_date)
            else:  # mod_date < pub_date - publication in past - 85%
                pub_date = self.fake.past_date(dt.date.today())
                mod_date = self.fake.date_between(create_date, pub_date)

        assert (create_date <= dt.date.today() and create_date <= mod_date and
                create_date <= pub_date and mod_date <= dt.date.today()), 'date generation logic is wrong'

        return {'create_date': create_date, 'mod_date': mod_date, 'pub_date': pub_date}

    def create_entry(self, num=50):
        for i in range(num):
            kwargs = {
                'author': random.choice(self.authors),
                'blog': random.choice(self.blogs),
                'headline': self.fake.text(254),
                'inactive' : random.choices((False, True), (85, 15))[0] # probability of appearance of True is 15%
            }
            kwargs.update(self._get_entry_dates())

            entry = blm.Entry(**kwargs)
            entry.save()
            entry_texts = self.create_entry_texts(entry)
            entry_comments = self.create_entry_comments(entry)
            entry_stat = self.create_entry_stat(entry, len(entry_comments))

            num_coautors = min(len(self.authors), random.choices((0, 1, 2, 3), (80, 12, 6, 2))[0])
            coautors = random.sample(self.authors, num_coautors)
            if coautors:
                entry.coauthors.set(coautors)
            # need generator of EntryText, EntryComment, EntryStat do send(entry)
            yield entry

    def _get_m2m_through_table_names(self, model: Model ):
        result = []
        if model._meta.local_many_to_many:
            for m2mfield in model._meta.local_many_to_many:
                m2m_descriptor = getattr(model, m2mfield.name)
                result.append(m2m_descriptor.through._meta.db_table)
        return result

    def clear_blog_data(self):
        models = (
            blm.EntryText, blm.EntryComment, blm.EntryStat,
            blm.Entry, blm.Blog, blm.Author, blm.Registration
        )
        for model in models:
            from django.db import connection
            table_name = model._meta.db_table

            table_names = self._get_m2m_through_table_names(model)
            table_names.append(table_name)
            with connection.cursor() as cursor:
                for table_name in table_names:
                    affected_rows = cursor.execute("DELETE FROM %s;" % table_name)
                    if affected_rows:
                        connection.commit()
                    self.stdout.write('table {0} deleted {1} rows'.format(table_name, affected_rows))

    def add_arguments(self, parser):
        parser.add_argument(
            '-cb','--clearbefore', action='store_true',
            help='Seeds fake data but it clears all tables before.'
        )
        parser.add_argument(
            '-co','--clearonly', action='store_true',
            help='Just clears the tables. It doesn\'t seed the database tables.'
        )

    def handle(self, *args, **options):
        if options['clearonly']:
            self.clear_blog_data()
            return

        if options['clearbefore']:
            self.clear_blog_data()

        self.registrations
        [*self.create_entry()]
