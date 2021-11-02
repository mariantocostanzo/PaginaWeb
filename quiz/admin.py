import json
from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.core.serializers.json import DjangoJSONEncoder

from .models import Categoria, EstadisticasUsuarios, LoginDetails, PartidasDetails, Respuesta, User, Preguntas, ProgresoHistorico, ProgresoSesion

# Register your models here.

admin.site.register(User)
admin.site.register(Preguntas)
admin.site.register(ProgresoSesion)
admin.site.register(ProgresoHistorico)
admin.site.register(Respuesta)
admin.site.register(Categoria)

#estadisticas usuarios
admin.site.register(EstadisticasUsuarios)

#intenando mostrar graficos
@admin.register(LoginDetails)
class LoginDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "login_time") # display these table columns in the list view
    ordering = ("-login_time",)                  # sort by most recent subscriber

    def changelist_view(self, request, extra_context=None):
        # Aggregate new subscribers per day
        chart_data = (
            LoginDetails.objects.annotate(date=TruncDay("login_time"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(PartidasDetails)
class PartidasDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "time") # display these table columns in the list view
    ordering = ("-time",)                  # sort by most recent subscriber

    def changelist_view(self, request, extra_context=None):
        # Aggregate new subscribers per day
        chart_data = (
            PartidasDetails.objects.annotate(date=TruncDay("time"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

