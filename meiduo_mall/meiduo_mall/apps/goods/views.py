from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin

from goods.models import SKU
from goods.serializers import SKUSerializer


# GET categories/(?P<category_id>\d+)/hotskus/
class HotSKUListView(ListCacheResponseMixin, ListAPIView):
	"""热销商品接口"""
	serializer_class = SKUSerializer

	def get_queryset(self):
		category_id = self.kwargs.get('category_id')
		return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:3]
