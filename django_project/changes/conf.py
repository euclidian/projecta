from django.conf import settings as django_settings

class LazySettings(object):

    @property
    def GRUNT_MODULES(self):
        return getattr(django_settings, "GRUNT_MODULES", {})