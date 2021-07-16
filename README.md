# AVManager
    龟速爬取 avmoo ,mgstage(蚊香社等dmm里没有的片商) 的影片元数据,在avmoo前端基础上做了影片收藏夹,预告片功能,女优的人脸识别 功能  


![image](https://github.com/Cinvin/AVManager/blob/master/src/img/movie.png "详情页")  

![image](https://github.com/Cinvin/AVManager/blob/master/src/img/face.png "识别页")  

数据库、人脸数据、训练模型:[百度云盘  密码: vo9k](https://pan.baidu.com/s/1EGjdhzQcTSJ27ISqJBLBuA)  
database.sql:影片元数据数据库  
data_X6800、data_y6800:爬取的全部人脸数据  
predict3094:前3094名女优训练出来的识别模型  

main.py:启动web(flask)  
crawler/avmoo.py 爬取avmoo  
crawler/MGStage.py 爬取MGStage  