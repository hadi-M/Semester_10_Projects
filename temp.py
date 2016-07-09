
class One(object):
	hello = None
	def __init__(self, r):
		One.hello = r


class R(object):
	def __init__(self):
		pass


r = R()
one = One(r)
