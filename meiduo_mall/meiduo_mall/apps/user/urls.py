from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from user.views import UsernameView, MobileView, RegisterView, FindPasswordStepOneView, FindPasswordStepTwoView, \
	FindPasswordStepThreeView, FindPasswordStepFourView, UserInfoView, SendAndSaveEmail

urlpatterns = [
	# 注册
	url(r'register/', RegisterView.as_view()),
	url(r'username/(?P<username>\w{5,20})/count/', UsernameView.as_view()),
	url(r'mobiles/(?P<mobile>(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8})/count/',
		MobileView.as_view()),
	# 登录
	url(r'authorizations/', obtain_jwt_token, name='authorizations'),
	# 找回密码
	url(r'accounts/(?P<account>\w{5,20})/sms/token/', FindPasswordStepOneView.as_view()),
	url(r'sms_codes/', FindPasswordStepTwoView.as_view()),
	url(r'accounts/(?P<account>\w{5,20})/password/token/', FindPasswordStepThreeView.as_view()),
	url(r'users/(?P<pk>\d+)/password/', FindPasswordStepFourView.as_view()),
	# 用户中心
	url(r'^user/', UserInfoView.as_view()),
	url(r'^emails/$', SendAndSaveEmail.as_view()),
]
