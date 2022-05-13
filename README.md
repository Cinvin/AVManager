# AVManager
  仅为了学习python爬虫和Flask框架知识,JAV元数据爬虫,用avmoo的前端,在此基础上做了影片收藏夹,预告片功能,女优的人脸识别 功能  

### 获取站点
- ~~FANZA(https://www.dmm.co.jp/)~~ (弃用 因为只有日本IP才能访问 而且用DMM API 同样可获取到)
- [DMM API](https://affiliate.dmm.com/api/v3/itemlist.html) (DMM旗下的FANZA是Javbus,JAVLibrary等网站内容的主要来源)
- [MGStage](http://mgstage.com/) (制造商prestige的电商网站)
- [AVE](https://www.aventertainments.com/)
- [FC2-PPV(部分)](https://adult.contents.fc2.com) 
- [1pondo(一本道)](https://www.1pondo.tv) 
- [10musume](https://www.10musume.com)
- [caribbeancom(カリビアンコム)](https://www.caribbeancom.com)
- [heyzo](https://www.heyzo.com)
- [pacopacomama(パコパコママ)](https://www.pacopacomama.com)
- [Tokyo-Hot](https://www.tokyo-hot.com/product/)

![image](https://github.com/Cinvin/AVManager/blob/master/src/img/movie.png "详情页")  

![image](https://github.com/Cinvin/AVManager/blob/master/src/img/face.png "识别页")  
人脸数据、训练模型:[百度云盘  密码: vo9k](https://pan.baidu.com/s/1EGjdhzQcTSJ27ISqJBLBuA)  
data_X6800、data_y6800:爬取的全部人脸数据  
predict3094:前3094名女优训练出来的识别模型  

[MySQL数据库(60w+条)](https://github.com/Cinvin/AVManager/tree/master/database)

main.py:启动web(flask)  
crawler/daila_craler.py:日常爬取 加入每日定时任务来保持获取最新
