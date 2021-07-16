import numpy as np
from model import *
from pyecharts.charts import Line, Pie, Bar
from pyecharts import options as opts
from sqlalchemy import func, exists, and_, or_

def geteecharts():
    echarts = list()
    echarts.append(get_av_year_charts())
    echarts.append(get_cup_pie_charts())
    echarts.append(get_actress_height_charts())
    echarts.append(get_actress_num_rank())
    return echarts


def get_av_year_charts():
    movie_count=AV.query.count()
    years = func.date_format(AV.rdate, "%Y").label('year')
    result = AV.query.with_entities(years, func.count('*').label('year_count')) \
        .filter(AV.rdate.isnot(None)) \
        .order_by(years) \
        .group_by(years).all()
    a1, a2 = zip(*result)
    line = (
        Line(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', )
        )
            .add_xaxis(list(a1))
            .add_yaxis("数量", list(a2),
                       label_opts=opts.LabelOpts(is_show=False),
                       is_smooth=True
                       )
            .set_global_opts(title_opts=opts.TitleOpts(title=f"AV数量年份统计(总计{str(movie_count)})"))
    )
    return line.render_embed()


def get_actress_height_charts():
    result = Actress.query.with_entities(Actress.height, func.count('*').label('height_count')) \
        .filter(Actress.height.isnot(None)) \
        .order_by(Actress.height) \
        .group_by(Actress.height).all()
    a1, a2 = zip(*result)
    a1, a2 = list(a1), list(a2)
    heightlist = ['<140', '140-144', '145-149', '150-154', '155-159', '160-164', '165-169', '170-174', '175-179',
                  '>=180']
    countlist = [0] * 10
    for i in range(0, len(a1)):
        index = 0
        if 140 <= a1[i] <= 144:
            index = 1
        elif 145 <= a1[i] <= 149:
            index = 2
        elif 150 <= a1[i] <= 154:
            index = 3
        elif 155 <= a1[i] <= 159:
            index = 4
        elif 160 <= a1[i] <= 164:
            index = 5
        elif 165 <= a1[i] <= 169:
            index = 6
        elif 170 <= a1[i] <= 174:
            index = 7
        elif 175 <= a1[i] <= 179:
            index = 8
        elif a1[i] >= 180:
            index = 9
        countlist[index] = a2[i]
    bar = (
        Bar(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', ))
            .add_xaxis(heightlist)
            .add_yaxis("数量", countlist)
            .set_global_opts(title_opts=opts.TitleOpts(title="身高分布"))
        # 或者直接使用字典参数
        # .set_global_opts(title_opts={"text": "主标题", "subtext": "副标题"})
    )
    return bar.render_embed()


def get_cup_pie_charts():
    result = Actress.query.with_entities(Actress.cup, func.count('*').label('cup_count')) \
        .filter(Actress.cup.isnot(None)) \
        .order_by(Actress.cup) \
        .group_by(Actress.cup).all()
    pie = (
        Pie(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', )
        )
            .add("", data_pair=result)
            .set_global_opts(title_opts=opts.TitleOpts(title="CUP分布"))
    )
    return pie.render_embed()


def get_actress_num_rank():
    counts = func.count(1)
    result = Actress.query.with_entities(Actress.actname, counts) \
        .join(av_actress) \
        .order_by(counts.desc()) \
        .group_by(Actress.id) \
        .all()
    # .join(av) \
    # .filter(datetime.date(datetime.datetime.now().year-5,1,1) <= av.rdate , av.rdate < datetime.date(datetime.datetime.now().year-4,1,1)) \

    countlist = [x[1] for x in result]
    avg = round(np.mean(countlist), 2)
    median = np.median(countlist)

    actresslist = []
    countlist = []
    for i in range(15):
        actresslist.append(result[i][0])
        countlist.append(result[i][1])
    actresslist.append('平均数')
    countlist.append(avg)
    actresslist.append('中位数')
    countlist.append(median)
    bar = (
        Bar(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', ))
            .add_xaxis(actresslist[::-1])
            .add_yaxis("数量", countlist[::-1])
            .set_global_opts(title_opts=opts.TitleOpts(title="数量TOP"))
        # 或者直接使用字典参数
        # .set_global_opts(title_opts={"text": "主标题", "subtext": "副标题"})
    )
    return bar.render_embed()