# Project: blog_7myon_com
# Package: 
# Filename: urls.py
# Generated: 2020 Oct 11 at 18:59 
# Description of <urls>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from . import urls_settings as bus


urlpatterns_for = {
    bus.AUTHOR_NAME: [bus.get_path_for_section(bus.AUTH_NAME), bus.get_path_for_section(bus.AUTHOR_NAME)],
    bus.STAFF_NAME: [bus.get_path_for_section(bus.AUTH_NAME), bus.get_path_for_section(bus.STAFF_NAME)]
}

app_name = bus.APP_NAME

_urlpatterns = [
    *urlpatterns_for[bus.STAFF_NAME],
    bus.get_path_for_section(bus.AUTHOR_NAME),
    bus.get_path_for_section(bus.PUBLIC_NAME),
]

urlpatterns = _urlpatterns
