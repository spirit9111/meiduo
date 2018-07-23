from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from drf_haystack.viewsets import HaystackViewSet
from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer


# GET categories/(?P<category_id>\d+)/hotskus/
class HotSKUListView(ListCacheResponseMixin, ListAPIView):
	"""热销商品接口"""
	serializer_class = SKUSerializer
	pagination_class = None

	def get_queryset(self):
		category_id = self.kwargs.get('category_id')
		return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:3]


class SkUListView(ListAPIView):
	"""商品列表接口"""
	serializer_class = SKUSerializer
	filter_backends = (OrderingFilter,)
	ordering_fields = ('create_time', 'price', 'sales')

	def get_queryset(self):
		category_id = self.kwargs.get('category_id')
		return SKU.objects.filter(category_id=category_id, is_launched=True)




class SKUSearchViewSet(HaystackViewSet):
	"""
	SKU搜索
	"""
	index_models = [SKU]

	serializer_class = SKUIndexSerializer
