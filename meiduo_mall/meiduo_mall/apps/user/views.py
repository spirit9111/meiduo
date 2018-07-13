from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from user.models import User


# GET usernames/(?P<username>/count/
class UsernameView(GenericAPIView):
	"""用户名验证接口"""

	def get(self, request, username):
		count = User.objects.filter(username=username).count()
		data = {
			'username': username,
			'count': count
		}
		return Response(data)


# GET mobile/(?P<mobile>/count/
class MobileView(GenericAPIView):
	"""手机号验证接口"""
	def get(self, request, mobile):
		count = User.objects.filter(mobile=mobile).count()
		data = {
			'mobile': mobile,
			'count': count
		}
		return Response(data)


class RegisterView(GenericAPIView):
	"""注册接口"""
	pass
