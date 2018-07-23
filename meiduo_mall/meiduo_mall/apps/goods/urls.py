from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from goods.views import HotSKUListView, SkUListView, SKUSearchViewSet

urlpatterns = [
	url(r'^categories/(?P<category_id>\d+)/hotskus/$', HotSKUListView.as_view()),
	url(r'^categories/(?P<category_id>\d+)/skus/$', SkUListView.as_view()),
]

router = DefaultRouter()
router.register('skus/search', SKUSearchViewSet, base_name='skus-search')

urlpatterns += router.urls
