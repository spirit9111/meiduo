from rest_framework import serializers

from goods.models import SKU


class OrderShowSerializer(serializers.ModelSerializer):
	count = serializers.IntegerField(label='数量')

	class Meta:
		model = SKU
		fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
	"""
	订单结算数据序列化器
	"""
	freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
	skus = OrderShowSerializer(many=True)

# 最终返回的数据结构如下:
# {
#     "freight":"10.00",
#     "skus":[
#         {
#             "id":10,
#             "name":"华为 HUAWEI P10 Plus 6GB+128GB 钻雕金 移动联通电信4G手机 双卡双待",
#              "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRchWAMc8rAARfIK95am88158618",
#             "price":"3788.00",
#             "count":1
#         },
#         {
#             "id":16,
#             "name":"华为 HUAWEI P10 Plus 6GB+128GB 曜石黑 移动联通电信4G手机 双卡双待",
#             "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRdPeAXNDMAAYJrpessGQ9777651",
#             "price":"3788.00",
#             "count":1
#         }
#     ]
# }
