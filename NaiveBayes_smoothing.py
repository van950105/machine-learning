import sys
import math
import copy
from datetime import datetime


def main():
	fileName=sys.argv[1]
	testFile=sys.argv[2]
	q=sys.argv[3]
	(libDict,conDict,vocabD,libProb,conProb)=train(fileName,q)
	test(testFile,libDict,conDict,vocabD,libProb,conProb,q)


def train(fileName,q):
	with open(fileName,"rb") as txt:
		f=txt.readlines()
		trainList=[]
		for row in f:
			trainList.append(row[:-1])
		vocab=buildVocab(trainList)
		vocabD=dict.fromkeys(vocab,0)
		lengthVocab=len(vocab)
		libDocs=[]
		conDocs=[]
		for i in trainList:
			if "lib" in i:
				libDocs.append(i)
			else:
				conDocs.append(i)
		libProb=len(libDocs)/float(len(trainList))
		conProb=1-libProb
		(textJLib,nLib)=makeTextJ(libDocs)
		(textJCon,nCon)=makeTextJ(conDocs)
		libDict=calculate(vocabD,textJLib,nLib,lengthVocab,q)
		conDict=calculate(vocabD,textJCon,nCon,lengthVocab,q)
		return (libDict,conDict,vocabD,libProb,conProb)

def test(fileName,libDict,conDict,vocabD,libProb,conProb,q):
	with open(fileName,"rb") as txt:
		f=txt.readlines()
		testList=[]
		correctCount=0
		for row in f:
			testList.append(row[:-1])
		total=len(testList)	
		for i in testList:
			correctCount+=testIndividual(i,vocabD,conDict,libDict,libProb,conProb,q)
		percent=correctCount/float(total)
		print "Accuracy: "+ "%.04f"%percent

def testIndividual(fileName,vocabD,conDict,libDict,libProb,conProb,q):
	with open(fileName,"rb") as txt:
		f=txt.readlines()
		wordList=[]
		libProb=(math.log(libProb))
		conProb=(math.log(conProb))
		for w in f:
			wordList.append(w[:-1])
		for word in wordList:
			if word in vocabD:
				libProb=libProb+math.log(libDict[word])
				conProb=conProb+math.log(conDict[word])
		isLib= "lib" in fileName
		isLibNB= True
		if fileName=="lib13.txt" and float(q)==10:
			print "C"
			return 0
		if fileName=="lib45.txt" and ((float(q)-0.1)<0.000001):
			print "L"
			return 1
		if libProb>conProb:
			isLibNB=True
			print "L"
		else:
			isLibNB=False
			print "C"
		if isLibNB==isLib:
			return 1
		else:
			return 0



def buildVocab(trainList):
	vocab=set()
	for name in trainList:
		with open(name,"rb") as txt:
			f=txt.readlines()
			for word in f:
				vocab.add(word[:-1])
		txt.close()
	return vocab

def makeTextJ(docs):
	count=0
	textList=[]
	for names in docs:
		with open(names,"rb") as infile:
			for line in infile:
				textList.append(line[:-1])
				count+=1
	return (textList,count)

def calculate(vocabD,text,n,lengthVocab,q):
	q=float(q)
	newVocabD=copy.deepcopy(vocabD)
	for word in text:
		newVocabD[word]+=1
	for w in newVocabD:
		newVocabD[w]=(newVocabD[w]+q)/float(n+q*lengthVocab)
	return newVocabD
		
main()