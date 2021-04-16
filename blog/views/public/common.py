# Project: blog_7myon_com
# Package: 
# Filename: common.py
# Generated: 2021 Mar 09 at 21:26 
# Description of <common>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import datetime

from django.db.models import Count, Subquery, OuterRef
from django.views.generic import ListView

from blog.models import Entry


class PublicMostPopularView(ListView):
    paginate_by = 10
    daydelta_kwargs = 'daydelta'

    def get_daydelta(self):
        daydelta = self.kwargs.get(self.daydelta_kwargs, None)
        get_daydelta = self.request.GET.get(self.daydelta_kwargs)
        return daydelta or get_daydelta

    def get_countable_field(self):
        """
            this should return the Entry's field name that will be counted
            for example: this value for Author should be 'author'
            and for Blog should be 'blog'
        """
        return self.model.__name__.lower()

    def get_queryset(self):
        qs = super().get_queryset()
        # Wee need to implement SQL like:
        # SELECT b.*, (
        # 	SELECT count(id)
        # 	FROM blog_entry as e WHERE e.inactive = 0 AND b.id = e.blog_id AND e.pub_date > CURDATE() - 123
        # ) AS cnt
        # FROM blog_blog AS b
        # ORDER BY cnt DESC

        # order values->annotate->values is important
        cfn = self.get_countable_field()
        entry_subqs = Entry.objects.filter(inactive=False).values(cfn).annotate(cnt=Count(cfn)).values('cnt')
        # Now 'entry_subqs' is
        # SELECT COUNT(`blog_entry`.`blog_id`) AS `cnt`
        # FROM `blog_entry` WHERE NOT `blog_entry`.`inactive` GROUP BY `blog_entry`.`blog_id` ORDER BY NULL

        daydelta = self.get_daydelta()
        if daydelta:
            daydelta = datetime.timedelta(days=int(daydelta))
            entry_subqs = entry_subqs.filter(pub_date__gte=datetime.date.today()-daydelta)
        # add the outer reference blog.id == entry.blog_id and having for cnt > 0
        fkwarg = { cfn: OuterRef('pk') }
        entry_subqs = entry_subqs.filter(**fkwarg)

        qs = qs.annotate(entries_count=Subquery(entry_subqs.values('cnt'))).\
            filter(entries_count__gt=0).order_by('-entries_count', 'name')
        # Now qs is (parts that include '...author... or ...blog...' string are variables
        # and it depends on attribute the model)
        # SELECT `blog_blog`.`id`, `blog_blog`.`name`, `blog_blog`.`tagline`,
        # (	SELECT COUNT(U0.`blog_id`) AS `cnt`
        #     FROM `blog_entry` U0
        #     WHERE (NOT U0.`inactive` AND U0.`blog_id` = `blog_blog`.`id`)
        #     GROUP BY U0.`blog_id` ORDER BY NULL
        # ) AS `entries_count`
        # FROM `blog_blog`
        # WHERE
        # (	SELECT COUNT(U0.`blog_id`) AS `cnt`
        #     FROM `blog_entry` U0
        #     WHERE (NOT U0.`inactive` AND U0.`blog_id` = `blog_blog`.`id`)
        #     GROUP BY U0.`blog_id` ORDER BY NULL
        # ) > 0
        # ORDER BY `entries_count` DESC, `blog_blog`.`name` ASC

        return qs
