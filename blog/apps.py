import pathlib

from django.forms.renderers import get_default_renderer, DjangoTemplates
import django.template.backends.django as backend
from django.template import engines

from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'blog'

    def ready(self):
        ################
        # Overriding django forms template
        form_renderer: DjangoTemplates = get_default_renderer()
        backend_engine: backend.DjangoTemplates = form_renderer.engine
        backend_engine.dirs.insert(0, pathlib.Path(self.path).resolve() / 'templates')
        # END of overriding django forms template

        ################
        # Add to templates/blog auth default registration path
        for engine in engines.all():
            engine.dirs.extend([
                pathlib.Path(self.path).resolve() / 'templates',
                pathlib.Path(self.path).resolve() / 'templates' / self.name,
                pathlib.Path(self.path).resolve() / 'templates' / self.name / 'auth'
            ])
