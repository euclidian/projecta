# coding=utf-8
"""Version related views."""
# noinspection PyUnresolvedReferences
import logging
from base.models import Project

LOGGER = logging.getLogger(__name__)

import re
import zipfile
import StringIO
import pypandoc

from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    RedirectView)

from django.http import HttpResponseRedirect, HttpResponse
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from pure_pagination.mixins import PaginationMixin

from ..models import Version
from ..forms import VersionForm


class VersionMixin(object):
    """Mixing for all views to inherit which sets some standard properties."""
    model = Version  # implies -> queryset = Entry.objects.all()
    form_class = VersionForm


class VersionListView(VersionMixin, PaginationMixin, ListView):
    """View for the list of versions."""
    context_object_name = 'versions'
    template_name = 'version/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        """Get the context data which is passed to a template.

        :param kwargs: Any arguments to pass to the superclass.
        :type kwargs: dict

        :returns: Context data which will be passed to the template.
        :rtype: dict
        """
        context = super(VersionListView, self).get_context_data(**kwargs)
        context['num_versions'] = self.get_queryset().count()
        context['unapproved'] = False
        return context

    def get_queryset(self):
        """Get the queryset for this view.

        :returns: A queryset which is filtered to only show approved versions.
        :rtype: QuerySet
        """
        versions_qs = Version.approved_objects.all()
        return versions_qs


class VersionDetailView(VersionMixin, DetailView):
    """A tabular list style view for a version."""
    context_object_name = 'version'
    template_name = 'version/detail.html'

    def get_queryset(self):
        """Get the queryset for this view.

        :returns: A queryset which is filtered to only show approved versions.
        :rtype: QuerySet
        """
        versions_qs = Version.approved_objects.all()
        return versions_qs

    def get_object(self, queryset=None):
        """
        Get the object for this view.
        Because Version slugs are unique within a Project, we need to make
        sure that we fetch the correct Version from the correct Project
        """
        if queryset is None:
            queryset = self.get_queryset()
            slug = self.kwargs.get('slug', None)
            project_slug = self.kwargs.get('project_slug', None)
            if slug and project_slug:
                project = Project.objects.get(slug=project_slug)
                obj = queryset.get(project=project, slug=slug)
                return obj
            else:
                raise Http404('Sorry! We could not find your version!')


class VersionMarkdownView(VersionDetailView):
    """Return a markdown version detail."""
    template_name = 'version/detail.md'

    def render_to_response(self, context, **response_kwargs):
        """Render this version as markdown.

        :param context: Context data to use with template.
        :type context: dict

        :param response_kwargs: A dict of arguments to pass to the renderer.
        :type response_kwargs: dict

        :returns: A rendered template with mime type application/text.
        :rtype: HttpResponse
        """
        response = super(VersionMarkdownView, self).render_to_response(
            context,
            mimetype='application/text',
            **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename="foo.md"'
        return response


class VersionThumbnailView(VersionMixin, DetailView):
    """A contact sheet style list of thumbs per entry."""
    context_object_name = 'version'
    template_name = 'version/detail-thumbs.html'

    def get_context_data(self, **kwargs):
        """Get the context data which is passed to a template.

        :param kwargs: Any arguments to pass to the superclass.
        :type kwargs: dict

        :returns: Context data which will be passed to the template.
        :rtype: dict
        """
        context = super(VersionThumbnailView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        """Get the queryset for this view.

        :returns: A queryset which is filtered to only show approved versions.
        :rtype: QuerySet
        """
        versions_qs = Version.objects.all()
        return versions_qs

    def get_object(self, queryset=None):
        """Get the object referenced by this view.

        :param queryset: An option queryset from which the object should be
            retrieved.
        :type queryset: QuerySet

        :returns: A Version instance.
        :rtype: Version
        """
        obj = super(VersionThumbnailView, self).get_object(queryset)
        obj.request_user = self.request.user
        return obj


class VersionDeleteView(LoginRequiredMixin, VersionMixin, DeleteView):
    """A view for deleting version objects."""
    context_object_name = 'version'
    template_name = 'version/delete.html'

    def get_success_url(self):
        """Get the url for when the operation was successful.

        :returns: A url.
        :rtype: str
        """
        return reverse('version-list', kwargs={
            'project_slug': self.object.project.slug
        })

    def get_queryset(self):
        """Get the queryset for this view.

        :returns: A queryset which shows all Versions if user.is_staff,
                or only the creator's Versions if not user.is_staff.
        :rtype: QuerySet
        """
        if not self.request.user.is_authenticated():
            raise Http404
        qs = Version.objects.all()
        if self.request.user.is_staff:
            return qs
        else:
            return qs.filter(creator=self.request.user)


class VersionCreateView(LoginRequiredMixin, VersionMixin, CreateView):
    """A view for creating version objects."""
    context_object_name = 'version'
    template_name = 'version/create.html'

    def get_success_url(self):
        """Get the url for when the operation was successful.

        :returns: A url.
        :rtype: str
        """
        return reverse('pending-version-list', kwargs={
            'project_slug': self.object.project.slug
        })

    def get_form_kwargs(self):
        kwargs = super(VersionCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class VersionUpdateView(LoginRequiredMixin, VersionMixin, UpdateView):
    """View to update an existing version."""
    context_object_name = 'version'
    template_name = 'version/update.html'

    def get_form_kwargs(self):
        kwargs = super(VersionUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_queryset(self):
        """Get the queryset for this view.

        :returns: A queryset which is filtered to only show approved versions.
        :rtype: QuerySet
        """
        versions_qs = Version.approved_objects.all()
        return versions_qs

    def get_success_url(self):
        """Get the url for when the operation was successful.

        :returns: A url.
        :rtype: str
        """
        return reverse('version-list', kwargs={
            'project_slug': self.object.project.slug
        })


class PendingVersionListView(
        VersionMixin, PaginationMixin, ListView, StaffuserRequiredMixin):
    """List all unapproved versions - staff see all """
    context_object_name = 'versions'
    template_name = 'version/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        """Get the context data which is passed to a template.

        :param kwargs: Any arguments to pass to the superclass.
        :type kwargs: dict

        :returns: Context data which will be passed to the template.
        :rtype: dict
        """
        context = super(PendingVersionListView, self).get_context_data(**kwargs)
        context['num_versions'] = self.get_queryset().count()
        context['unapproved'] = True
        return context

    def get_queryset(self):
        """Get the queryset for this view.

        :returns: A queryset which is filtered to only show approved versions.
        :rtype: QuerySet
        """
        versions_qs = Version.unapproved_objects.all()
        if self.request.user.is_staff:
            return versions_qs
        else:
            return versions_qs.filter(creator=self.request.user)


class ApproveVersionView(VersionMixin, StaffuserRequiredMixin, RedirectView):
    """A view to allow staff users to approve a given version."""
    permanent = False
    query_string = True
    pattern_name = 'pending-version-list'

    def get_redirect_url(self, project_slug, slug):
        """Get the url for when the operation completes.

        :param pk: The primary key of the object being approved.
        :type pk: int

        :returns: A url.
        :rtype: str
        """
        version_qs = Version.unapproved_objects.all()
        version = get_object_or_404(version_qs, slug=slug)
        version.approved = True
        version.save()
        return reverse(self.pattern_name, kwargs={
            'project_slug': version.project.slug
        })


class VersionDownload(VersionMixin, StaffuserRequiredMixin, DetailView):
    """A view to allow staff users to download version page in RST format"""
    template_name = 'version/detail-content.html'

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a RST document for a project version page.

        :param context:
        :param response_kwargs:
        """
        version_obj = context.get('version')
        # set the context flag for 'rst_download'
        context['rst_download'] = True
        # render the template
        document = self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )
        # convert the html to rst
        converted_doc = pypandoc.convert(
            document.rendered_content, 'rst', format='html')
        converted_doc = converted_doc.replace('/media/images/', 'images/')

        # prepare the ZIP file
        zip_file = self._prepare_zip_archive(converted_doc, version_obj)

        # Grab the ZIP file from memory, make response with correct MIME-type
        response = HttpResponse(
            zip_file.getvalue(), mimetype="application/x-zip-compressed")
        # ..and correct content-disposition
        response['Content-Disposition'] = (
            'attachment; filename="{}-{}.zip"'.format(
                version_obj.project.name, version_obj.name)
        )

        return response

    # noinspection PyMethodMayBeStatic
    def _prepare_zip_archive(self, document, version_obj):
        """
        Prepare a ZIP file with the document and referenced images.
        :param document:
        :param version_obj: Instance of a version object.
        """
        # create in memory file-like object
        temp_path = StringIO.StringIO()

        # grab all of the images from document
        images = []
        for line in document.split('\n'):
            if 'image::' in line:
                matches = re.findall(r'images.+', line)
                images.extend(matches)

        # create the ZIP file
        with zipfile.ZipFile(temp_path, 'w') as zip_file:
            # write all of the image files (read from disk)
            for image in images:
                zip_file.write(
                    './media/{0}'.format(image),
                    '{0}'.format(image)
                )
            # write the actual RST document
            zip_file.writestr(
                '{}-{}.rst'.format(
                    version_obj.project.name, version_obj.name),
                document)

        return temp_path
