import requests
import os
from twilio.rest import Client
import html

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_API = os.environ.get("SP_API")
NEWS_API = os.environ.get("NEWS_API")

parameters_stock = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API
}

parameters_news = {
    "q": COMPANY_NAME,
    "apiKey": NEWS_API
}

# Twilio credentials
account_sid = "AC374af1563c9affd93a631d3dfedbba31"
auth_token = os.environ.get("AUTH_TOKEN")

response = requests.get(url=STOCK_ENDPOINT, params=parameters_stock)
response.raise_for_status()
stock_data = response.json()["Time Series (Daily)"]
# print(stock_data)

# We need to create a list to hold price because yesterday could be different for everyday
data_list = [value["4. close"] for (key, value) in stock_data.items()]
# print(data_list)

# When stock price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
yesterday_price = float(data_list[0])
day_before_yes_price = float(data_list[1])
price_change = yesterday_price - day_before_yes_price
# print(price_change)
price_change_pct = round((yesterday_price - day_before_yes_price) / day_before_yes_price * 100)
# print(price_change_pct)
up_down = None
if price_change > 0:
    up_down = "📈"
if price_change < 0:
    up_down = "📉"

if abs(price_change_pct) > 5:
    response = requests.get(url=NEWS_ENDPOINT, params=parameters_news)
    response.raise_for_status()
    news_data = response.json()["articles"][:3]
    news_data_unescaped = html.unescape(news_data)
    # print(news_data)
    # print(news_data_unescaped)

    # Get news
    article_list = [f"{STOCK_NAME}: {up_down}{abs(price_change_pct)}%\nHeadline: {article['title']}. "
                    f"\nBrief: {article['description']}" for article in news_data_unescaped]
    # print(article_list)
    #Use twilio.com/docs/sms/quickstart/python
    #to send a separate message with each article's title and description to your phone number.
    client = Client(account_sid, auth_token)
    for article in article_list:
        message = client.messages.create(
            body=article,
            from_='+13464833780',
            to="+61405996852"
        )
        print(message.status)
