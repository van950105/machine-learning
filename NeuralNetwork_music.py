import random
import math
import csv
import sys

def sigmoid(x):
	return 1/(1.0+math.exp(-x))

class Node:
	def __init__(self,nodeType):
		self.outEdges=[]
		self.inputEdges=[]
		self.type=nodeType
		self.delta=None
		self.label=None
		self.value=None
		self.output=None

class Edge:
	def __init__(self,source,target):
		self.weight=random.uniform(0.1,0.2)
		self.source=source
		self.target=target
		source.outEdges.append(self)
		target.inputEdges.append(self)

class Network:
	def __init__(self,theta,hidUnits,numInput):
		self.theta=theta
		self.hidUnits=hidUnits
		self.hidList=[]
		self.inputList=[]
		self.inputEdges=[]
		self.outputEdges=[]
		self.output=Node("output")
		self.stdErr=0
		for i in xrange(hidUnits+1):
			temp=Node("hid")
			self.hidList.append(temp)
			self.outputEdges.append(Edge(self.hidList[i],self.output))
		for j in xrange(numInput+1):
			self.inputList.append(Node("input"))
			temp=[]
			for k in xrange(hidUnits):
				temp.append(Edge(self.inputList[j],self.hidList[k]))
			self.inputEdges.append(temp)

	def train(self,examples):
		vec=examples[0]
		label=examples[1]
		vec.append(1)
		for i in xrange(len(self.inputList)):
			self.inputList[i].value=vec[i]
		o=self.eval()
		self.stdErr+=0.5*(label-o)**2
		self.deltaOutput(o,label)
		self.deltaHidden()
		self.updateWeight()


	def eval(self):
		sumOut=0
		for i in xrange(len(self.hidList)-1):
			sumHid=0
			for j in xrange(len(self.inputList)):
				weight=self.inputEdges[j][i].weight
				inputValue=self.inputList[j].value
				sumHid+=weight*inputValue
			output=sigmoid(sumHid)
			self.hidList[i].output=output
			self.hidList[i].value=sumHid
			sumOut+=self.outputEdges[i].weight*output
		sumOut+=1*self.outputEdges[-1].weight
		return sigmoid(sumOut)

	def deltaOutput(self,o,label):
		#print "o="+str(o),"label="+str(label)
		delta=o*(1-o)*(label-o)
		self.output.delta=delta

	def deltaHidden(self):
		for i in xrange(len(self.hidList)-1):
			output=self.hidList[i].output
			delta=output*(1-output)*self.outputEdges[i].weight*self.output.delta
			#print "output="+str(output),"weight="+str(self.outputEdges[i].weight),"delta="+str(self.output.delta),"result="+str(delta)
			self.hidList[i].delta=delta

	def updateWeight(self):
		theta=self.theta
		for i in xrange(len(self.hidList)-1):
			for j in xrange(len(self.inputList)):
				delta=theta*self.hidList[i].delta*self.inputList[j].value
				self.inputEdges[j][i].weight+=delta
			delta=theta*self.output.delta*self.hidList[i].value
			self.outputEdges[i].weight+=delta
		delta=theta*self.output.delta*1
		self.outputEdges[-1].weight+=delta

	def test(self,test):
		sumOut=0
		for i in xrange(len(self.hidList)-1):
			sumHid=0
			for j in xrange(len(self.inputList)-1):
				weight=self.inputEdges[j][i].weight
				inputValue=test[j]
				sumHid+=weight*inputValue
			output=self.outputEdges[i].weight*sigmoid(sumHid)
			sumOut+=output
		return sigmoid(sumOut)



def main():
	fileName = sys.argv[1]
	testFileName = sys.argv[2]
	with open(fileName,"rb") as csvfile:
		f=csv.reader(csvfile)
		temp=[]
		for row in f :
			temp.append(row)
		a=temp.pop(0)
		for attr in temp:
			for j in xrange(len(temp[0])):
				if a[j]=="Year":
					attr[j]=float(attr[j])
					attr[j]-=1950
					attr[j]=attr[j]
				elif attr[j]=="yes":
					attr[j]=1.0
				elif attr[j]=="no":
					attr[j]=0.0
				else:
					attr[j]=float(attr[j])-5.32
	numInput=len(temp[0])-1
	theta=0.01
	hidUnits=3
	nnw=Network(theta,hidUnits,numInput)
	for i in xrange(len(temp)):
		nnw.train((temp[i][:-1],temp[i][-1]))
	newStderr=nnw.stdErr
	oldStderr=10**10
	nnw.stdErr=0
	iteration=0
	while newStderr<oldStderr and iteration<1000:
		for i in xrange(len(temp)):
			nnw.train((temp[i][:-1],temp[i][-1]))
		oldStderr=newStderr
		newStderr=nnw.stdErr
		if newStderr<oldStderr:
			print nnw.stdErr
		nnw.stdErr=0
		iteration+=1
	nnw.stdErr=0
	print "TRAINING COMPLETED! NOW PREDICTING."
	test(testFileName,nnw)

def test(testFileName,nnw):
	with open(testFileName,"rb") as csvfile:
		f=csv.reader(csvfile)
		temp=[]
		for row in f :
			temp.append(row)
		a=temp.pop(0)
		for attr in temp:
			for j in xrange(len(temp[0])):
				if a[j]=="Year":
					attr[j]=float(attr[j])
					attr[j]-=1950
					attr[j]=attr[j]
				if attr[j]=="yes":
					attr[j]=1.0
				if attr[j]=="no":
					attr[j]=0.0
				else:
					attr[j]=float(attr[j])-5.32
		for i in temp:
			t=nnw.test(i)
			if t>0.5:
				print "yes"
			else:
				print "no"

main()
