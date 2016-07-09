import simpy
import random
import math

arrT1 = 0
arrT2 = 0
# ------------------------------------------------------------------
#	Random Generator
# ------------------------------------------------------------------

def expgen (mean_value):
	x = random.uniform(0, 1)
	return (-math.log(1-x)*(1/mean_value))
# ------------------------------------------------------------------
#	Queue
# ------------------------------------------------------------------

class Queue(object):
	def __init__(self, q_name, q_size, q_type):
		self.q_name = q_name
		self.q_size = q_size
		self.q_type = q_type
		self.myQ = []

	def is_empty(self):
		if len(self.myQ) > 0:
			return False
		else:
			return True

	def is_full(self):
		if len(self.myQ) < self.q_size:
			return False
		else:
			return True

	def add_to_q(self, arr_proc):
		if not self.is_full():
			return self.myQ.append(arr_proc)
		else:
			return False

	def remove_from_q(self, index):
		return self.myQ.pop(index)

	def random_type(self):
		if not self.is_empty():
			index = random.randint(0, len(self.myQ)-1)
			return self.remove_from_q(index)
		else:
			return False

	def srjf(self):
		if not self.is_empty():
			exe_min = self.myQ[0].exeTime
			min_index = 0
			temp = 0
			for i in self.myQ:
				if i.exeTime < exe_min:
					exe_min = i.exeTime
					min_index = temp
				temp += 1
			return self.remove_from_q(min_index)
		else:
			return False

	def q_elem (self):
		return self.myQ
# ------------------------------------------------------------------
#	Preprocessor (SRJF)
# ------------------------------------------------------------------

class Preprocr1(Queue):
	idle = []
	busy = []
	exeJob = []
	intJob = None
	intFlage = 0
	totWait = 0.0
	Njobs = 0
	def __init__(self, env, mainproc):
		Queue.__init__(self, 'Preprocessor 1', 100, 'SRJF')
		self.env = env
		self.mainproc = mainproc
		self.startExeT = 0
		Preprocr1.idle.append(self)
		self.pre1_run = env.process(self.run())

	def run(self):
		while True:
			if self.is_empty or self.mainproc.is_full:
				print('Passive Mode----------------------------------------')
				yield Preprocr1.pre1_run_react # Passive mode
			Preprocr1.idle.remove(self)
			Preprocr1.busy.append(self)
			while not self.is_empty():
				if ArrivalClass1.idle != [] and Preprocr1.intFlage == 0:
					ArrivalClass1.arr1_run_react.succeed() # Activate ArrivalClass
					ArrivalClass1.arr1_run_react = env.event()
				j = self.srjf()
				Preprocr1.exeJob.append(j)
				print('Size of Q in Pre1:', len(self.myQ))
				print('Job %d and arrival time %f' % (Preprocr1.Njobs, j.arrivalTime))
				exeTime = j.exeTime
				if Preprocr1.intFlage == 1:
					self.add_to_q(Preprocr1.intJob)
				try:
					self.startExeT = self.env.now
					yield self.env.timeout(exeTime)
					print('Exiting Time:', self.env.now)
					Preprocr1.intFlage = 0
					Preprocr1.exeJob.remove(j)
					# self.mainproc.add_to_q(j)
					Preprocr1.totWait += self.env.now - j.arrivalTime
					Preprocr1.Njobs += 1
				except simpy.Interrupt:
					print('Iterrupt occured at:', self.env.now)
					j.exeTime = j.exeTime - (self.env.now - self.startExeT)
					Preprocr1.exeJob.remove(j)
					Preprocr1.intJob = j
					Preprocr1.intFlage = 1

			Preprocr1.idle.append(self)
			Preprocr1.busy.remove(self)
# ------------------------------------------------------------------
#	Preprocessor (Random)
# ------------------------------------------------------------------

class Preprocr2(Queue):
	idle = []
	busy = []
	totWait = 0.0
	Njobs = 0
	def __init__(self, env, mainproc):
		Queue.__init__(self, 'Preprocessor 2', 12, 'Random Type')
		self.env = env
		self.mainproc = mainproc
		Preprocr2.idle.append(self)
		self.pre2_run = env.process(self.run())

	def run(self):
		while True:
			if self.is_empty or self.mainproc.is_full:
				yield Preprocr2.pre2_run_react # Passive mode
			Preprocr2.idle.remove(self)
			Preprocr2.busy.append(self)
			while not self.is_empty():
				if ArrivalClass2.idle != []:
					ArrivalClass2.arr2_run_react.succeed() # Activate ArrivalClass
					ArrivalClass2.arr2_run_react = env.event()
				j = self.random_type()
				print('Size of Q in Pre2:', len(self.myQ))
				print('Job %d and arrival time %f' % (Preprocr2.Njobs, j.arrivalTime))
				exeTime = j.exeTime
				yield self.env.timeout(exeTime)
				print('Exiting Time:', self.env.now)
				# self.mainproc.add_to_q(j)
				Preprocr2.totWait += self.env.now - j.arrivalTime
				Preprocr2.Njobs += 1
			Preprocr2.idle.append(self)
			Preprocr2.busy.remove(self)
# ------------------------------------------------------------------
#	Main Processor
# ------------------------------------------------------------------

class Mainprocr(Queue):
	idle = []
	busy = []
	totWait = 0.0
	def __init__(self, env):
		Queue.__init__(self, 'Main', 50, 'Round Robin')
		self.env = env
		Mainprocr.idle.append(self)
		self.main_run = env.process(self.run())
		

	def run(self):
		while True:
			yield Mainprocr.main_run_react # Passivating
			Mainprocr.idle.remove(self)
			Mainprocr.busy.append(self)
			while not self.is_empty():
				j = self.random_type()
				exeTime = j.exeTime
				yield self.env.timeout(exeTime)
				Preprocr2.totWait += self.env.now - j.arrivalTime
			Mainprocr.idle.append(self)
			Mainprocr.busy.remove(self)
# ------------------------------------------------------------------
# ------------------------------------------------------------------
# ------------------------------------------------------------------
#	Job Class
# ------------------------------------------------------------------

class JobClass(object):

	def __init__(self, env, exeTime, exeTime_K3):
		self.arrivalTime = env.now
		self.exeTime = exeTime
		self.exeTime_K3 = exeTime_K3
# ------------------------------------------------------------------
#	Arrival Time Creator For Preprocessor 1
# ------------------------------------------------------------------

class ArrivalClass1(object):
	idle = []
	def __init__(self, env, pre1):
		self.env = env
		self.arr_run = env.process(self.run())
	def run(self):
		while True:
			if pre1.is_full():
				ArrivalClass1.idle.append(self)
				print('................Arrival 1 Going to passive mode................')
				yield ArrivalClass1.arr1_run_react # Passive mode
				ArrivalClass1.idle.remove(self)

			exeTime = expgen(5)
			inarrTime = expgen(7)
			exeTime_K3 = expgen(1)
			yield self.env.timeout(inarrTime)
			j = JobClass(self.env, exeTime, exeTime_K3)			
			pre1.add_to_q(j)
			if Preprocr1.exeJob != []:
				remainT = Preprocr1.exeJob[0].exeTime - (self.env.now - pre1.startExeT)
				if j.exeTime < remainT:
					pre1.pre1_run.interrupt()
			if Preprocr1.idle != []:
				Preprocr1.pre1_run_react.succeed()
				Preprocr1.pre1_run_react = env.event()

# ------------------------------------------------------------------
#	Arrival Time Creator For Preprocessor 2
# ------------------------------------------------------------------
class ArrivalClass2(object):
	idle = []
	def __init__(self, env, pre2):
		self.env = env
		self.arr_run = env.process(self.run())

	def run(self):
		while True:
			if pre2.is_full():
				ArrivalClass2.idle.append(self)
				print('................Arrival 2 Going to passive mode................')
				yield ArrivalClass2.arr2_run_react # Passive mode
				ArrivalClass2.idle.remove(self)

			exeTime = expgen(3)
			inarrTime = expgen(2)
			exeTime_K3 = expgen(1)
			yield self.env.timeout(inarrTime)
			j = JobClass(self.env, exeTime, exeTime_K3)
			pre2.add_to_q(j)
			if Preprocr2.idle != []:
				Preprocr2.pre2_run_react.succeed()
				Preprocr2.pre2_run_react = env.event()

# ------------------------------------------------------------------
# ------------------------------------------------------------------
# ------------------------------------------------------------------
env = simpy.Environment()
ArrivalClass1.arr1_run_react = env.event()
ArrivalClass2.arr2_run_react = env.event()
Mainprocr.main_run_react = env.event()
Preprocr1.pre1_run_react = env.event()
Preprocr2.pre2_run_react = env.event()

mainproc = Mainprocr(env)
pre1 = Preprocr1(env, mainproc)
pre2 = Preprocr2(env, mainproc)
arrival1 = ArrivalClass1(env, pre1)
arrival2 = ArrivalClass2(env, pre2)

env.run(until=20)
