# 定义生成静态页面的函数
import os
from collections import OrderedDict

from django.conf import settings
from django.template import loader

from content.models import ContentCategory
from goods.models import GoodsChannel


def generate_static_index_html():
	"""生成首页的静态html"""
	# 商品频道分类的展示
	# 构建有序的空字典
	categories = OrderedDict()
	channels = GoodsChannel.objects.order_by('group_id', 'sequence')
	# 将商品类别按照分组
	for channel in channels:
		group_id = channel.group_id
		if group_id not in categories:
			categories[group_id] = {
				'channels': [],
				'sub_cats': [],
			}
		# 一级分类
		cat1 = channel.category
		categories[group_id]['channels'].append({
			'id': cat1.id,
			'name': cat1.name,
			'url': channel.url
		})
		# 二级分类
		for cat2 in cat1.goodscategory_set.all():
			# 三级分类
			cat2.sub_cats = []
			for cat3 in cat2.goodscategory_set.all():
				cat2.sub_cats.append(cat3)
			categories[group_id]['sub_cats'].append(cat2)
	# 广告页面
	contents = dict()
	content_categories = ContentCategory.objects.all()
	for cat in content_categories:
		contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

	context = {
		'categories': categories,
		'contents': contents,
	}
	template = loader.get_template('index.html')
	html_text = template.render(context)
	file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
	with open(file_path, 'w') as f:
		f.write(html_text)
