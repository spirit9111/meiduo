from rest_framework.routers import DefaultRouter
from .views import AreaView

router = DefaultRouter()
router.register(r'areas', AreaView, base_name='areas')

urlpatterns = []

urlpatterns += router.urls
