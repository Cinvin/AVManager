import os
from datetime import datetime
from sklearn import svm
import joblib


def learn_imagedata():
    data_X = []
    data_y = []
    basepath = os.path.abspath(".") + '/traindata/'
    if os.path.exists(basepath + 'data_X.bin'):
        data_X = joblib.load(basepath + 'data_X.bin')

    if os.path.exists(basepath + 'data_y.bin'):
        data_y = joblib.load(basepath + 'data_y.bin')

    clf = svm.SVC()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] start fit")
    clf.fit(data_X, data_y)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] end fit")
    joblib.dump(clf, basepath + 'predict.clf', compress=True)


if __name__ == '__main__':
    learn_imagedata()
