from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage
from changes.conf import settings as grunt_settings


register = template.Library()

@register.simple_tag
def grunt_module(module):
    """
    Render A Javascript based on grunt
    :param module:Script filename of js
    :return: Template to render
    """
    if not settings.DEBUG:
        return mark_safe(
            """<script src={module}></script>""".format(
                module=staticfiles_storage.url(grunt_settings.GRUNT_MODULES[module]["out"]),
            )
        )

    scripts = grunt_settings.GRUNT_MODULES[module]["files"]
    out_script = ""
    for script in scripts:
        out_script += mark_safe(
                """<script src="{module}""></script>""".format(
                    module=staticfiles_storage.url(script)
                )
        )

    return out_script
