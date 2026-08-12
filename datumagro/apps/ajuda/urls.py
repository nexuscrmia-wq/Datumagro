from django.urls import path
from .views import GuiaModuloDetailView

app_name = "ajuda"

urlpatterns = [
    path("<slug:modulo_slug>/", GuiaModuloDetailView.as_view(), name="guia-detalhe"),
]
