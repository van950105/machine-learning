import sys
import csv
import math
import copy

EXAMPLE = {"love":["yes","no"],"debut":["yes","no"],"hit":["yes","no"]}
MUSIC={"year":["before1950","after1950"],"solo":["yes","no"],"vocal":["yes","no"],"jazz":["yes","no"],\
"length":["morethan3min","lessthan3min"],"original":["yes","no"],"tempo":["fast","slow"],\
"folk":["yes","no"],"classical":["yes","no"],"rhythm":["yes","no"],\
"rock":["yes","no"],"hit":["yes","no"]}
grades=["A","notA"]
EDUCATION={"M1":grades,"M2":grades,"M3":grades,"M4":grades,"M5":grades,"P1":grades,\
"P2":grades,"P3":grades,"P4":grades,"F":grades,"grade":grades}
CARS={"buying":["expensive","cheap"],"maint":["high","low"],"doors":["Two","MoreThanTwo"],\
"person":["Two","MoreThanTwo"],"boot":["small","large"],"safety":["low","high"],"class":["yes","no"]}
ATTRIBUTESLIST=[EXAMPLE,MUSIC,EDUCATION,CARS]
errorList=[]

def main():
	filenameTrain=sys.argv[1]
	filenameTest=sys.argv[2]
	with open(filenameTrain,"rb") as csvfile:
		f=csv.reader(csvfile)
		posLabel=0
		negLabel=0
		counting = 0
		for row in f:
			if counting== 0: 	
				attributes=row
				label=row[-1]
			if row[-1]== "yes" or row[-1]== "A":
				posLabel+=1
			elif row[-1]=="no" or row[-1]=="notA":
				negLabel+=1
			counting+=1
	print "["+str(posLabel)+"+/"+str(negLabel)+"-]"
	trainHelper(filenameTrain,attributes,posLabel,negLabel,[],0,label)
	calculateError(filenameTrain,'train',attributes)
	calculateError(filenameTest,'test',attributes)

def trainHelper(filenameTrain,attributes,pos,neg,prev,level,label):
	if len(prev)+1<len(attributes) and level<2:
		mutualInfoDict=dict()
		maxAttr=""
		for attrs in attributes:
			if attrs!=label and checkCond(prev,attrs):
				(a,b,c,d)=trainHelperHelper(prev,filenameTrain,attrs,label)
				mutualInfo=mutualInfoHelper(a+c,b+d,a,b,c,d)
				mutualInfoDict[attrs]=(mutualInfo,a,b,c,d)
		v=sorted(mutualInfoDict.values())[-1]
		value=v[0]
		for key in mutualInfoDict:
			if (abs(mutualInfoDict[key][0]-value)<0.000000001):
				maxAttr=key
		posLabel=getAttributes(maxAttr)[0]
		negLabel=getAttributes(maxAttr)[1]
		if value>0.1:
			labels=[label,getAttributes(label)[0],getAttributes(label)[1]]
			prevA=copy.deepcopy(prev)
			prevB=copy.deepcopy(prev)
			printhelper(maxAttr,level,posLabel,mutualInfoDict[maxAttr][1],mutualInfoDict[maxAttr][2],prevA,labels)
			prevA.append([maxAttr,getAttributes(maxAttr)[0]])
			levelA=level+1
			levelB=level+1
			trainHelper(filenameTrain,attributes,pos,neg,prevA,levelA,label)
			printhelper(maxAttr,level,negLabel,mutualInfoDict[maxAttr][3],mutualInfoDict[maxAttr][4],prevB,labels)
			prevB.append([maxAttr,getAttributes(maxAttr)[1]])
			trainHelper(filenameTrain,attributes,pos,neg,prevB,levelB,label)


def checkCond(prev,attr):
	if prev!=[]:
		for attrs in prev:
			if attrs[0]==attr:
				return False
	return True

def printhelper(attr,levels,name,posCount,negCount,prev,labels):
	if levels>0:
		sys.stdout.write("|"+" "*levels*2)
	tempDict=dict()
	tempDict['level']=levels
	tempDict['info']=prev
	tempDict['label']=labels
	tempDict['actual']=""
	errorList.append(tempDict)
	print attr+"= "+name+": [" + str(posCount)+"+/"+str(negCount)+"-]" 	

def trainHelperHelper(prev,name,attr,label):
	with open(name,"rb") as csvfile:
		f=csv.reader(csvfile)
		counting=0
		index=0
		aPosCount=0
		aNegCount=0
		bPosCount=0
		bNegCount=0
		[a,b]=getAttributes(attr)
		[c,d]=getAttributes(label)
		for row in f:
			if counting==0:
				attrIndex = row.index(attr)
				labelIndex=row.index(label)
				prevIndex=[]
				prevIndexRela=[]
				for i in prev:
					prevIndex.append(row.index(i[0]))
					prevIndexRela.append(i[1])
			else:
				if prev==[] or countingCond(row,prevIndex,prevIndexRela):
					if row[attrIndex]==a and row[labelIndex]==c:
						aPosCount+=1
					elif row[attrIndex]==a and row[labelIndex]==d:
						aNegCount+=1
					elif row[attrIndex]==b and row[labelIndex]==c:
						bPosCount+=1
					elif row[attrIndex]==b and row[labelIndex]==d:
						bNegCount+=1
			counting+=1
		return (aPosCount,aNegCount,bPosCount,bNegCount)

def countingCond(row,prevIndex,prevIndexRela):
	i=0
	for i in xrange (len(prevIndex)):
		if row[prevIndex[i]]!=prevIndexRela[i]:
			return False
	return True




def getAttributes(name):
	for attrs in ATTRIBUTESLIST:
		if name in attrs:
			return attrs[name]


def mutualInfoHelper(pos,neg,posA,negA,posB,negB):
	totalEntrop=entropHelper(pos,neg)
	total=float(posA+negA+posB+negB)
	condEntropA=(posA+negA)/total*entropHelper(posA,negA)
	condEntropB=(posB+negB)/total*entropHelper(posB,negB)
	return totalEntrop-condEntropA-condEntropB


def entropHelper(a,b):
	a=float(a)
	b=float(b)
	entrop=0
	if a==0 or b==0:
		return 0
	else:
		return a/(a+b)*math.log((a+b)/a,2)+b/(a+b)*math.log((a+b)/b,2)



def calculateError(name,string,attributes):
	i=0
	correct=0
	wrong=0
	for i in xrange (len(errorList)):
		if  (i+1==(len(errorList))) or (i+1<xrange(len(errorList)) \
			and errorList[i]['level']>=errorList[i+1]['level']):
			(posCount,negCount)=countErrorHelp(errorList[i],name,attributes)
			if string=="train":
				if posCount>=negCount:
					errorList[i]['actual']='pos'
					correct+=posCount
					wrong+=negCount
				else:
					errorList[i]['actual']='neg'
					correct+=negCount
					wrong+=posCount
			else:
				if errorList[i]['actual']=='pos':
					correct+=posCount
					wrong+=negCount
				else:
					correct+=negCount
					wrong+=posCount
	rate=0 if wrong ==0 else float(wrong)/(correct+wrong)
	print "error("+string+"): " +str(rate)

def countErrorHelp(data,name,attributes):
	with open(name,"rb") as csvfile:
		f=csv.reader(csvfile)
		newIndexList=[]
		newRelative=[]
		posCount=0
		negCount=0
		posInfo=data['label'][1]
		negInfo=data['label'][2]
		labelIndex=attributes.index(data['label'][0])
		for l in data['info']:
			newIndexList.append(attributes.index(l[0]))
			newRelative.append(l[1])
		for row in f:
			if countingCond(row,newIndexList,newRelative):
				if row[labelIndex]==posInfo:
					posCount+=1
				elif row[labelIndex]==negInfo:
					negCount+=1
		return (posCount,negCount)


main()


