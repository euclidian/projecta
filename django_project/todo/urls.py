# coding=utf-8
"""Urls for submitting github support requests."""
from django.conf.urls import patterns, url
from django.conf import settings

from views import todo

urlpatterns = patterns(
    '',
    # basic app views
    url(r'^todo', todo, name="todo"),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}))
