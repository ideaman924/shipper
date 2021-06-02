from django.urls import path
from .views import *

urlpatterns = [
    path('', DownloadsView.as_view(), name='downloads'),
    path('download/<slug:codename>/', DownloadsDeviceView.as_view(), name='downloads_device'),
    path('download/<slug:codename>/<int:pk>/', DownloadsBuildView.as_view(), name='downloads_build'),
    path('maintainers/', MaintainerDashboardView.as_view(), name='dashboard'),
    path('maintainers/device/<int:pk>/', DeviceDetailView.as_view(), name='device_detail'),
    path('maintainers/device/<int:pk>/upload/', build_upload, name='build_upload'),
    path('maintainers/build/<int:pk>/delete/', BuildDeleteView.as_view(), name='build_delete'),
    path('maintainers/api/system/', system_information, name='system_information'),
    path('maintainers/api/login/', maintainer_api_login, name='maintainer_api_login'),
    path('maintainers/api/chunked_upload/', ChunkedBuildUpload.as_view(), name='chunked_build_upload'),
    path('maintainers/api/chunked_upload/<uuid:pk>/', ChunkedBuildUpload.as_view(), name='chunkedupload-detail'),
]
