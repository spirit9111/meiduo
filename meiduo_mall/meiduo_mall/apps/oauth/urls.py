from django.conf.urls import url

from oauth.views import QQAuthUrlView, QQAuthUserView

urlpatterns = [
	url(r'^qq/authorization/', QQAuthUrlView.as_view()),
	url(r'^qq/user/', QQAuthUserView.as_view()),
]
