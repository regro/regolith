"""Emails people via SMTP"""
import smtplib

MESSAGE = """From: {from}\r\nTo: {to}\r\nSubject: {subject}\r\n\

{body}
"""

def make_message(rc, to, subject='', body=''):
    """Creates an email following the approriate format."""
    kw = {'from': rc.email['from'], 'to': to, 'subject': subject, 'body': body}
    message = MESSAGE.format(**kw)
    return message


def test_email(rc):
    """Sends a test email from regolith."""
    if rc.to is None:
        raise ValueError('--to must be given to send a test email.')
    message = make_message(rc, rc.to, subject='Regolith test email',
                           body='This is only a test. Do not be alarmed.')
    return [message]


EMAIL_CONSTRUCTORS = {
    'test': test_email,
    }

def emailer(rc):
    """Constructs and sends out emails"""
    constructor = EMAIL_CONSTRUCTORS[rc.email_target]
    emails = constructor(rc)
    conf = rc.email
    with smtplib.SMTP(conf['url'], port=conf['port']) as smtp:
        if conf['tls']:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(conf['from'], conf['password'])
        for to, message in emails:
            print('sending email to ' + to + '...')
            smtp.sendmail(conf['from'], to, message)
