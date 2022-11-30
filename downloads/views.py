from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView
from django.shortcuts import render
from core.models import Build, Device, Statistics


class DownloadsMainView(ListView):
    template_name = "downloads_main.html"
    model = Device

    ordering = ["-status", "manufacturer", "name"]


class DownloadsDeviceView(DetailView):
    template_name = "downloads_device.html"
    model = Device

    def get_object(self, queryset=None):
        return get_object_or_404(Device, codename=self.kwargs.get("codename"))


class DownloadsBuildView(DetailView):
    template_name = "downloads_build.html"
    model = Build


class LanguageSwitchView(TemplateView):
    template_name = "language_switch.html"

    def get(self, request, *args, **kwargs):
        redirect_url = request.GET.get("next", None)
        if not redirect_url:
            redirect_url = request.META.get("HTTP_REFERER", None)
        if not redirect_url:
            redirect_url = "/"
        return render(request, self.template_name, {"redirect_to": redirect_url})


class StatisticsMainView(TemplateView):
    template_name = "statistics_main.html"
    
    def get(self, request, *args, **kwargs):
        devices = Device.objects.all()
        
        popular_devices_ranking = []
        
        for device in devices:
            popular_devices_ranking += (device, device.get_statistics_count())
        
        popular_devices_ranking.sort(reverse=True, key=lambda x: x[1])
        
        data = {"popular_devices_ranking": popular_devices_ranking}
        
        return render(request, self.template_name, data)

