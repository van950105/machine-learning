from scipy.sparse import lil_matrix
import scipy.spatial.distance
import time
import sklearn.preprocessing as pp
from math import sqrt

with open('HW4_data/train.csv') as trainFile:
	count = 0
	MOVIE_MAXID = 0
	USER_MAXID = 0
	ratedone = 0
	ratedthree = 0
	ratedfive = 0
	totalScore = 0
	for i in trainFile:	
		MOVIE_MAXID = max(int(i.split(',')[0]), MOVIE_MAXID)
		USER_MAXID = max(int(i.split(',')[1]), USER_MAXID)
		score = int(i.split(',')[2])
		if int(i.split(',')[0]) == 3:
			count += 1
			if score == 1:
				ratedone += 1
			if score == 3:
				ratedthree += 1
			if score == 5:
				ratedfive += 1
			totalScore += score

#print MOVIE_MAXID, USER_MAXID, count, ratedone, ratedthree, ratedfive
#print totalScore/float(count)


def getUserMatrix(userNo, itemNo):
	return lil_matrix((userNo+1, itemNo+1))

USER_MOVIE_MAT = getUserMatrix(USER_MAXID,MOVIE_MAXID)
with open('HW4_data/train.csv') as trainFile:
	for i in trainFile:
		movie_id = int(i.split(',')[0])
		user_id = int(i.split(',')[1])
		score = int(i.split(',')[2])
		USER_MOVIE_MAT[user_id,movie_id] = (score-3)
USER_MOVIE_MAT_CSR = USER_MOVIE_MAT.tocsr()


def cosine_similarities_user(mat):
    col_normed_mat = pp.normalize(mat.tocsr(), axis=0)
    return col_normed_mat * col_normed_mat.T

def cosine_similarities_movie(mat):
    col_normed_mat = pp.normalize(mat.tocsr(), axis=0)
    return col_normed_mat.T * col_normed_mat

cosSimMat_user = cosine_similarities_user(USER_MOVIE_MAT_CSR)
cosSimMat_movie = cosine_similarities_movie(USER_MOVIE_MAT_CSR)
cosSimMat_user = cosSimMat_user.tocsr()
cosSimMat_movie = cosSimMat_movie.tocsr()
#print spatial.distance.cosine(USER_MOVIE_MAT_CSR[1,],USER_MOVIE_MAT_CSR[333,])
#print USER_MOVIE_MAT_CSR[1]
#print cosSimMat_user[1]


def corpus_knn_user():
	'''
	dotProd = USER_MOVIE_MAT_CSR.dot(USER_MOVIE_MAT_CSR[4321].T)
	print cosSimMat_user[4321].toarray()[0].argsort()[::-1][1:6]
	print dotProd.toarray().flatten().argsort()[::-1][1:6]'''

	dotProd = USER_MOVIE_MAT_CSR.T.dot(USER_MOVIE_MAT_CSR.T[3].T)
	print cosSimMat_movie[3].toarray()[0].argsort()[::-1][1:6]
	print dotProd.toarray().flatten().argsort()[::-1][1:6]

#corpus_knn_user()

def user_user_dot(movie_id,user_id,k):
	user_rating = USER_MOVIE_MAT_CSR[user_id].T
	dotProd = USER_MOVIE_MAT_CSR.dot(user_rating).toarray().flatten().argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[i,movie_id] for i in dotProd]
	return sum(scores)/float(k)




def user_user_dot_script(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_user_user_dot_%d.txt' % (k),'w')
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = user_user_dot(movie_id,user_id,k)
			outputfile.write(str(score+3)+'\n')
		print time.time()-init_time

#user_user_dot_script(10)
#user_user_dot_script(100)
#user_user_dot_script(500)

def user_user_cos_mean(movie_id,user_id,k):
	cosSim = cosSimMat_user[user_id]
	cosSim = cosSim.toarray()[0]
	cosSim = cosSim.argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[i,movie_id] for i in cosSim]
	return sum(scores)/float(k)



def user_user_cos_script_mean(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_user_user_cos_mean_%d.txt' % (k),'w')
		count = 0
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = user_user_cos_mean(movie_id,user_id,k)
			outputfile.write(str(score+3)+'\n')
		print time.time()-init_time

#user_user_cos_script_mean(100)
#user_user_cos_script_mean(500)

def user_user_cos_weighted_mean(movie_id,user_id,k):
	cosSim = cosSimMat_user[user_id]
	cosSim = cosSim.toarray()[0]
	cosSimIndex = cosSim.argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[i,movie_id] for i in cosSimIndex]
	weightSum = 0
	score = 0
	for i in xrange(k):
		weightSum += cosSim[cosSimIndex[i]]
		score += scores[i]*cosSim[cosSimIndex[i]]
	if weightSum ==0: return 0
	return score/weightSum

def user_user_cos_script_weighted(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_user_user_cos_weighted_%d.txt' % (k),'w')
		count = 0
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = user_user_cos_weighted_mean(movie_id,user_id,k)
			outputfile.write(str(score+3)+'\n')
		print time.time()-init_time

#user_user_cos_script_weighted(10)
#user_user_cos_script_weighted(100)
#user_user_cos_script_weighted(500)


#################################

def movie_movie_dot(movie_id,user_id,k):
	movie_rating = USER_MOVIE_MAT_CSR.T[movie_id].T
	dotProd = USER_MOVIE_MAT_CSR.T.dot(movie_rating).toarray().flatten().argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[user_id,i] for i in dotProd]
	return sum(scores)/float(k)




def movie_movie_dot_script(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_movie_movie_dot_%d.txt' % (k),'w')
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = movie_movie_dot(movie_id,user_id,k)
			outputfile.write(str(score+3)+'\n')
		print time.time()-init_time

#movie_movie_dot_script(10)
#movie_movie_dot_script(100)
#movie_movie_dot_script(500)

def movie_movie_cos_mean(movie_id,user_id,k):
	cosSim = cosSimMat_movie[movie_id]
	cosSim = cosSim.toarray()[0]
	cosSim = cosSim.argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[user_id,i] for i in cosSim]
	return sum(scores)/float(k)



def movie_movie_cos_script_mean(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_movie_movie_cos_mean_%d.txt' % (k),'w')
		count = 0
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = movie_movie_cos_mean(movie_id,user_id,k)
			outputfile.write(str(score+3)+'\n')
		print time.time()-init_time


#movie_movie_cos_script_mean(10)
#movie_movie_cos_script_mean(100)
#movie_movie_cos_script_mean(500)

def movie_movie_cos_weighted_mean(movie_id,user_id,k):
	cosSim = cosSimMat_movie[movie_id]
	cosSim = cosSim.toarray()[0]
	cosSimIndex = cosSim.argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[user_id,i] for i in cosSimIndex]
	weightSum = 0
	score = 0
	for i in xrange(k):
		weightSum += cosSim[cosSimIndex[i]]
		score += scores[i]*cosSim[cosSimIndex[i]]
	if weightSum == 0: return 0
	return score/weightSum


def movie_movie_cos_script_weighted(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_movie_movie_cos_weighted_%d.txt' % (k),'w')
		count = 0
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = movie_movie_cos_weighted_mean(movie_id,user_id,k)
			outputfile.write(str(score+3)+'\n')
		print time.time()-init_time

#movie_movie_cos_script_weighted(10)
#movie_movie_cos_script_weighted(100)
#movie_movie_cos_script_weighted(500)



#####################################

COMPENS = []

def standardize_matrix():
	matrix_std = USER_MOVIE_MAT_CSR.tolil()
	for i in xrange(matrix_std.shape[0]):
		if (len(USER_MOVIE_MAT_CSR[i].nonzero()[1])) == 0:
			reduction == 0
		else:
			reduction = USER_MOVIE_MAT_CSR[i].sum()/len(USER_MOVIE_MAT_CSR[i].nonzero()[1])
		norm = USER_MOVIE_MAT_CSR[i].data**2
		norm = sqrt(norm.sum())
		COMPENS.append(reduction)
		for j in (USER_MOVIE_MAT_CSR[i].nonzero()[1]):
			matrix_std[i,j] -=reduction
			if norm!=0:
				matrix_std[i,j] /=norm
	return matrix_std.tocsr()

MATRIX_STD = standardize_matrix()

def pcc_dot(movie_id,user_id,k):
	matrix_std = MATRIX_STD
	user_rating = matrix_std[user_id].T
	dotProd = matrix_std.dot(user_rating).toarray().flatten().argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[i,movie_id] for i in dotProd]
	return sum(scores)/float(k)


def pcc_dot_script(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_pcc_dot_%d.txt' % (k),'w')
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = pcc_dot(movie_id,user_id,k)
			outputfile.write(str(score+COMPENS[user_id]+3)+'\n')
		print time.time()-init_time

#pcc_dot_script(10)
#pcc_dot_script(100)
#pcc_dot_script(500)

cosSimMat_pcc = cosine_similarities_user(MATRIX_STD)
cosSimMat_pcc = cosSimMat_pcc.tocsr()



def pcc_cos_mean(movie_id,user_id,k):
	cosSim = cosSimMat_pcc[user_id]
	cosSim = cosSim.toarray()[0]
	cosSim = cosSim.argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[i,movie_id] for i in cosSim]
	return sum(scores)/float(k)



def pcc_cos_script_mean(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_pcc_cos_mean%d.txt' % (k),'w')
		count = 0
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = pcc_cos_mean(movie_id,user_id,k)
			outputfile.write(str(score+3+COMPENS[user_id])+'\n')
		print time.time()-init_time
#pcc_cos_script_mean(10)
#pcc_cos_script_mean(100)
#pcc_cos_script_mean(500)


def pcc_cos_weighted_mean(movie_id,user_id,k):
	cosSim = cosSimMat_pcc[user_id]
	cosSim = cosSim.toarray()[0]
	cosSimIndex = cosSim.argsort()[::-1][1:k+1]
	scores = [USER_MOVIE_MAT_CSR[i,movie_id] for i in cosSimIndex]
	weightSum = 0
	score = 0
	for i in xrange(k):
		weightSum += cosSim[cosSimIndex[i]]
		score += scores[i]*cosSim[cosSimIndex[i]]
	if weightSum ==0: return 0
	return score/weightSum

def pcc_cos_script_weighted(k):
	init_time = time.time()
	with open('HW4_data/dev.csv') as devset:
		outputfile = open('result_pcc_cos_weighted_%d.txt' % (k),'w')
		count = 0
		for i in devset:
			movie_id = int(i.split(',')[0])
			user_id = int(i.split(',')[1])
			score = pcc_cos_weighted_mean(movie_id,user_id,k)
			outputfile.write(str(score+3)+'\n')
		print time.time()-init_time
#pcc_cos_script_weighted(10)
#pcc_cos_script_weighted(100)
#pcc_cos_script_weighted(500)
