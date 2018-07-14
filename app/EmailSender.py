from flask_mail import Message
from app import mail


class EmailSender(object):
    def __init__(self, mail_obj):
        self.obj_mail = mail_obj

    def send(self, to_who, subject, content):
        msg = Message(subject=subject, body=content, recipients=to_who)
        self.obj_mail.send(msg)


if __name__ == '__main__':
    sender = EmailSender(mail)
    sender.send('aaa@163.com', 'notify', 'content')
