"""Emails people via SMTP"""
import os
import smtplib
import tempfile
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

try:
    from docutils.core import publish_string
except ImportError:
    publish_string


def attach_txt(filename):
    with open(filename, 'r') as f:
        txt = f.read()
    msg = MIMEText(txt, _subtype='text')
    return msg


def attach_pdf(filename):
    with open(filename, 'r') as f:
        pdf = f.read()
    msg = MIMEApplication(pdf, _subtype="pdf")
    return msg


ATTACHERS = {
    '.txt': attach_txt,
    '.rst': attach_txt,
    '.pdf': attach_pdf,
    }


def make_message(rc, to, subject='', body='', attachments=()):
    """Creates an email following the approriate format. The body kwarg
    may be a string of restructured text.  Attachements is a list of filenames
    to attach.
    """
    msg = MIMEMultipart('alternative')
    plain = MIMEText(body, 'plain')
    msg.attach(plain)
    if publish_string is not None:
        html = publish_string(body, writer_name='html',
                              settings_overrides={'output_encoding': 'unicode'})
        html = MIMEText(html, 'html')
        msg.attach(html)
    if attachments:
        text = msg
        msg = MIMEMultipart('mixed')
        msg.attach(text)
        for attachment in attachments:
            _, ext = os.path.splitext(attachment)
            att = ATTACHERS[ext](attachment)
            att.add_header('content-disposition', 'attachment',
                           filename=os.path.basename(attachment))
            msg.attach(att)
    msg['Subject'] = subject
    msg['From'] = rc.email['from']
    msg['To'] = to
    return (to, msg.as_string())


def test_email(rc):
    """Sends a test email from regolith."""
    if rc.to is None:
        raise ValueError('--to must be given to send a test email.')
    with tempfile.NamedTemporaryFile(suffix='.rst') as f:
        f.write(b'This is *only* a test attachment.\n')
        f.flush()
        message = make_message(rc, rc.to, subject='Regolith test email',
                               body='This is *only* a test. Do not be alarmed.',
                               attachments=[f.name])
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
        smtp.set_debuglevel(conf['verbosity'])
        if conf['tls']:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(conf['user'], conf['password'])
        for to, message in emails:
            print('sending email to ' + to + '...')
            smtp.sendmail(conf['from'], to, message)
