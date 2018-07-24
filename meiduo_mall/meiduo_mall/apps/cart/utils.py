import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_to_redis(request, user, response):
	"""
	合并cookie_cart到redis_cart
	:return:
	"""

	cookie_cart_str = request.COOKIES.get('cart')

	# 如果原本cookie就没有cart直接返回
	if cookie_cart_str is None:
		return response

	# 从cookie中获取cart信息
	# {
	# 	sku_id:{
	# 		count:count,
	# 		selected:True
	# 	},
	# ...
	# }
	cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str.encode()))

	redis_conn = get_redis_connection('cart')
	# 从redis中获取数据
	# {
	# 	b'sku_id':b'count',# byte类型
	# 	b'sku_id':b'count',# byte类型
	# }
	redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
	# [b'sku_id',b'sku_id'...]
	# redis_cart_set = redis_conn.smembers('cart_selected_%s' % user.id)

	# 转换成能够合并的python字典,值为int类型
	redis_cart_dict_to_int = {}
	for sku_id, count in redis_cart_dict.items():
		redis_cart_dict_to_int[int(sku_id)] = int(count)
	# 构建新数据
	redis_cart_set_list = []
	for sku_id, value_dict in cookie_cart_dict.items():
		redis_cart_dict_to_int[sku_id] = value_dict['count']
		if value_dict['selected']:
			redis_cart_set_list.append(sku_id)

	# 更新hash_cart
	redis_conn.hmset('cart_%s' % user.id, redis_cart_dict_to_int)
	# 更新set_cart
	redis_conn.sadd('cart_selected_%s' % user.id, *redis_cart_set_list)

	response.delete_cookie('cart')
	return response
