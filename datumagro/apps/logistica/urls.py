from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmbarqueViewSet, ItemEmbarqueViewSet

router = DefaultRouter()
router.register(r'embarques', EmbarqueViewSet, basename='embarque')
router.register(r'itens', ItemEmbarqueViewSet, basename='itemembarque')

urlpatterns = [
    path('', include(router.urls)),
]
