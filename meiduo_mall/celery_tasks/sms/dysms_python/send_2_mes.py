import uuid
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider


# 注意：不要更改
from celery_tasks.sms.dysms_python.build.lib.aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest


class SendMes(object):
	REGION = "cn-hangzhou"
	PRODUCT_NAME = "Dysmsapi"
	DOMAIN = "dysmsapi.aliyuncs.com"

	# 申请的ACCESS_KEY_ID和ACCESS_KEY_SECRET
	ACCESS_KEY_ID = "LTAIYEeWFSUAFcYy"
	ACCESS_KEY_SECRET = "FeuGEGSeHXHJ7A4uFIO0mMLoGjKiiY"

	acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
	region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

	def send_2_mes(self, phone_numbers, code):
		# 申请的短信签名 和 短信模板
		sign_name = 'SpiritBlog'
		template_code = 'SMS_137657397'
		business_id = uuid.uuid1()
		template_param = '{"code":"%s"}' % code
		smsRequest = SendSmsRequest.SendSmsRequest()
		# 申请的短信模板编码,必填
		smsRequest.set_TemplateCode(template_code)

		# 短信模板变量参数
		if template_param is not None:
			smsRequest.set_TemplateParam(template_param)

		# 设置业务请求流水号，必填。
		smsRequest.set_OutId(business_id)

		# 短信签名
		smsRequest.set_SignName(sign_name)

		# 短信发送的号码列表，必填。
		smsRequest.set_PhoneNumbers(phone_numbers)

		# 调用短信发送接口，返回json
		smsResponse = self.acs_client.do_action_with_exception(smsRequest)
		return smsResponse

# sm = SendMes()
# sm.send_2_mes(15071176826, 333333)
