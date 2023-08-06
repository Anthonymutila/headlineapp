import feedparser
import json
import urllib
from urllib.request import urlopen
import urllib.parse

from flask import Flask,request,url_for
from flask import render_template

app = Flask(__name__)

Defaults = {
    "publication": 'Lusakatimes',
    "city": 'Lusaka',
    "currency_from": 'USD',
    "currency_to": 'ZMW',
}

RSS_FEEDS = {

    # World News
    'Bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'Cnn': 'http://rss.cnn.com/rss/edition.rss',
    "Nytimes": 'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml',
    "Politico":'https://rss.politico.com/politics-news.xml',
    "Yahoo Sports": 'https://sports.yahoo.com/rss/',
    "NewYork post": 'https://nypost.com/feed/',
    "Climate Change":'https://news.un.org/feed/subscribe/en/news/topic/climate-change/feed/rss.xml',
    "America magazine":'https://www.americamagazine.org/feeds/complete/rss.xml'
    

    # Local News
    "Zambiareports": 'https://zambiareports.com/feed/',
    "Lusakatimes": 'https://www.lusakatimes.com/feed/',
    "Diggers.news": 'https://diggers.news/feed/',
    
     # Health Me
    "Mayoclinic": 'https://www.mayoclinic.org/rss/all-health-information-topics',
    "Mayoclinic": 'https://www.mayoclinic.org/rss/ask-a-specialist',
    "Mayoclinic": 'https://www.mayoclinic.org/rss/research-news',

   

    # Africa
    "UN.News":'https://news.un.org/feed/subscribe/en/news/region/africa/feed/rss.xml',
    
    # Entertainment
    "Etonline":'https://www.etonline.com/news/rss',
    "Etonline":'https://www.etonline.com/music/rss',
    
    # Technology
    "Wired": 'https://www.wired.com/feed',
    "Itworld": 'http://itworld.blog/feed',
    "HT Tech": 'https://tech.hindustantimes.com/rss',


}

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=0dd56c7a7c894cc583e858ea69bc6757"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=193c04858dbbbc76ecccf995c1213501"



@app.route("/")
def home():
            # get customized headlines(cnn, bbc etc), based on user input or default
            publication = request.args.get('publication')

            if not publication:
                Defaults['publication']
            articles = get_news(publication)

            city = request.args.get('city')
            if not city:
                city = Defaults['city']
            weather = get_weather(city)
            # get customized currency based on user input or default
            currency_from = request.args.get('currency_from')
            if not currency_from:
                currency_from = Defaults['currency_from']
            currency_to = request.args.get('currency_to')
            if not currency_to:
                currency_to = Defaults['currency_to']
            rate, currencies = get_currency(currency_from, currency_to)
            return render_template("home.html",articles=articles, title='News headlines', RSS_FEEDS=RSS_FEEDS,weather=weather,\
            currency_from=currency_from, currency_to=currency_to,rate=rate, currencies=sorted( currencies))  # return a sorted tuple of currencies as well hence the currencies sorted




def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = Defaults['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']



def get_weather(query):
     weather_url = "http://api.openweathermap.org/data/2.5/weather?q={" \
                   "}&units=metric&appid=193c04858dbbbc76ecccf995c1213501 "
     query = urllib.parse.quote(query)
     url = weather_url.format(query)
     data = urllib.request.urlopen(url).read()
     parsed = json.loads(data)
     weather = None
     if parsed.get('weather'):
         weather = {"description": parsed['weather'][0]['description'],
                    "temperature": parsed['main']['temp'],
                    "city": parsed['name'],"country": parsed['sys']['country']}
     return weather

def get_currency(frm, to):
      all_currency = urllib.request.urlopen(CURRENCY_URL).read()
      data = json.loads(all_currency).get('rates')
      frm_rate = data.get(frm.upper())
      to_rate = data.get(to.upper())

      send_rates = (to_rate / frm_rate, data.keys())
      return send_rates

@app.route('/about')
def about():
    return render_template("About.html",title = 'About')


if __name__ == "__main__":
    app.run(port=5000, debug=True)
