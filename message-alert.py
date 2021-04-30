import requests
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = 'https://ask.sirimangalo.org/feed/qa.rss'

RSS_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %z'

OUTPUT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

LAST_PROCESSED_FILE = 'last_processed_datetime'

EMAIL_LIST_FILE = 'email_list'

SENDER_EMAIL = os.getenv('EMAIL_ADDRESS')

EMAIL_PASSWORD = os.getenv('EMAIL_PASS')


def run():
    print('Started running at {}'.format(datetime.now()))

    response = get_rss()
    soup = BeautifulSoup(response.content, 'xml')
    all_items = get_items(soup)

    last_processed_date = get_last_processed_date()
    new_items = find_new(all_items, last_processed_date)

    send_emails(new_items)
    save_last_processed_date(new_items)


def get_rss():
    print('Getting RSS feed')
    return requests.get(URL)


def get_items(soup):
    print('Extracting all items from RSS')

    rss = soup.find('rss')
    channel = rss.find('channel')
    xml_items = channel.find_all('item')

    items = []

    for i in xml_items:
        title = i.find('title').text
        link = i.find('link').text
        desc = i.find('description').text
        guid = i.find('guid').text
        pub_date = i.find('pubDate').text

        items.append({
            'title': title,
            'link': link,
            'description': desc,
            'guid': guid,
            'pubDate': format_rss_date(pub_date)
        })

    return items


def format_rss_date(unformatted):
    return datetime.strptime(unformatted, RSS_DATE_FORMAT).strftime(OUTPUT_DATE_FORMAT)


def get_last_processed_date():
    print('Getting last processed date')

    with open(LAST_PROCESSED_FILE, 'r') as f:
        return parse_date(f.read())


def parse_date(str_date):
    return datetime.strptime(str_date.replace('\n', ''), OUTPUT_DATE_FORMAT)


def find_new(all_items, last_processed_date):
    print('Getting new items after {}'.format(last_processed_date))
    return [item for item in all_items if parse_date(item['pubDate']) > last_processed_date]


def send_emails(items):
    if len(items) == 0:
        print('No items found. Skipping sending email')
        return

    print('Sending emails')

    message = create_message(items)
    emails = get_emails()

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)

            for receiver in emails:
                smtp_message = create_smtp_message(SENDER_EMAIL, receiver, message)
                server.sendmail(SENDER_EMAIL, receiver, smtp_message.as_string())

    except Exception as e:
        print(e)


def create_smtp_message(sender, receiver, message):
    smtp_message = MIMEMultipart('alternative')
    smtp_message['Subject'] = 'New Ask Sirimangalo Messages'
    smtp_message['From'] = sender

    part1 = MIMEText('You need an email that can render html', 'plain')
    part2 = MIMEText(message, 'html')

    smtp_message.attach(part1)
    smtp_message.attach(part2)
    return smtp_message


def get_emails():
    with open('email_list', 'r') as f:
        return [email.replace('\n', '') for email in f.readlines()]


def create_message(items):
    header = '<html><body>'
    footer = '</body></html>'
    body = ''

    for item in items:
        body += '<h1>{}</h1>'.format(item['title'])
        body += '<p>{}</p>'.format(item['pubDate'])
        body += '<p>{}</p>'.format(item['description'])
        body += '<a href={}>Go to message</a><br /><br /><br />'.format(item['link'])
        body += '<hr>'

    return '{}{}{}'.format(header, body, footer)


def save_last_processed_date(items):
    if len(items) == 0:
        print('No items found. Skipping saving last processed date')
        return

    print('Saving last processed date')
    with open(LAST_PROCESSED_FILE, 'w') as f:
        f.write(items[0]['pubDate'])


if __name__ == '__main__':
    while True:
        run()
        print('==================================', flush=True)
        time.sleep(600)
