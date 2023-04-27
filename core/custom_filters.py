from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class HashedFilter(admin.SimpleListFilter):
    title = _("hashed")
    parameter_name = "hashed"

    def lookups(self, request, model_admin):
        return [
            (None, _("All")),
            ("true", _("Yes")),
            ("false", _("No")),
        ]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        ids = []

        if self.value() == "true":
            ids = [build.id for build in queryset.all() if build.is_hashed()]
        elif self.value() == "false":
            ids = [build.id for build in queryset.all() if not build.is_hashed()]

        return queryset.filter(id__in=ids)


class MirroredFilter(admin.SimpleListFilter):
    title = _("mirrored")
    parameter_name = "mirrored"

    def lookups(self, request, model_admin):
        return [
            (None, _("All")),
            ("true", _("Yes")),
            ("false", _("No")),
        ]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        ids = []

        if self.value() == "true":
            ids = [build.id for build in queryset.all() if build.is_mirrored()]
        elif self.value() == "false":
            ids = [build.id for build in queryset.all() if not build.is_mirrored()]

        return queryset.filter(id__in=ids)
