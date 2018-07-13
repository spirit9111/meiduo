import random

from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from apps.verifications.constants import IMAGE_CODE_REDIS_EXPIRES, SMS_CODE_REDIS_EXPIRES, SEND_SMS_CODE_INTERVAL
from apps.verifications.serializers import CheckImageCodeSerializer
from libs.captcha.captcha import captcha
from libs.dysms_python.send_2_mes import SendMes
from utils.exceptions import logger
from rest_framework.generics import GenericAPIView


# 返回图片验证码
# GET image_code/(?P<image_code_id>)
class ImageCodeView(APIView):
	"""图片验证码接口"""

	def get(self, request, image_code_id):
		text, image = captcha.generate_captcha()
		logger.error('--->图片验证码:[%s]<---' % text)
		logger.error('--->UUID:[%s]<---' % image_code_id)
		redis_conn = get_redis_connection('verify_codes')
		redis_conn.setex('img_%s' % image_code_id, IMAGE_CODE_REDIS_EXPIRES, text)
		return HttpResponse(image, content_type='images/jpg')


# GET /sms_code/(?P<mobile>)/?image_code_id=xxx&text=yyy/
class SmsCodeView(GenericAPIView):
	"""短信验证码接口"""

	serializer_class = CheckImageCodeSerializer

	def get(self, request, mobile):
		# 需要校验的参数,{'image_code_id':xxx,'text':yyy}
		data = request.query_params
		serializer = self.get_serializer(data=data)
		serializer.is_valid(raise_exception=True)
		# 校验成功后,生成并保存真实的短信验证码到redis
		sms_code = '%06d' % random.randint(0, 999999)
		logger.error('--->短信验证码:[%s]<---' % sms_code)

		redis_conn = get_redis_connection('verify_codes')
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
		return Response({'message': 'OK'})
