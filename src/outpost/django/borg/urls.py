from django.conf.urls import url

from . import views

app_name = "borg"

urlpatterns = [
    url(r"^$", views.RepositoryListView.as_view(), name="repository"),
    url(
        r"^update/(?P<secret>[\w\d]+)/$",
        views.StatusUpdateView.as_view(),
        name="repository-status-update",
    ),
    url(
        r"^(?P<pk>\d+)/$",
        views.RepositoryDetailView.as_view(),
        name="repository-detail",
    ),
    url(r"^add/$", views.RepositoryCreateView.as_view(), name="repository-create"),
    url(
        r"^edit/(?P<pk>\d+)$",
        views.RepositoryUpdateView.as_view(),
        name="repository-edit",
    ),
    url(
        r"^delete/(?P<pk>\d+)$",
        views.RepositoryDeleteView.as_view(),
        name="repository-delete",
    ),
]
