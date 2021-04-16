# Project: blog_7myon_com
# Package: 
# Filename: widgets.py
# Generated: 2020 Oct 14 at 20:39 
# Description of <widjets>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.forms.widgets import Widget


class PlainText(Widget):
    template_name = 'django/forms/widgets/plain_text.html'

    def use_required_attribute(self, initial)->bool:
        return False

    def id_for_label(self, id_):
        return None

    def get_context(self, name, value, attrs: dict):
        attrs.pop('id', None)
        context = super().get_context(name, value, attrs)
        return context

    def subwidgets(self, name, value, attrs=None):
        return super().subwidgets(name, value, attrs)

