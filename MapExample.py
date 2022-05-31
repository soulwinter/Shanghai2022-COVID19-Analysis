from pyecharts.charts import *
from pyecharts.components import Table
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import random
import datetime


from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "https://cdn.kesci.com/lib/pyecharts_assets/"

# 虚假数据
province = [
    '广东',
    '湖北',
    '湖南',
    '四川',
    '重庆',
    '黑龙江',
    '浙江',
    '山西',
    '河北',
    '安徽',
    '河南',
    '山东',
    '西藏']
data = [(i, random.randint(50, 150)) for i in province]

bmap = (
    BMap()
    .add_schema(baidu_ak="ivMnHuSCrEGDtGrEIXP5oOtbqg1S1KZ7", center=[120.13066322374, 30.240018034923])
    .add("", data)
)
bmap.render_notebook()