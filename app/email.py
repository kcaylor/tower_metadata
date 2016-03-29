from threading import Thread
from flask import current_app, render_template
from app import mail


def send_async_email(app, mailargs):
    with app.app_context():
        mail.send_email(**mailargs)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    mailargs = {
        'to': to,
        'from': app.config['PULSEPOD_MAIL_SENDER'],
        'subject': app.config['PULSEPOD_MAIL_SUBJECT_PREFIX'] + subject,
        'text': render_template(template + '.txt', **kwargs),
        'html': render_template(template + '.html', **kwargs)
    }
    thr = Thread(target=send_async_email, args=[app, mailargs])
    thr.start()
    return thr
