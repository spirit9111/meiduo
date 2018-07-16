from django.conf.urls import url

from oauth.views import QQAuthUrlView

urlpatterns = [
	url(r'^qq/authorization/', QQAuthUrlView.as_view()),
]
