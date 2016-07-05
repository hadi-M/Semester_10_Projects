import simpy

class Car(object):
	def __init__(self, env, bcs, name, driving_time=3, charge_duration=2):
		self.env = env
		self.bcs = bcs
		self.driving_time = driving_time
		self.name = name
		self.charge_duration = charge_duration
		self.action = env.process(self.run())

	def run(self):
		yield self.env.timeout(self.driving_time)
		print("car %s arriving at: %d" % (self.name, self.env.now))

		with self.bcs.request() as req:
			yield req
			print('car %s start of charging %d' % (self.name, self.env.now))
			yield self.env.timeout(self.charge_duration)
			print('car %s end of charging %d' % (self.name, self.env.now))


	def charge(self):
		print('car %s start of charging %d' % (self.name, self.env.now))
		yield self.env.timeout(self.charge_duration)
		print('car %s end of charging %d' % (self.name, self.env.now))


env = simpy.Environment()
bcs = simpy.Resource(env, capacity=2)
for i in range(4):
	car = Car(env, bcs, i, 2*i, 5)
env.run()