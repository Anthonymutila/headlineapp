import feedparser
import json
import urllib
from urllib.request import urlopen
import urllib.parse

from flask import Flask,request,url_for
from flask import render_template

app = Flask(__name__)

Defaults = {
    "publication": 'diggers.news',
    "city": 'Lusaka',
    "currency_from": 'USD',
    "currency_to": 'ZMW',
}

RSS_FEEDS = {

    # World News
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    "timesofindia": 'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms',
    "nytimes": 'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml',
    "europe & Africa": 'https://allafrica.com/tools/headlines/rdf/europeandafrica/headlines.rdf',


    # Local News
    "zambiareports": 'https://zambiareports.com/feed/',
    "lusakatimes": 'https://www.lusakatimes.com/feed/',
    "diggers.news": 'https://diggers.news/feed/',
    "zambianintelligencenews": 'http://www.zambianintelligencenews.com/feed/',
    "zambianeye": 'https://zambianeye.com/feed/',

    # Africa
    "middle east and africa": 'https://allafrica.com/tools/headlines/rdf/middleeastandafrica/headlines.rdf',
    "central africa": 'https://allafrica.com/tools/headlines/rdf/centralafrica/headlines.rdf',
    "north africa": 'https://allafrica.com/tools/headlines/rdf/northafrica/headlines.rdf',
    "east africa": 'https://allafrica.com/tools/headlines/rdf/eastafrica/headlines.rdf',
    "westafrica": 'https://allafrica.com/tools/headlines/rdf/westafrica/headlines.rdf',
    "southern africa": 'https://allafrica.com/tools/headlines/rdf/southernafrica/headlines.rdf',
    "corruption": 'https://allafrica.com/tools/headlines/rdf/corruption/headlines.rdf',
    "news24": 'http://feeds.news24.com/articles/news24/Africa/rss',

    # Entertainment
    "naijavibes": 'https://www.naijavibes.com/feed',
    "zambianmusicblog": 'https://zambianmusicblog.co/feed',

    # Technology
    "wired": 'https://www.wired.com/feed',
    "itworld": 'http://itworld.blog/feed',


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
