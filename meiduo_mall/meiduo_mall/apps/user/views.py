from django.shortcuts import render
from rest_framework.generics import GenericAPIView


# Create your views here.
class UsernameView(GenericAPIView):
	"""用户名验证接口"""
	pass


class MobileView(GenericAPIView):
	"""手机号验证接口"""
	pass


class RegisterView(GenericAPIView):
	"""注册接口"""
	pass
