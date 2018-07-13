from django.conf.urls import url

from apps.verifications.views import ImageCodeView

urlpatterns = [
	url(r'image_code/(?P<image_code_id>.+)/', ImageCodeView.as_view())
]
