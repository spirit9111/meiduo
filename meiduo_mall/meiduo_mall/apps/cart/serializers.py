from rest_framework import serializers

from goods.models import SKU
from meiduo_mall.utils.exceptions import logger


class AddSkuSerializer(serializers.Serializer):
	"""校验购物车参数"""
	sku_id = serializers.IntegerField(min_value=1)
	count = serializers.IntegerField(min_value=1)
	selected = serializers.BooleanField(default=True)

	def validate(self, data):
		try:
			sku = SKU.objects.get(id=data['sku_id'])
		except Exception as e:
			logger.error(e)
			raise serializers.ValidationError('商品不存在')

		if data['count'] > sku.stock:
			raise serializers.ValidationError('商品库存不足')

		return data
