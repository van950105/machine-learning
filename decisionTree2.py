import sys
import csv
import math
import copy

EXAMPLE = {"love":["yes","no"],"debut":["yes","no"],"hit":["yes","no"]}
MUSIC={"year":["before1950","after1950"],"solo":["yes","no"],"vocal":["yes","no"],\
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
			if row[-1]== "yes" or row[-1]== "A":
				posLabel+=1
			elif row[-1]=="no" or row[-1]=="notA":
				negLabel+=1
			counting+=1
	print "["+str(posLabel)+"+/"+str(negLabel)+"-]"
	trainHelper(filenameTrain,attributes,posLabel,negLabel,[],0)
	#calculateError(filenameTrain,"train")
	#calculateError(filenameTest,"test")

def trainHelper(filenameTrain,attributes,pos,neg,cond,level):
	if level==3 or len(attributes)-1==level:
		return False
	else:
		with open (filenameTrain,"rb") as csvfile:
			f=csv.reader(csvfile)
			counting=0
			labelList=[]
			posA=0
			posB=0
			negA=0
			negB=0
			for row in f:
				if counting==0:
					attributeName=row[len(cond)]
					[a,b]=getAttributes(attributeName)
					[c,d]=getAttributes(row[-1])
				else:
					(posA,negA,posB,negB)=countHelp(row,a,b,c,d,posA,negA,posB,negB,cond)
				counting+=1
			condA=copy.deepcopy(cond)
			condB=copy.deepcopy(cond)
			condA.append(a)
			condB.append(b)
			levelA=level
			levelB=level
			if mutualInfoHelper(pos,neg,posA,negA,posB,negB) or len(cond)==0:
				if level>0:
					sys.stdout.write("|"+" "*level*2)
				print attributeName+"= yes: [" + str(posA)+"+/"+str(negA)+"-]" 
				levelA+=1
			lowestA=trainHelper(filenameTrain,attributes,posA,negA,condA,levelA)
			if lowestA==False:
				condA.append(c if posA>negA else d)
				errorList.append(condA)
			if mutualInfoHelper(pos,neg,posA,negA,posB,negB) or len(cond)==0:	
				if level>0:
					sys.stdout.write("|"+" "*level*2)
				print attributeName+"= no: [" + str(posB)+"+/"+str(negB)+"-]"
				levelB+=1
			lowestB=trainHelper(filenameTrain,attributes,posB,negB,condB,levelB)
			if lowestB==False:
				condB.append(c if posB>negB else d)
				errorList.append(condB)
			return not(mutualInfoHelper(pos,neg,posA,negA,posB,negB))

def getAttributes(name):
	for attrs in ATTRIBUTESLIST:
		if name in attrs:
			return attrs[name]

def countHelp(row,a,b,c,d,posA,negA,posB,negB,cond):
	length=len(cond)
	for i in xrange (length):
		if row[i]!=cond[i]:
			return (posA,negA,posB,negB)
	if row[length]==a:
		if row[-1]==c:
			return (posA+1,negA,posB,negB)
		else:
			return (posA,negA+1,posB,negB)
	else:
		if row[-1]==c:
			return (posA,negA,posB+1,negB)
		else:
			return (posA,negA,posB,negB+1) 


def mutualInfoHelper(pos,neg,posA,negA,posB,negB):
	totalEntrop=entropHelper(pos,neg)
	total=float(posA+negA+posB+negB)
	condEntropA=(posA+negA)/total*entropHelper(posA,negA)
	condEntropB=(posB+negB)/total*entropHelper(posB,negB)
	return totalEntrop-condEntropA-condEntropB>=0.1


def entropHelper(a,b):
	a=float(a)
	b=float(b)
	entrop=0
	if a==0 or b==0:
		return 0
	else:
		return a/(a+b)*math.log((a+b)/a,2)+b/(a+b)*math.log((a+b)/b,2)

def calculateError(name,string):
	with open(name,"rb") as csvfile:
		f=csv.reader(csvfile)
		correct=0
		wrong=0
		for row in f:
			for correctAtt in errorList:
				length=len(correctAtt)
				if correctAtt[:-1]==row[:length-1]:
					if row[-1]==correctAtt[-1]:
						correct+=1
					else:
						wrong+=1
		print "error("+string+"): "+str(float(wrong)/(correct+wrong))




main()

#print mutualInfoHelper(46,11,29,0,17,11)

#print entropHelper(5,6)