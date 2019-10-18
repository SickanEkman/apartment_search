import requests
import smtplib
import ssl
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
import re

"""
Instructions and inspiration:
https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development
https://www.codementor.io/gergelykovcs/how-and-why-i-built-a-simple-web-scrapig-script-to-notify-us-about-our-favourite-food-fcrhuhn45
"""


def request_apartments(url):
    """
    Send request to url
    :return: request object with response
    """
    get_page = requests.get(url)
    get_page.raise_for_status()  # if error it will stop the program
    return get_page


def search_for_interesting_apartments(response):
    """
    Check for keywords
    :param response: request object with response
    :return: list of interesting apartment ids
    """
    apartment_as_list = response.content.decode().split('AnnonsId')
    hits = []
    for apartment in apartment_as_list:
        if '"Vanlig":true' in apartment:
            if '"Stadsdel":"Södermalm"' in apartment or '"Stadsdel":"Reimersholme"' in apartment or '"Stadsdel":"Långholmen"' in apartment:
                match = re.search(r':\d+(?=,"Stadsdel")', apartment)
                ad_id = match.group(0).strip(':')
                hits.append(ad_id + '\n')
    return hits


def compare_with_old_ads(current_ids):
    """
    Compare new ad IDs with stored IDs. If new IDs, write them to storage file
    :param current_ids: list with IDs from web scraping
    :return: Boolean, True if any new IDs, False if not
    """
    new_ids = []
    with open(os.path.join(sys.path[0], "ad_id.txt"), "r") as storage:
        old_ids = storage.readlines()
        for current_id in current_ids:
            if current_id not in old_ids:
                new_ids.append(current_id)
    if new_ids:
        with open(os.path.join(sys.path[0], "ad_id.txt"), "a") as write_file:
            write_file.writelines(new_id for new_id in new_ids)
        return True
    else:
        return False


def create_message(hits):
    """
    Create message body for email, one if interesting apartments and another if there aren't.
    :param hits: Boolean, True or False
    :return: Messages for email, one html and one plain text.
    """
    if hits:
        html_text = """\
    <html>
      <body>
        <p style="color:Green;">Hej!<br><br>
           <b>Lagenhet pa Sodermalm ligger ute nu!</b><br> 
           <a href="https://bostad.stockholm.se/Lista/?s=59.30796&n=59.32623&w=18.02393&e=18.07637&sort=annonserad-fran-desc&vanlig=1&omrade=%5B%7B%22value%22%3A%22Stadsdel-92%22%2C%22name%22%3A%22Stockholm%20-%20S%C3%B6dermalm%22%7D%2C%7B%22value%22%3A%22Stadsdel-71%22%2C%22name%22%3A%22Stockholm%20-%20Reimersholme%22%7D%2C%7B%22value%22%3A%22Stadsdel-58%22%2C%22name%22%3A%22Stockholm%20-%20L%C3%A5ngholmen%22%7D%5D">Link to Bostadsformedlingen</a> <br><br>
           <i>-- Email sent from my Python app</i>
        </p>
      </body>
    </html>
    """
        plain_text = "Lagenhet ligger ute!\n" \
                     "https://bostad.stockholm.se/Lista/?s=59.30796&n=59.32623&w=18.02393&e=18.07637&sort=annonserad-fran-desc&vanlig=1&omrade=%5B%7B%22value%22%3A%22Stadsdel-92%22%2C%22name%22%3A%22Stockholm%20-%20S%C3%B6dermalm%22%7D%2C%7B%22value%22%3A%22Stadsdel-71%22%2C%22name%22%3A%22Stockholm%20-%20Reimersholme%22%7D%2C%7B%22value%22%3A%22Stadsdel-58%22%2C%22name%22%3A%22Stockholm%20-%20L%C3%A5ngholmen%22%7D%5D\n\n" \
                     "-- Email sent from my Python app"
        return html_text, plain_text
    else:
        html_text = """\
    <html>
      <body>
        <p style="color:Red;">Hej!<br><br>
           Inga intressanta lagenheter idag. <br><br>
           <a href="https://bostad.stockholm.se/Lista/?s=59.30796&n=59.32623&w=18.02393&e=18.07637&sort=annonserad-fran-desc&vanlig=1&omrade=%5B%7B%22value%22%3A%22Stadsdel-92%22%2C%22name%22%3A%22Stockholm%20-%20S%C3%B6dermalm%22%7D%2C%7B%22value%22%3A%22Stadsdel-71%22%2C%22name%22%3A%22Stockholm%20-%20Reimersholme%22%7D%2C%7B%22value%22%3A%22Stadsdel-58%22%2C%22name%22%3A%22Stockholm%20-%20L%C3%A5ngholmen%22%7D%5D">Link to Bostadsformedlingen</a> <br><br>
           <i>-- Email sent from my Python app</i>
        </p>
      </body>
    </html>
    """
        plain_text = "Ingen intressant lagenhet idag.\n" \
                     "https://bostad.stockholm.se/Lista/?s=59.30796&n=59.32623&w=18.02393&e=18.07637&sort=annonserad-fran-desc&vanlig=1&omrade=%5B%7B%22value%22%3A%22Stadsdel-92%22%2C%22name%22%3A%22Stockholm%20-%20S%C3%B6dermalm%22%7D%2C%7B%22value%22%3A%22Stadsdel-71%22%2C%22name%22%3A%22Stockholm%20-%20Reimersholme%22%7D%2C%7B%22value%22%3A%22Stadsdel-58%22%2C%22name%22%3A%22Stockholm%20-%20L%C3%A5ngholmen%22%7D%5D\n" \
                     "-- Email sent from my Python app"
        return html_text, plain_text


def send_mail(sender_email, receiver_email, html_body, plain_body):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Daily Apartment Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(plain_body, "plain")
    part2 = MIMEText(html_body, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    port = 465  # For SSL
    password = secrets.gmail_app_password

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


if __name__ == "__main__":
    apartment_url = 'https://bostad.stockholm.se/Lista/AllaAnnonser'
    from_email = secrets.from_gmail
    to_email = secrets.to_gmail
    apartments = request_apartments(apartment_url)
    hit_list = search_for_interesting_apartments(apartments)
    hit = compare_with_old_ads(hit_list)
    html_message, plain_message = create_message(hit)
    send_mail(from_email, to_email, html_message, plain_message)
    
