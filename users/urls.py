from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet,RegisterView


router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')      # /api/auth/
router.register(r'', UserViewSet, basename='user')      # /api/users/


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
    
]