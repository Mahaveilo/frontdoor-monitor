#!c:/python27/python

import util
import db
from domain import Employee
from domain import Workflow
from domain import Workstage

# ***************************************** Workflow methods ************************************************
teamMap = {}
teamMap['Risk and Authetication'] = "xsurgm238425"
teamMap['Data Platform'] = "avnysb509043"
teamMap['Business Intelligence'] = "ztdrbh099982"
teamMap['Commercial'] = "mlqezb440981"
teamMap['Loyalty and Marketing'] = "epwkkx828208"


#first request from creation page calls this method
#PM assigned, @return Workflow
def createNewSimpleWorkFlowStage(request):
	w = Workflow(None)
	w.configSimpleFlow("simple")
	assignPMToStage(w, request)
	teams = getTeamsFromRequest(request)
	programs = getProgramsFromRequest(request)
	w.setTeam(None, teams)
	w.setProgram(None, programs)
	data = getDataFromRequest(request)
	w.setData(data)
	w.status = w.getCurStatusDesc()
	db.insertDummy(w)
	return w

#second request for PM to assign the analyts
#analyst assigned, @return Workflow
def analystAssignmentStage(request):
	print "\n-------> move to analyst stage:\n"
	#get w from DB, assign analyst
	f_id = getFlowIdFromRequest(request)
	f = db.findByFlowId(f_id)[0]
	assignanalystToStage(f, request)
	#persist them inside database
	f.status = f.getCurStatusDesc()
	db.updateFlow(f)
	#return the entire w
	return f

#request coming from Pending page, triggered when an analyst submit a done
#one analyst finished the task
def analystAssessment(request):
	#get w from DB,
	f_id = getFlowIdFromRequest(request)
	f = db.findByFlowId(f_id)[0]
	stages2 = f.flow[1]

	analystId = getAnalyticsIDFromRequest(request)
	allAssessmentDone = True
	for stage in stages2:
		if stage.employee.eid == analystId:
			print "analystId: " +analystId+" matches the stage Id: " + stage.employee.eid
			if(stage.status=="S"):
				print "Error: this task is already been assessed"
			stage.status="S"
			stage.status_desc=Workstage.PM4
			stage.setData(getDataFromAnalystAssessmentRequest(request))
		else:
			print "analystId: " +analystId+" doesn't match the stage Id: " + stage.employee.eid

	for stage in stages2:
		if stage.status != "S":
			allAssessmentDone = False
	#check all analyst done, if so, update flow to 3rd stage
	if allAssessmentDone:
		moveToPMApproveStage(request, f)
	#persist inside database
	f.status = f.getCurStatusDesc()
	db.updateFlow(f)
	print "one analyst task finished"
	return f

#request coming from Pending page, triggered by PM
#get PM from w itself, update PM and persist, @return Workflow
def moveToPMApproveStage(request, workflow):

	#update PM_stage, duplicate that PM_stage to 3rd stages
	stages1 = workflow.flow[0]
	if(len(stages1)<1):
		raise ValueError("There is no PM stage in the first stages, flow id = " + workflow.flow_ID)
	st1 = stages1[0]
	st1.status_desc = Workstage.PM4

	stages3 = workflow.flow[2]
	if(len(stages3)>0):
		print "Already at 3rd stage"
	else:
		newStage = Workstage(None, 3, Workflow.pending, Workstage.PM4)
		newStage.assignEmployee(st1.employee)
		stages3.append(newStage)
		print "move to PM final approve stage"

#limited to 1 PM at this point
def PMApprove(request):
	pmid = getPMIDFromRequest(request)
	f_id = getFlowIdFromRequest(request)
	f = db.findByFlowId(f_id)[0]
	stages3 = f.flow[2]
	if(len(stages3)<1):
		raise ValueError("There is no stage in 3rd stages yet")
	st3 = stages3[0]
	if pmid != st3.employee.eid:
		raise ValueError("PM Id not matched for approvement")
	if st3.status == 'S':
		raise ValueError("The Project has been approved already")
	st3.status == 'S'
	st3.status_desc = Workstage.PM5
	st3.setData(getDataFromPMApprovalRequest(request))

	#update all the previous status_desc
	stages2 = f.flow[1]
	for stage in stages2:
		stage.status_desc = Workstage.PM5
	stages1 = f.flow[0]
	for stage in stages1:
		stage.status_desc = Workstage.PM5
	f.status =f.getCurStatusDesc()
	db.updateFlow(f)
	return f

# ***************************************** Assign employees to stages ************************************************

#call after 1st stage instantiated
def assignPMToStage(workflow, request):
	pm = getPMFromRequest(request)
	stage = workflow.flow[0][0]
	stage.assignEmployee(pm)
	print "assigning PM to stage"

#call after 2nd stage instantiated
def assignanalystToStage(workflow, request):
	print "assigning analyst to stages .."
	stage1 = workflow.flow[0][0]
	if (stage1.status == "S"):
		# raise ValueError("stage1 is S, analyst already assigned")
		print "stage1 is S, analyst already assigned"
	stage1.status = "S"
	stage1.status_desc = Workstage.AN3
	stage1.setData(getDataFromAssignAnalystRequest(request))
	#getanalystFromRequest = anas
	anas = getAnalystFromRequest(request)
	cur=workflow.getCurrentStageNumber()
	stages = []
	#assign anas to each stage, respectively
	for ana in anas:
		tmp = Workstage(None, cur + 1, Workflow.pending, Workstage.AN3)
		tmp.assignEmployee(ana)
		stages.append(tmp)
	workflow.initNextStage(cur + 1, stages)

#call after 3rd stage instantiated
def finalPMApprove(workflow, request):
	print "PM final approving"

def getPMFromRequest(request):
	pmId = getPMIDFromRequest(request)
	pm = db.getEmployeeById(pmId)
	if (pm.role!="PM") & (pm.role!="Project Manager"):
		raise ValueError("Not a Project Manager")
	return pm

def getAnalystFromRequest(request):
	analystIds = getAnalyticsIDsFromRequest(request)
	anas = []
	for aid in analystIds:
		analyst = db.getEmployeeById(aid)
		if analyst.role != "Analyst":
			raise ValueError("Not a Analyst")
		anas.append(analyst)
	return anas

def getCurrentUserFromRequest(request):
	raise ValueError("Not implemented")

def createNewEmployee(name, role):
	e = Employee(name, role, None)
	db.insertEmployee(e)

def createNewPM(name):
	createNewEmployee(name, "Project Manager")

def createNewAnalyst(name):
	createNewEmployee(name, "Analyst")




# ************************************************************** E N D *********************************************************************
# fUNCTIONS below needs to be implemented from other modules:
# e.g. import rest_module, and call out those methods
# ********************************** Area 52 ****************************************
#Test methods                                                                   *****
#@Govind, you need provide following funcions from REST layer to use the module.
#for now, I am just faking the objects returned from request object

#extract pm information from request, just a name and role for now
#similarly, extract analyst information
def getPMIDFromRequest(request):
    teamtype = request["teamType"]
    return teamMap[teamtype];

def getAnalyticsIDFromRequest(request):
	# return "zcfqke061605"
	return "oxsqtr318710"

def getAnalyticsIDsFromRequest(request):
	res = ['oxsqtr318710','jzigml339281'];
	return res

def getanalyst(request):
	randomid = util.generateID(8)
	randomid2 = util.generateID(8)
	ana1 = Employee("Joe", "analyst")
	ana2 = Employee("Raman", "analyst")
	ana = []
	ana.append(ana1)
	ana.append(ana2)
	return ana
#extract flow id from request
def getFlowIdFromRequest(request):
	return "pichtwei41981489"

def getTeamsFromRequest(request):
	# res = []
	# res.append("R")
	# res.append("Risk and Authetication")
        return request['teamType']

def getProgramsFromRequest(request):
	# res = []
	# res.append("R")
	# res.append("Account Level Management (ALM)")
	# return res
        return request['programname']

def getAllUsers(request):
	return db.getAllEmployees()

def getDataFromRequest(request):
	return request

def getDataFromAssignAnalystRequest(request):
	data = '{"RTN": "820820","projectname": "Rewards Redemption","programname": "Loyalty and Marketing", "Analyst Count":"2"}'
	return data

def getDataFromAnalystAssessmentRequest(request):
	data = '{"RTN": "820820","Assessment":"$100,000"}'
	return data

def getDataFromPMApprovalRequest(request):
	data = '{"Approved":"True","Comments":"Nice job, Govind"}'
	return data

# *******                                                                     *******
# ********************************** Area 52 ****************************************

# the main body
print "Smoke Test Begin .. "

# @simple test for service
print "__Service__"

# @simple test for database
print "__DataBase__"

print "__Web service calls__"

# >> First request method avaiable <<
# w = createNewSimpleWorkFlowStage(None)

# >> Second request method available <<
# wf = analystAssignmentStage(None)

# >> once you got an workflow instance, you can use wf to get the status
# print wf.getCurStatusDesc()

# >> analyst assesment request
# analystAssessment(None)

# >> PM approve request
# PMApprove(None)


print "__create employees__"
# employees
# createNewEmployee("Kyle", "PM")
# createNewEmployee("Tom", "Analyst")
# createNewEmployee("Steve", "Analyst")

# createNewEmployee("John", "PM");
# createNewEmployee("Chris", "PM");
# createNewEmployee("Paul", "PM");
# createNewEmployee("Ben", "PM");


# getPMFromRequest(None)
# getAllUsers(None)








