from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

router = DefaultRouter()
router.register(r'', TransactionViewSet, basename='transaction')  # ← FIX THIS LINE

urlpatterns = [
    path('', include(router.urls)),
]