import requests
import smtplib
import ssl
import secrets

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
    :return: list of interesting apartments
    """
    apartment_as_list = response.content.decode().split('AnnonsId')
    hits = []
    for apartment in apartment_as_list:
        if '"Stadsdel":"Södermalm"' in apartment and '"Vanlig":true' in apartment:
            hits.append(apartment)
    return hits


def create_message(hits):
    """
    Create message body for email.
    One if there are interesting appartments and another if there aren't.
    :param hits: list of interesting apartments (may be empty)
    :return: Message for email.
    """
    if hits:
        return """\
            Subject: Daily Bostadsformedlingen Alert

            Lagenhet i Sodermalm ligger ute nu!
            https://bostad.stockholm.se/Lista/?s=59.33731&n=59.33989&w=18.00999&e=18.02112&sort=annonserad-fran-desc&hiss=1&vanlig=1&omrade=%5B%7B%22value%22%3A%22Stadsdel-92%22%2C%22name%22%3A%22Stockholm%20-%20S%C3%B6dermalm%22%7D%5D
            -- This message is sent from my Python app"""
    else:
        return """\
            Subject: Daily Bostadsformedlingen Alert
    
            Ingen Sodermalmslagenhet ute :(    
            -- This message is sent from my Python app"""


def send_mail(sender_email, receiver_email, password, message, port):
    """
    Send email
    """
    context = ssl.create_default_context()  # Create a secure SSL context
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


if __name__ == "__main__":
    apartment_url = 'https://bostad.stockholm.se/Lista/AllaAnnonser'
    apartments = request_apartments(apartment_url)
    hit_list = search_for_interesting_apartments(apartments)
    email_message = create_message(hit_list)
    port_for_ssl = 465  # For SSL
    from_email = secrets.from_gmail
    to_email = secrets.to_gmail
    login_password = secrets.gmail_app_password
    send_mail(from_email, to_email, login_password, email_message, port_for_ssl)
