import os
import datetime
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

import yfinance as yf

from math import pi
import pandas as pd

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, LassoSelectTool, WheelZoomTool, PointDrawTool, ColumnDataSource
from bokeh.palettes import Category20c, Spectral6
from bokeh.transform import cumsum

from bokeh.resources import CDN
from bokeh.plotting import figure, show
from bokeh.sampledata.stocks import MSFT

from . import database
from .models import Post

def chart(request, market='indices', ric='DJI'):
    ric_display = ric
    if market not in ['indices', 'forex']:
        market = 'indices'
    if market == 'indices':
        ric = '^'+ric
    elif market == 'forex':
        ric += '=X'
    data = yf.download(  # or pdr.get_data_yahoo(...
        tickers = [ ric ],
        period = "1y",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )
    df = data.reset_index()
    df.columns= df.columns.str.lower()
    today = datetime.date.today()
    querydate = today.strftime("%Y-%m-%d")

    df["date"] = pd.to_datetime(df["date"])

    inc = df.close > df.open
    dec = df.open > df.close
    w = 12*60*60*1000 # half day in ms

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, width=1500, title = ric + " Candlestick")
    p.xaxis.major_label_orientation = pi/4
    p.grid.grid_line_alpha=0.3

    p.segment(df.date, df.high, df.date, df.low, color="black")
    p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")

    script, div = components(p)

    return render(request, 'finservice/bokeh-one.html', {'ric': ric_display, 'market': market, 'date': querydate, 'script': script, 'div': div, 'title': 'Bokeh Combo Graph'})


# Create your views here.
def index(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'finservice/index.html', context)

def equity(request, country_code='us'):
    country_equities = {
            'us': "NFE,KUASF,TTM,YSG,CHNVF,RLX,TUIFY,MPNGF,MPNGY,ZH,IQ,HUYA,DUOL,BILI,APP,OTLY,SEER,AZPN,LEVI,CRCT,IFS,FFIE,BABA,GDS,FCX",
            'au': "BHP,CBA,RIO,CSL,WBC,NAB,ANZ,MQG,WES,RMD,WOW,TLS,FMG,TCL,GMG,APT,ALL,AMC,WPL,COL,SYD,JHX,XRO,REA,NWS,SHL,NCM,FPH,WTC,QBE,S32,SUN,RHC,ASX,BXB,SCG,STO,COH"
            }

    # any unknown country code, route to US
    if country_code not in country_equities.keys():
        country_code = 'us'

    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = country_equities[country_code], 
        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period = "1d",
        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = "1d",
        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by = 'ticker',
        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust = True,
        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = True,
        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,
        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None
    )
    #marketdate = data.index.to_pydatetime()[0].strftime('%Y-%m-%d')
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    marketdate = yesterday.strftime("%Y-%m-%d")
    datadict = dict()
    for ric, field in data.columns:
        if data[ric].isnull().values.any():
            continue
        if ric not in datadict.keys():
            datadict[ric] = dict()
            datadict[ric]['Name'] = ric
        datadict[ric][field] = data[ric][field].values[0]
    datalist = list(datadict.values())

    return render(request, 'finservice/equity.html', {'country': country_code.upper(), 'market': 'Equity', 'data': datalist, 'date': marketdate})

def indices(request, ric='DJI'):
    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = [ '^' + ric ],
        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period = "2y",
        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = "1d",
        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by = 'ticker',
        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust = True,
        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = True,
        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,
        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None
    )
    today = datetime.date.today()
    querydate = today.strftime("%Y-%m-%d")

    data = json.loads(data.to_json(index=True))
    data_formatted = [{**{"Date": datetime.datetime.fromtimestamp(int(dt) / 1000).strftime('%Y-%m-%d %H:%M:%S')},
        **{fd: data.get(fd).get(dt) for fd in data.keys()}} for dt in data.get(list(data.keys())[0]).keys()]

    return render(request, 'finservice/indices.html', {'ric': ric, 'market': 'Indices', 'data': data_formatted, 'date': querydate})

def forex(request, ric='AUD'):
    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = [ ric + '=X' ],
        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period = "2y",
        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = "1d",
        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by = 'ticker',
        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust = True,
        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = True,
        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,
        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None
    )
    today = datetime.date.today()
    querydate = today.strftime("%Y-%m-%d")

    data = json.loads(data.to_json(index=True))
    data_formatted = [{**{"Date": datetime.datetime.fromtimestamp(int(dt) / 1000).strftime('%Y-%m-%d %H:%M:%S')},
        **{fd: data.get(fd).get(dt) for fd in data.keys()}} for dt in data.get(list(data.keys())[0]).keys()]

    return render(request, 'finservice/forex.html', {'ric': ric, 'market': 'Forex', 'data': data_formatted, 'date': querydate})


class PostListView(ListView):
    model = Post
    template_name = 'finservice/index.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'finservice/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


