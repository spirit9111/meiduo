from alipay import AliPay
from django.shortcuts import render
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.utils.exceptions import logger
from orders.models import OrderInfo
import os

#  GET /orders/(?P<order_id>\d+)/payment/
from payment.models import Payment


class PaymenView(APIView):
	"""发起支付请求,[去支付]接口"""
	permission_classes = [IsAuthenticated, ]

	def get(self, request, order_id):
		# 校验order_id
		try:
			order_obj = OrderInfo.objects.get(order_id=order_id)
		except Exception as e:
			logger.error(e)
			return Response({'message': 'order_id错误'})

		app_private_key_string = open(
			os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem")).read()
		alipay_public_key_string = open(
			os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem")).read()
		# 调用python-alipay-sdk中的类创建alipay对象
		alipay = AliPay(
			appid="2016091700529506",  # 沙箱的appid
			app_notify_url=None,  # 默认回调url
			app_private_key_string=app_private_key_string,
			alipay_public_key_string=alipay_public_key_string,
			sign_type="RSA2",  # RSA 或者 RSA2
			debug=True  # 默认False
		)

		# 调用python-alipay-sdk中的api_alipay_trade_page_pay生成用于支付的链接地址查询字符串
		order_string = alipay.api_alipay_trade_page_pay(
			out_trade_no=order_id,
			total_amount=str(order_obj.total_amount),
			subject='MeiDuoTest_%s' % order_id,
			return_url="http://www.meiduo.site:8080/pay_success.html",
			# notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
		)
		alipay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
		# print(alipay_url)
		return Response({'alipay_url': alipay_url})


# PUT / payment / status /?支付宝参数
class SaveChangeStatusView(APIView):
	"""保存支付流水号/修改订单状态"""

	def put(self, request):
		# 将query_dict转换为python的字典
		data_dict = request.query_params.dict()
		signature = data_dict.pop('sign')

		app_private_key_string = open(
			os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem")).read()
		alipay_public_key_string = open(
			os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem")).read()

		# 调用python-alipay-sdk中的类创建alipay对象
		alipay = AliPay(
			appid="2016091700529506",  # 沙箱的appid
			app_notify_url=None,  # 默认回调url
			app_private_key_string=app_private_key_string,
			alipay_public_key_string=alipay_public_key_string,
			sign_type="RSA2",  # RSA 或者 RSA2
			debug=True  # 默认False
		)
		success = alipay.verify(data_dict, signature)
		if success:
			# 订单编号
			order_id = data_dict.get('out_trade_no')
			# 支付宝支付流水号
			trade_id = data_dict.get('trade_no')
			Payment.objects.create(
				order_id=order_id,
				trade_id=trade_id
			)
			OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
				status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
			return Response({'trade_id': trade_id})
		else:
			return Response({'message': '非法请求'}, status=403)
