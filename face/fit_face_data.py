import os
from datetime import datetime

import face_recognition
from sklearn import svm,neural_network
import joblib

from collections import Counter


def learn_imagedata_svm():
    data_X = []
    data_y = []
    basepath = os.path.abspath(".") + '/traindata/'
    if os.path.exists(basepath + 'data_X3094.bin'):
        data_X = joblib.load(basepath + 'data_X3094.bin')

    if os.path.exists(basepath + 'data_y3094.bin'):
        data_y = joblib.load(basepath + 'data_y3094.bin')

    clf = svm.SVC()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] start fit")
    clf.fit(data_X, data_y)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] end fit")
    joblib.dump(clf, basepath + 'predict3094.clf', compress=True)

def learn_imagedata_nn():
    data_X = []
    data_y = []
    basepath = os.path.abspath(".") + '/traindata/'
    if os.path.exists(basepath + 'data_X6800.bin'):
        data_X = joblib.load(basepath + 'data_X6800.bin')

    if os.path.exists(basepath + 'data_y6800.bin'):
        data_y = joblib.load(basepath + 'data_y6800.bin')

    clf = neural_network.MLPClassifier(hidden_layer_sizes=(128, ))
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] start fit")
    clf.fit(data_X, data_y)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] end fit")
    joblib.dump(clf, basepath + 'predict_nn.clf', compress=True)


def cutdata():
    data_X = []
    data_y = []
    basepath = os.path.abspath(".") + '/traindata/'
    if os.path.exists(basepath + 'data_X6800.bin'):
        data_X = joblib.load(basepath + 'data_X6800.bin')

    if os.path.exists(basepath + 'data_y6800.bin'):
        data_y = joblib.load(basepath + 'data_y6800.bin')

    counter = dict(Counter(data_y))
    csorted = sorted(counter.items(), key=lambda x: -x[1])
    count = 0
    for i in range(1, len(csorted)):
        count += 1
        if csorted[i][1] != csorted[i - 1][1]:
            print(f"{csorted[i - 1]} {count}")

    for i in range(0, len(csorted)):
        piccode = csorted[i][0]
        count = csorted[i][1]
        if count < 40:
            while data_y.count(piccode) > 0:
                index = data_y.index(piccode)
                del data_X[index]
                del data_y[index]

        # if count >129:
        #     while data_y.count(piccode) > 129:
        #         indexs = data_y.index(piccode)
        #         indexe = indexs
        #         while indexe<len(data_y)-1:
        #             if data_y[indexe+1]==piccode:
        #                 indexe+=1
        #             else:
        #                 break
        #         temp_X=data_X[indexs:indexe+1]
        #
        #         sums = [sum(face_recognition.face_distance(temp_X, temp_X[i])) for i in range(len(temp_X))]
        #         maxdata = max(sums)
        #         indexdelete = sums.index(maxdata)
        #         del data_X[indexs + indexdelete]
        #         del data_y[indexs + indexdelete]

    actcount = len(set(data_y))

    joblib.dump(data_X, basepath + 'data_X' + str(actcount) + '.bin', compress=True)
    joblib.dump(data_y, basepath + 'data_y' + str(actcount) + '.bin', compress=True)

if __name__ == '__main__':
    learn_imagedata_nn()
    # cutdata()

