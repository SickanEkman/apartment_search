Web crawler scanning Stockholm Stads bostadsformedling for apartment with certain criteria. Sends me a daily email with good or bad news.

Setup after cloning project:
* Create empty file named ad_id.txt in same directory as main.py (will eventually fill up with ad id's)
* Create secrets.py in same directory as main.py. File should contain three variables:
>* from_gmail = from.email.adress@mail.com
>* to_gmail = to.email.adress@mail.com
>* gmail_app_password = google.it.if.you.dont.know.what.it.is
* Set up cronjob once a day, example: 0 12 * * * python3 full/path/to/main.py
