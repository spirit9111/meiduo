import json
from urllib import request, parse
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer

from meiduo_mall.utils.exceptions import logger


class OAuthQQ(object):
	"""用于qq登录的工具类,生成相应的url等"""

	def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
		self.client_id = client_id or settings.QQ_CLIENT_ID
		self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
		self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
		self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

	def generate_qq_login_url(self):
		"""生成用于qq登录扫码的url地址"""
		params = {
			'response_type': 'code',
			'client_id': self.client_id,
			'redirect_uri': self.redirect_uri,
			'state': self.state,
			'scope': 'get_user_info',  # 用户勾选的授权范围,get_user_info表示,获取登录用户的昵称、头像、性别
		}
		url = 'https://graph.qq.com/oauth2.0/authorize?'
		# 拼接查询字符串,
		url += parse.urlencode(params)
		return url

	def get_qq_access_token(self, code):
		"""获取access_token"""
		params = {
			'grant_type': 'authorization_code',
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'code': code,
			'redirect_uri': self.redirect_uri,
		}
		url = 'https://graph.qq.com/oauth2.0/token?'
		url += parse.urlencode(params)
		# 向qq方发起http请求,获取包含access_token的查询字符串
		# 形式access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
		try:
			response = request.urlopen(url)
			response_data = response.read().decode()
			# 讲查询字符串转换为python中的字典
			data = parse.parse_qs(response_data)
			access_token = data.get('access_token', None)
		except Exception as e:
			logger.error(e)
			raise Exception('获取access_token异常')
		return access_token

	def get_qq_openid(self, access_token):
		"""获取openid"""
		url = 'https://graph.qq.com/oauth2.0/me?'
		url += access_token
		try:
			response = request.urlopen(url)
			response_data = response.read().decode()
			# 返回一个字符串  callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
			data_dict = json.loads(response_data[10:-4])
			openid = data_dict.get('openid', None)
		except Exception as e:
			logger.error(e)
			raise Exception('获取openid异常')
		return openid

	@staticmethod
	def generate_save_user_token(self, openid):
		"""根据openid生成注册/绑定时用于验证身份的token"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		data = {'openid': openid}
		token = serializer.dumps(data).decode()
		return token
