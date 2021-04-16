# Project: blog_7myon_com
# Package: 
# Filename: urls_names.py
# Generated: 2021 Feb 13 at 12:12 
# Description of <urls_names>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import posixpath

from django.urls import path, get_script_prefix, include
from django.contrib.auth.models import User

APP_NAME = 'blog'

AUTHOR_NAME = 'author'
STAFF_NAME = 'staff'
AUTH_NAME = 'auth'
PUBLIC_NAME = 'public'


def construct_default_path_string_for(section: str = AUTHOR_NAME) -> str:
    """
        returns instance default pathstring for section,
        by default section is AUTHOR_NAME = 'author'
        it means path string that will match to path that started from
        "APP_NAME/AUTHOR_NAME/" not from "/APP_NAME/AUTHOR_NAME/"
    :param section:
    :return:
    """
    return '%s/%s/' % (APP_NAME, section)


def get_default_urlpatterns_module_name_for(section_name: str = AUTHOR_NAME):
    """
        Just returns APP_NAME + '.urls_' + section_name (module name).
        This little bit not consistent to get_pattern_for
        where section can contain any strings that compatible with url syntax
    :param section_name:
    :return: constructed module name which should contain the declared urlpatterns array
    """
    return APP_NAME + '.urls_%s' % section_name


def get_path_for_section(section=AUTH_NAME):
    if section not in (PUBLIC_NAME, AUTH_NAME, AUTHOR_NAME, STAFF_NAME):
        raise ValueError(
            'Names of sections that have support are {0},{1},{2},{3}'.format(PUBLIC_NAME, AUTH_NAME, AUTHOR_NAME, STAFF_NAME)
        )
    return path(
        construct_default_path_string_for(section),
        include(get_default_urlpatterns_module_name_for(section))
    )


def match_sections(path, sections=None):
    """
        By default it will test Request.path on belonging to sections AUTHOR_NAME or STAFF_NAME
        If all by default then it just will test if path starts from
        'blog/author' or 'blog/staff'
    :param sections: iterable
    :param path: str
    :return: Matched section name
    """
    sections = sections or (AUTHOR_NAME, STAFF_NAME)
    for section in sections:
        pattern_str = posixpath.sep + construct_default_path_string_for(section)
        if path.startswith(pattern_str):
            return section

    return False


def get_section_for_user(user: User):
    if user.is_authenticated and not user.is_superuser:
        if user.is_staff:
            return STAFF_NAME
        else:
            return AUTHOR_NAME


def get_url_for_section(user: User, url):
    section = get_section_for_user(user)
    if not section:
        return url if url is not None else ''

    if not url:
        # construct_default_path_string_for() returns relative path always
        return posixpath.sep + construct_default_path_string_for(section)

    # path de-normalization stage
    isabs_url = posixpath.isabs(url)
    if isabs_url:
        url: str = url[len(posixpath.sep):]

    # now url and section_path are relative both
    url_parts = url.split(posixpath.sep)
    url_parts_len = len(url_parts)
    if url_parts_len > 0:
        if url_parts[0] == APP_NAME:
            # need to test section is allowed
            if url_parts_len > 1 and url_parts[1] in (AUTHOR_NAME, STAFF_NAME):
                url = posixpath.sep.join((APP_NAME, section, *url_parts[2:]))
        else:
            url = posixpath.sep.join((APP_NAME, section, *url_parts))

    return url if not isabs_url else posixpath.sep + url
