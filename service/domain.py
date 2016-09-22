#!c:/python27/python
import util
import json
import datetime

class Employee:

	def __init__(self, name, role, email, j):
		if j == None:
			self.name = name
			self.email = email
			self.role = role
			self.eid = util.generateID(6)
		else:
			self.__dict__ = json.loads(j)


class Workflow:

	pending = "P"
	success = "S"
	failed = "F"

	def __init__(self, j):
		if j==None:
			self.pmflag = False
			self.flow_ID = util.generateID(8)
			self.data = None
			self.status = None
			self.isSimple = True
			self.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		else:
			self.__dict__ = json.loads(j)

	def setData(self, data):
		self.data = data

	def assignPMForSize(self, name):
		self.sizePM = name
		self.pmflag = True

	def configSimpleFlow(self, name):
		flow = []
		stages = [1]
		stages[0] = Workstage(None, 1, Workflow.pending, Workstage.PM2)

	
		flow.append(stages)
		flow.append([])
		flow.append([])
		self.flow = flow
		self.name = name
		print "simple flow init, flow size = " + str(len(flow))

	def getCurrentStageNumber(self):
		cur = 1
		for idx, stages in enumerate(self.flow):
			if len(stages) > 0:
				print "DEBUG: index->"+str(idx) +", size of stages in flow : " + str(len(stages))
				for workstage in stages:
					if workstage.status != Workflow.success:
						print "DEBUG: current stage = " + str(workstage.stage)
						return workstage.stage
					else:
						cur = workstage.stage
			else:
				print "DEBUG: index->"+str(idx) +" empty slot"
		return cur

# int nextStage, workstage[] stage_list
	def initNextStage(self, nextStage, stage_list):
		if (stage_list==None) | (len(stage_list)<1):
			print "next stage list cannot be null!!"
			return
		if self.name == "simple":
			if nextStage >= 3:
				print "ALL approved, GREEN!"
			else:
				self.flow[nextStage-1] = stage_list
				print "assigning " + str(len(stage_list)) + " items to stage " + str(nextStage)
		else:
			print "non-simple case not implemented"

	def getCurrentStages(self):
		return self.flow[self.getCurrentStageNumber()-1]

	def setTeam(self, team_code, team):
		self.team_code = team_code
		self.team = team

	def setProgram(self, program_code, program):
		self.program_code = program_code
		self.program = program

	def setRTN(self, rtn):
		self.rtn = rtn

	def getCurStatusDesc(self):
		stages = self.getCurrentStages()
		if(len(stages) > 0):
			return stages[0].status_desc
		else:
			return None
			
# each work stage represents an item in the pending list
class  Workstage:

	PM2 = "Waiting for Analyst Selection"
	AN3 = "Waiting for Analyst Assessment"
	PM4 = "Waiting for Project Manager Approvement"
	PM5 = "Approved"
	idsize = 6

	def __init__(self, j, stage, status, status_desc):
		if j == None:
			self.status = status
			self.status_desc = status_desc
			self.stage = stage
			self.stage_ID = util.generateID(8)
			self.data = None
			print self.toString() + " init-ed"
		else:
			self.__dict__ = json.loads(j)

	def setData(self, data):
		self.data = data

	def approve(self):
		if self.status != Workflow.success:
			print self.toString() + " approved"
			self.status = Workflow.success
		else:
			print self.toString() + " already approved"

	def disapprove(self):
		if self.status != Workflow.failed:
			print self.toString() + " disapproved"
			self.status = Workflow.failed
		else:
			print self.toString() + " already disapproved"

	def toString(self):
		return self.stage_ID + "-> status [" + self.status + "] " + self.status_desc + " at stage (" + str(self.stage) + ")"

	def assignEmployee(self, employee):
		self.employee = employee
