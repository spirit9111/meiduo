from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from meiduo_mall.utils.exceptions import logger
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import OAuthQQ


# Create your views here.

# 因为是前后端分离不能直接重定向,
# 所以需要前端在请求接口时返回QQ登录的的url地址,
# 在前端的回调函数中实现跳转QQ扫码登录的界面


# GET /oauth/qq/authorization/?state=xxx
class QQAuthUrlView(APIView):
	"""获取QQ扫码登录的网址接口"""

	def get(self, request):
		"""
		:return 扫码的url地址
		"""
		state = request.query_params.get('state')
		oauthqq = OAuthQQ(state=state)
		qq_login_url = oauthqq.generate_qq_login_url()
		return Response({'qq_login_url': qq_login_url})


# qq登录后会返回设定注册qq登录功能时指定的重定向界面
# 该界面的js中将获取qq的code,进入接口
# GET /oauth/qq/user/?code = xxx
class QQAuthUserView(GenericAPIView):
	"""QQ登录后,拿着code获取access_token值"""
	# todo
	serializer_class = OAuthQQUserSerializer

	def get(self, request):
		"""QQ登录"""
		code = request.query_params.get('code')
		if not code:
			return Response({'message': 'code不存在'}, 400)

		# 目标是通过 code获取access_token
		oauthqq = OAuthQQ()
		access_token = oauthqq.get_qq_access_token(code)

		# 通过access_token获取openid
		openid = oauthqq.get_qq_openid(access_token)

		# 获取openid后需要判断
		# oauthqquser = OAuthQQUser.get

		try:
			oauthqquser = OAuthQQUser.objects.get(openid=openid)
		except Exception as e:
			logger.error('此人未绑定或未注册:%s' % e)
			# 1.第一次用qq登录
			# 使用openid生成记录qq身份的token,以便注册或绑定时验证身份
			access_token = OAuthQQ.generate_save_user_token(openid)
			return Response({'access_token': access_token})
		# 1.1 已经注册本站账号--->跳转绑定界面
		# 1.2 未注册本站账号--->注册并绑定

		# 2.以前已经qq登录过(一定有本站账号)
		else:
			user = oauthqquser.user
			# 生成jwt_token,用于记录登录状态
			jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
			jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
			payload = jwt_payload_handler(user)
			jwt_token = jwt_encode_handler(payload)

			data = {
				'user_id': user.id,
				'username': user.username,
				'token': jwt_token
			}
			return Response(data=data)

	def post(self, request):
		"""QQ绑定网站账号/注册新账号"""

		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
		jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
		payload = jwt_payload_handler(user)
		jwt_token = jwt_encode_handler(payload)

		data = {
			'user_id': user.id,
			'username': user.mobile,
			'token': jwt_token
		}
		return Response(data=data)
