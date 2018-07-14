def jwt_response_payload_handler(token, user=None, request=None):
	"""自定义JWT返回的内容,默认只有token"""

	return {
		'token': token,
		'user_id': user.id,
		'username': user.username
	}
