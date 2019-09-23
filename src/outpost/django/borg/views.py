import iso8601
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy as reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    View,
    DetailView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin
from django.contrib.staticfiles import finders
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from guardian.shortcuts import get_objects_for_user, assign_perm, get_users_with_perms
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from jsonschema import validate, ValidationError
from guardian.mixins import PermissionRequiredMixin, PermissionListMixin

from . import models


class IndexView(TemplateView):
    template_name = "borg/index.html"


class RepositoryListView(LoginRequiredMixin, PermissionListMixin, ListView):
    model = models.Repository
    permission_required = ("borg.change_repository", "borg.delete_repository")
    get_objects_for_user_extra_kwargs = {"any_perm": True}


class RepositoryDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Repository
    permission_required = ("borg.change_repository", "borg.delete_repository")


class RepositoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Repository
    fields = ("server", "name", "public_key")
    permission_required = "borg.add_repository"
    permission_object = None
    success_url = reverse("borg:repository")

    def form_valid(self, form):
        res = super().form_valid(form)
        assign_perm("borg.change_repository", self.request.user, form.instance)
        assign_perm("borg.delete_repository", self.request.user, form.instance)
        return res


class RepositoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Repository
    fields = ("server", "name", "public_key")
    permission_required = "borg.add_repository"
    success_url = reverse("borg:repository")


class RepositoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Repository
    permission_required = "borg.delete_repository"
    success_url = reverse("borg:repository")


class StatusUpdateView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create = finders.find("borg/create.json")
        with open(create, "r") as f:
            self.schema = json.load(f)

    def post(self, request, *args, **kwargs):
        try:
            validate(self.request_json, schema=self.schema)
        except ValidationError as e:
            return HttpResponseBadRequest(str(e))
        repository = get_object_or_404(models.Repository, secret=kwargs["secret"])
        archive = models.Archive(repository=repository)
        archive.id = self.request_json["archive"]["id"]
        archive.name = self.request_json["archive"]["name"]
        archive.start = iso8601.parse_date(self.request_json["archive"]["start"])
        archive.end = iso8601.parse_date(self.request_json["archive"]["end"])
        archive.files = self.request_json["archive"]["stats"]["nfiles"]
        archive.raw = self.request_json["archive"]["stats"]["original_size"]
        archive.compressed = self.request_json["archive"]["stats"]["compressed_size"]
        archive.deduplicated = self.request_json["archive"]["stats"][
            "deduplicated_size"
        ]
        archive.save()
        repository.updated = iso8601.parse_date(self.request_json["repository"]["last_modified"])
        repository.raw = self.request_json["cache"]["stats"]["total_size"]
        repository.compressed = self.request_json["cache"]["stats"]["total_csize"]
        repository.deduplicated = self.request_json["cache"]["stats"]["unique_csize"]
        repository.save()
        perms = get_users_with_perms(repository)
        for user in perms:
            assign_perm("borg.change_archive", user, archive)
            assign_perm("borg.delete_archive", user, archive)

        return self.render_json_response({"archive": archive.pk})
