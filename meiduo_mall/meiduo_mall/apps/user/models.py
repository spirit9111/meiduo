from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer

# Create your models here.
from meiduo_mall.utils.exceptions import logger


class User(AbstractUser):
	"""用户模型"""
	mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

	class Meta:
		db_table = 'tb_users'
		verbose_name = '用户'
		verbose_name_plural = verbose_name

	def generate_mobile_token(self):
		"""
		使用手机号生成token
		TimedJSONWebSignatureSerializer()可以生成对象
		该对象可以使用.dump()生成带有时效的token,bytes类型
		"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		# data = token中的载荷
		data = {'mobile': self.mobile}
		token = serializer.dumps(data).decode()
		return token

	def generate_password_token(self):
		"""使用user.id生成token"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		# data = token中的载荷
		data = {'user_id': self.id}
		token = serializer.dumps(data).decode()
		return token

	@staticmethod
	def check_access_token_send_sms(token):
		"""校验access_token获取真实的当前用户mobile"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		try:
			data = serializer.loads(token)
		except Exception as e:
			logger.error('解析mobile异常%s' % e)
			return None
		else:
			return data.get('mobile')

	@staticmethod
	def check_access_token_reset_password(user_id, token):
		"""校验access_token获取真实的当前用户mobile"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		try:
			data = serializer.loads(token)
		except Exception as e:
			logger.error('解析user_id异常%s' % e)
			return False
		else:
			if user_id != str(data.get('user_id')):
				return False
			else:
				return True
