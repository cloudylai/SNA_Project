import sys
import numpy as np
import time
import itertools as itertl
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Manager
from sklearn import svm
from sklearn import tree
from sklearn import linear_model
from sklearn.ensemble import AdaBoostClassifier as abc
from sklearn.ensemble import RandomForestClassifier as rfc



def load_data(featL):
	trX = None
	trY = None
	teX = None
	teY = None
	temp_list = list()
	## train results ##
	with open('Gowalla/link_prediction/train_and_test/gowalla.train.txt', 'r') as f:
		for line in f:
			u1, u2, y = line.strip().split()
			y = int(y)
			temp_list.append(y)
	trY = np.array(temp_list)
	## test results ##
	temp_list[:] = []
	with open('Gowalla/link_prediction/train_and_test/gowalla.test.txt', 'r') as f:
		for line in f:
			u1, u2, y = line.strip().split()
			y = int(y)
			temp_list.append(y)
	teY = np.array(temp_list)
	for feat in featL:
		temp_list[:] = []
		feat_name = feat + '_tr_nol.txt'
		with open(feat_name, 'r') as f:
			for line in f:
				u1, u2, s = line.strip().split()
				s = float(s)
				temp_list.append([s])
		if trX == None:
			trX = np.array(temp_list)
		else:
			trX = np.concatenate((trX, np.array(temp_list)), axis=1)
		temp_list[:] = []
		feat_name = feat + '_te_nol.txt'
		with open(feat_name, 'r') as f:
			for line in f:
				u1, u2, s = line.strip().split()
				s = float(s)
				temp_list.append([s])
		if teX == None:
			teX = np.array(temp_list)
		else:
			teX = np.concatenate((teX, np.array(temp_list)), axis=1)
	return (trX, trY, teX, teY)


# label each data of test array with (user1, user2) 
def test_index(teX):
	idx_list = list()
	test_dict = dict()
	with open('Gowalla/link_prediction/train_and_test/gowalla.test.txt', 'r') as f:
		i = 0
		for line in f:
			u1, u2, s = line.strip().split()
			u1 = int(u1)
			u2 = int(u2)
			test_dict[(u1,u2)] = teX[i].tolist()
			idx_list.append((u1,u2))
			i += 1
	return test_dict, idx_list



# pair: ( (u1, u2), [features list] )
def task_predict(clf, test_pair, rlt_dict):
	u1 = test_pair[0][0]
	u2 = test_pair[0][1]
	feat = test_pair[1]
#	print('Debug: u1:', u1, 'u2:', u2)
#	print('Debug: feat:', feat)
	feat = np.array([feat])
	rlt = clf.predict(feat)
	rlt = rlt[0]
	rlt_dict[(u1,u2)] = rlt
	return rlt



def linear():
	trainX, trainY, testX, testY = load_data(['common_neigh', 'adamic_adar', 'mean_distance'])
	print('load data completely')
	clf = linear_model.SGDClassifier()
	clf.fit(trainX, trainY)
	print('linear SGD classifier model completely')
	testDict, testList = test_index(testX)
	test_size = len(testDict)
	predictY = clf.predict(testX)
	print('predict testing data completely')
	with open('linear_predict.txt', 'w') as f:
		for i in range(test_size):
			print(testList[i][0], testList[i][1], predictY[i], file=f)



def SVC():
	trainX, trainY, testX, testY = load_data(['common_neigh', 'check_common_time_spot', 'check_cosine_common_spot', 'dist_common_spot', 'shortest_path', 'katzB', 'adamic_adar', 'mean_distance'])
	print('load data completely')
	clf = svm.SVC()
	clf.fit(trainX, trainY)
	print('SVM classifier model completely')
	testDict, testList = test_index(testX)
	test_size = len(testDict)
	predictY = clf.predict(testX)
	with open('svm_predict.txt', 'w') as f:
		for i in range(test_size):
			print(testList[i][0], testList[i][1], predictY[i], file=f)
	scores = clf.score(testX, testY)
	print('predict testing data completely')
	print('Accuracy in sample =', scores)


def DecTree():
	trainX, trainY, testX, testY = load_data(['common_neigh', 'adamic_adar', 'dist_common_spot', 'mean_distance'])
	print('load data completely')
	clf = tree.DecisionTreeClassifier()
	clf.fit(trainX, trainY)
	print('decisiion tree completely')
	testDict, testList = test_index(testX)
	test_size = len(testDict)
	predictY = clf.predict(testX)
	with open('dectree_predict.txt', 'w') as f:
		for i in range(test_size):
			print(testList[i][0], testList[i][1], predictY[i], file=f)
	scores = clf.score(testX, testY)
	print('predict testing data completely')
	print('Accuracy in sample =', scores)


def AdaBoost():
	trainX, trainY, testX, testY = load_data(['common_neigh', 'check_common_time_spot','common_crt_time_spot', 'dist_common_spot', 'shortest_path', 'katzB' ,'adamic_adar', 'mean_distance'])
	print('load data completely')
	clf = abc(n_estimators=300)
	clf.fit(trainX, trainY)
	print('AdaBooting completely')
	print(clf.feature_importances_)
	testDict, testList = test_index(testX)
	test_size = len(testDict)
	predictY = clf.predict(testX)
	with open('adaboost_predict.txt', 'w') as f:
		for i in range(test_size):
			print(testList[i][0], testList[i][1], predictY[i], file=f)
	scores = clf.score(testX, testY)
	print('predict testing data completely')
	print('Accuracy in sample =', scores)


def RandomForest():
	trainX, trainY, testX, testY = load_data(['common_neigh', 'common_crt_time_spot', 'weight_common_spot', 'adamic_adar_entropy', 'check_common_spot', 'spot_product', 'shortest_path', 'katzB' ,'adamic_adar', 'mean_distance'])
	print('load data completely')
	clf = rfc(n_estimators=300, n_jobs=-1, max_depth = 20)
	clf.fit(trainX, trainY)
	print('Random Forest completely')
	print(clf.feature_importances_)
	testDict, testList = test_index(testX)
	test_size = len(testDict)
	predictY = clf.predict(testX)
	with open('randomforest_predict.txt', 'w') as f:
		for i in range(test_size):
			print(testList[i][0], testList[i][1], predictY[i], file=f)
	scores = clf.score(testX, testY)
	print('predict testing data completely')
	print('Accuracy in sample =', scores)

if __name__ == '__main__':
	RandomForest()
