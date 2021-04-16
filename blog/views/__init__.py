# Project: blog_7myon_com
# Package: 
# Filename: __init__.py
# Generated: 2020 Oct 11 at 19:02 
# Description of <__init__.py>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

# ################
# # Overiding django forms template
#
# import pathlib
# form_templates_overloading_dir = pathlib.Path(__file__).parent.parent / 'templates'
#
# # Alternative of above
# # from django.conf import settings
# # backend_engine.dirs.insert(0,settings.BASE_DIR / 'app_name' / 'templates')
#
# from django.forms.renderers import get_default_renderer, DjangoTemplates
# import django.template.backends.django as backend
#
# form_renderer: DjangoTemplates = get_default_renderer()
# backend_engine: backend.DjangoTemplates = form_renderer.engine
#
# backend_engine.dirs.insert(0, form_templates_overloading_dir)
#
# # END of overiding django forms template
# ################
