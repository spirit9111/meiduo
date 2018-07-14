import random
import re

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from meiduo_mall.utils.exceptions import logger
from serializers import RegisterSerializer
from user.models import User

# GET usernames/(?P<username>/count/
from verifications.constants import SMS_CODE_REDIS_EXPIRES, SEND_SMS_CODE_INTERVAL
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
	"""找回密码第一步,用户名+图片验证接口"""
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


#  GET /sms_codes/?access_token=xxx
# 使用token中的手机号发送短信,
class FindPasswordStepTwoView(GenericAPIView):
	"""找回密码第二步,发送短信验证接口"""

	def get(self, request):
		access_token = request.query_params.get('access_token')
		if not access_token:
			return Response({'message': 'token不存在'}, 400)
		# 从access_token中取回取到手机号
		mobile = User.check_access_token_send_sms(access_token)
		if not mobile:
			return Response({'message': 'token失效或不存在'}, 400)
		# 60s发送一次
		redis_conn = get_redis_connection('verify_codes')
		send_flag = redis_conn.get("send_flag_%s" % mobile)
		if send_flag==1:
			return Response({"message": "请求次数过于频繁"}, 429)

		sms_code = '%06d' % random.randint(0, 999999)
		logger.error('--->短信验证码:[%s]<---' % sms_code)

		pl = redis_conn.pipeline()
		pl.setex('sms_%s' % mobile, SMS_CODE_REDIS_EXPIRES, sms_code)
		pl.setex("send_flag_%s" % mobile, SEND_SMS_CODE_INTERVAL, 1)
		pl.execute()

		# 发送短信
		# try:
		# 	send_mes = SendMes()
		# 	send_mes.send_2_mes(mobile, sms_code)
		# except Exceptione:
		# 	logger.error(e)
		# 异步发短信
		return Response({'message': 'ok'})
