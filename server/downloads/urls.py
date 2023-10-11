from django.urls import path

from .views import (
    DownloadsBuildView,
    DownloadsDeviceView,
    DownloadsMainView,
    LanguageSwitchView,
    download_view,
)

urlpatterns = [
    path("", DownloadsMainView.as_view(), name="downloads"),
    path(
        "download/<slug:codename>/",
        DownloadsDeviceView.as_view(),
        name="downloads_device",
    ),
    path(
        "download/<slug:codename>/<int:pk>/",
        DownloadsBuildView.as_view(),
        name="downloads_build",
    ),
    path("language_switch/", LanguageSwitchView.as_view(), name="language_switch"),
    path(
        "media/<slug:codename>/<slug:file_name>/", download_view, name="download_view"
    ),
]
