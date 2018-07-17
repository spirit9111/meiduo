import random
import re
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin
from rest_framework.views import APIView

from meiduo_mall.utils.exceptions import logger
from user.serializers import RegisterSerializer, CheckSmsCodeSerializer, CheckUserIdSerializer, UserInfoSerializer, \
	EmailSerializer
from user.models import User
from verifications.constants import SMS_CODE_REDIS_EXPIRES, SEND_SMS_CODE_INTERVAL
from verifications.serializers import CheckImageCodeSerializer


# GET usernames/(?P<username>/count/_
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
		if send_flag == 1:
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
		# except Exception as e:
		# 	logger.error(e)
		# 异步发短信
		return Response({'message': 'ok'})


# GET accounts/(?P<account>\w{5,20})/password/token/

class FindPasswordStepThreeView(GenericAPIView):
	"""找回密码第三步,校验短信验证码+设置token给下一步使用"""
	serializer_class = CheckSmsCodeSerializer

	def get(self, request, account):
		serializer = self.get_serializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)

		user = serializer.user

		access_token = user.generate_password_token()
		return Response({'user_id': user.id, 'access_token': access_token})


# POST users / (?P < pk > \d+) / password /
class FindPasswordStepFourView(UpdateModelMixin, GenericAPIView):
	"""找回密码第四步,校验身份+重制密码"""
	serializer_class = CheckUserIdSerializer
	queryset = User.objects.all()

	def post(self, request, pk):
		return self.update(request, pk)


# class FindPasswordStepFourView(UpdateAPIView):
# 	serializer_class = CheckUserIdSerializer
# 	queryset = User.objects.all()

# GET user/
# jwt保存在请求头中
class UserInfoView(RetrieveAPIView):
	"""用户信息"""
	serializer_class = UserInfoSerializer
	# 指定视图的访问权限,不期望通过user/pk方式进行访问
	permission_classes = [IsAuthenticated]

	def get_object(self):
		"""
		在默认的RetrieveAPIView的get_object需要url中传入pk指明具体查询的用户
		request.user 保存了通过验证的user对象
		:return: 通过权限验证的用户对象
		"""
		return self.request.user


# 更新emil
# PUT email/
class SendAndSaveEmail(UpdateAPIView):
	"""发送+保存email"""
	serializer_class = EmailSerializer
	permission_classes = [IsAuthenticated]

	def get_object(self):
		return self.request.user


class VerifyEmailView(APIView):
	"""
	邮箱验证
	"""

	def get(self, request):
		# 获取token
		token = request.query_params.get('token')
		if not token:
			return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

		# 验证token
		user = User.check_verify_email_token(token)
		if user is None:
			return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
		else:
			user.email_active = True
			user.save()
			return Response({'message': 'OK'})
