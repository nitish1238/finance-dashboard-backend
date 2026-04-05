from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet

router = DefaultRouter()
router.register('', DashboardViewSet, basename='dashboard')

urlpatterns = router.urls