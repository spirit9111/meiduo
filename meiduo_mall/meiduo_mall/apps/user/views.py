import re

from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from serializers import RegisterSerializer
from user.models import User

# GET usernames/(?P<username>/count/
from verifications.serializers import CheckImageCodeSerializer


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


# POST register/
# class RegisterView(CreateModelMixin, GenericAPIView):
class RegisterView(CreateAPIView):
	"""注册接口"""
	serializer_class = RegisterSerializer


# def post(self, request):
# 	return self.create(request)


# 找回密码
# 第一步,发送用户名和图片验证码
# GET GET accounts/(?P<account>\w{5,20})/sms/token/
# 接受username和图片验证码,返回处理过的手机号和用于验证的token

class FindPasswordStepOneView(GenericAPIView):
	"""找回密码第一步"""
	serializer_class = CheckImageCodeSerializer

	def get(self, request, account):
		# 对用户名进行处理
		# 1.判断用户是否存在
		user = User.objects.get(username=account)
		if not user:
			return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

		# 对图片验证码进行处理
		# 复用图片验证码的序列化器
		serializer = self.get_serializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)

		# 返回经过处理的隐藏的手机号
		mobile = re.sub(r'(\d{3})\d{4}(\d{3})', r'\1****\2', user.mobile)

		# 返回使用手机号生成token,
		# access_token = user.生成token的方法
		access_token = user.generate_mobile_token()

		data = {
			'mobile': mobile,
			'access_token': access_token,
		}
		return Response(data)
