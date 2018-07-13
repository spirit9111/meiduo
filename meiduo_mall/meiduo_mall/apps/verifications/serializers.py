# 定义序列化器
from django_redis import get_redis_connection
from rest_framework import serializers

from meiduo_mall.utils.exceptions import logger


class CheckImageCodeSerializer(serializers.Serializer):
	"""校验图片验证码"""
	# 校验参数的格式是否正确
	image_code_id = serializers.UUIDField()
	text = serializers.CharField(min_length=4, max_length=4)

	def validate(self, attrs):
		"""额外校验"""
		# 取出需要反序列化的值
		image_code_id = attrs['image_code_id']
		text = attrs['text']
		logger.error(self.context)
		# {'request':obj,'format':'bbb','view':'obj'}
		mobile = self.context['view'].kwargs['mobile']

		# 取出真实的图片验证码
		redis_conn = get_redis_connection('verify_codes')
		real_text = redis_conn.get('img_%s' % image_code_id)

		# 图片验证码只能使用一次
		try:
			redis_conn.delete('img_%s' % image_code_id)
		except Exception as e:
			logger.error('redis删除异常:%s' % e)
			pass

		if not real_text:
			raise serializers.ValidationError('图片验证码失效')

		if text.lower() != real_text.decode().lower():
			raise serializers.ValidationError('图片验证码输入错误')

		if redis_conn.get("send_flag_%s" % mobile) == 1:
			raise serializers.ValidationError('一分钟一次')

		return attrs
