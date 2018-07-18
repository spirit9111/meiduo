from rest_framework.routers import DefaultRouter

from user.views import CreateOrUpdateAddressInfo
from .views import AreaView

router = DefaultRouter()
router.register(r'areas', AreaView, base_name='areas')
router.register(r'addresses', CreateOrUpdateAddressInfo, base_name='addresses')

urlpatterns = []

urlpatterns += router.urls
