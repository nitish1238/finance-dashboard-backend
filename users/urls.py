from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet


router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')      # /api/users/
router.register(r'auth', AuthViewSet, basename='auth')      # /api/auth/

urlpatterns = [
    path('', include(router.urls)),
]