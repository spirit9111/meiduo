from django.conf.urls import url

from goods.views import HotSKUListView,SkUListView

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', HotSKUListView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus/$', SkUListView.as_view()),
]