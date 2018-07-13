from django.conf.urls import url

from apps.verifications.views import ImageCodeView, SmsCodeView

urlpatterns = [
	url(r'image_code/(?P<image_code_id>.+)/', ImageCodeView.as_view()),
	url(r'sms_code/(?P<mobile>(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8})/',
		SmsCodeView.as_view()),
]
