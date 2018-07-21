from django.conf.urls import url

from goods.views import HotSKUListView

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', HotSKUListView.as_view()),
]