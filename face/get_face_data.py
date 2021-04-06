from io import BytesIO
import joblib
import sqlhelper
import os
from crawler import CrawlerHelper
import numpy as np
import PIL.Image
import face_recognition
import random
import threading
from datetime import datetime
from model import *
from sqlalchemy import func
from concurrent.futures import ThreadPoolExecutor, as_completed


class GetActressImgData:
    def __init__(self):
        self.data_X = []
        self.data_y = []
        self.actcodelist = []
        self.basepath = os.path.abspath("./traindata") + '/'
        self.urlpre = ['https://pics.dmm.co.jp', 'https://jp.netcdn.space', 'https://pics.avdmm.top']
        self.datalock = threading.Lock()
        self.actcount = 0
        if os.path.exists(self.basepath + 'data_X.bin'):
            self.data_X = joblib.load(self.basepath + 'data_X.bin')
        if os.path.exists(self.basepath + 'data_y.bin'):
            self.data_y = joblib.load(self.basepath + 'data_y.bin')

        set_y = set(self.data_y)
        result = Actress.query.with_entities(Actress.piccode) \
            .join(av_actress) \
            .filter(Actress.piccode.isnot(None), Actress.piccode.notin_(set_y)) \
            .order_by(func.count('*').desc()) \
            .group_by(Actress.piccode) \
            .having(func.count('*') >= 10).all()

        self.actcodelist = [x.piccode for x in result]

        self.counter = 0

    def savefile(self):
        print("savefile")
        joblib.dump(self.data_X, self.basepath + 'data_X.bin', compress=True)
        joblib.dump(self.data_y, self.basepath + 'data_y.bin', compress=True)

    def start(self):
        print(f"len(self.actidlist) {len(self.actcodelist)}")
        print(f"len(self.data_X) {len(self.data_X)}")
        print(f"len(self.data_y) {len(self.data_y)}")
        executor = ThreadPoolExecutor(max_workers=64)
        obj_list = []

        for actcode in self.actcodelist:
            obj = executor.submit(self._get_itemactressdata, actcode)
            obj_list.append(obj)

        i = 0
        for future in as_completed(obj_list):
            i += 1
            future.result()
            print(f"finish: {i}/{len(obj_list)}")

        self.savefile()

    def _get_itemactressdata(self, actcode):
        picurls = []
        picurls.append(f"/mono/actjpgs/{actcode}.jpg")
        movielist = sqlhelper.fetchall(
            "SELECT a.`code`,a.piccode,a.piccount FROM t_av a INNER JOIN t_av_actress b on a.id = b.av_id INNER JOIN t_actress c on c.id = b.actress_id WHERE c.piccode=%s and EXISTS (SELECT 1 FROM t_av_actress c where a.id=c.av_id GROUP BY c.av_id HAVING count(*)=1) ORDER BY a.rdate desc",
            actcode)

        for movie in movielist:
            picurls.append(f"/digital/video/{movie['piccode']}/{movie['piccode']}pl.jpg")
            for i in range(1, movie['piccount'] + 1):
                picurls.append(f"/digital/video/{movie['piccode']}/{movie['piccode']}jp-{str(i)}.jpg")
        myfaces = []

        for url in picurls:
            img = self.getimg(url)
            if img is not None:
                face_ec = face_recognition.face_encodings(img, num_jitters=10, model="large")
                if len(face_ec) > 0:
                    myfaces.extend(face_ec)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  {actcode} found {len(myfaces)}")
                    if len(myfaces) > 200:
                        break

        self.add_data(myfaces, actcode)

    def add_data(self, data, actcode, tolerance=0.6):
        if len(data) == 0:
            return
        while True:
            sums = [sum(face_recognition.face_distance(data, data[i])) for i in range(len(data))]
            maxdata = max(sums)
            if maxdata > tolerance * (len(data) - 1):
                index = sums.index(maxdata)
                del data[index]
            else:
                break
        if len(data) < 10:
            return
        data_y = [actcode for i in range(len(data))]
        self.datalock.acquire()
        self.data_X.extend(data)
        self.data_y.extend(data_y)
        self.actcount += 1
        if self.actcount % 8 == 0:
            self.savefile()
        self.datalock.release()
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {actcode} add {len(data)}, datacount:{len(self.data_y)}")

    def getimg(self, url):
        urlpre = random.choice(self.urlpre)
        img = CrawlerHelper.get_requests(urlpre + url, is_stream=True)
        if img is None:
            urlpre = random.choice(self.urlpre)
            img = CrawlerHelper.get_requests(urlpre + url, is_stream=True)
            if img is None:
                return None
        if "printing" in img.url:
            return None
        try:
            im = PIL.Image.open(BytesIO(img.content))
        except:
            return None
        im = im.convert('RGB')
        return np.array(im)


def main():
    g = GetActressImgData()
    g.start()


if __name__ == '__main__':
    main()
