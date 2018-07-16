from django_redis import get_redis_connection
from rest_framework import serializers

from meiduo_mall.utils.exceptions import logger
from oauth.models import OAuthQQUser
from oauth.utils import OAuthQQ
from user.models import User


class OAuthQQUserSerializer(serializers.Serializer):
	"""创建或绑定QQ对应的本站用户"""
	access_token = serializers.CharField(label='操作凭证')
	mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
	password = serializers.CharField(label='密码', max_length=20, min_length=8)
	sms_code = serializers.CharField(label='短信验证码')

	def validate(self, data):
		# 检验access_token
		access_token = data['access_token']
		openid = OAuthQQ.check_token_by_openid(access_token)
		if not openid:
			raise serializers.ValidationError('access_token失效')
		# 检验短信验证码
		mobile = data['mobile']
		sms_code = data['sms_code']
		redis_conn = get_redis_connection('verify_codes')
		real_sms_code = redis_conn.get('sms_%s' % mobile).decode()
		if not real_sms_code:
			raise serializers.ValidationError('短信验证码失效或过期')

		if real_sms_code != sms_code:
			raise serializers.ValidationError('短信验证码错误')

		# 如果用户存在，检查用户密码
		try:
			user = User.objects.get(mobile=mobile)
		except Exception as e:
			logger.error('本站用户不存在,等待注册---%s' % e)
			pass
		else:
			# 如果存在就校验密码
			password = data['password']
			if not user.check_password(password):
				raise serializers.ValidationError('密码错误')
			data['user'] = user

		data['openid'] = openid
		return data

	def create(self, validated_data):
		user = validated_data.get('user', None)
		if not user:
			# 用户不存在,先注册本站新用户
			user = User.objects.create_user(
				username=validated_data['mobile'],
				password=validated_data['password'],
				mobile=validated_data['mobile'],
			)
		# 新老用户都绑定QQ的openid
		OAuthQQUser.objects.create(
			openid=validated_data['openid'],
			user=user
		)
		return user
