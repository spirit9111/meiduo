# 定义函数用于快速生成商品类别展示
from collections import OrderedDict
from goods.models import GoodsChannel


def get_categories():
	"""分类数据的展示"""
	categories = OrderedDict()
	channels = GoodsChannel.objects.order_by('group_id', 'sequence')
	for channel in channels:
		group_id = channel.group_id
		if group_id not in categories:
			# 按照组别进行分类
			categories[group_id] = {'channels': [], 'sub_cats': []}
		cat1 = channel.category
		categories[group_id]['channels'].append({'id': cat1.id,
												 'name': cat1.name,
												 'url': channel.url})
		for cat2 in cat1.goodscategory_set.all():
			cat2.sub_cats = []
			for cat3 in cat2.goodscategory_set.all():
				cat2.sub_cats.append(cat3)
			categories[group_id]['sub_cats'].append(cat2)
	return categories
