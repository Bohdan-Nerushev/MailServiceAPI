import sys
import email.utils
from imap_tools import MailBox, MailMessageFlags
from email.message import EmailMessage

try:
    with MailBox('localhost').login('admin', 'admin') as mb:
        print('Logged in')
        if 'Sent' not in [f.name for f in mb.folder.list()]:
             mb.folder.create('Sent')
        msg = EmailMessage()
        msg['Subject'] = 'Test'
        msg['From'] = 'admin@localhost'
        msg['To'] = 'admin@localhost'
        msg['Date'] = email.utils.formatdate(localtime=True)
        msg['Message-ID'] = email.utils.make_msgid(domain='localhost')
        msg.set_content('Just testing Date and ID')
        
        mb.append(msg.as_bytes(), 'Sent', [MailMessageFlags.SEEN])
        print("Appended")
        mb.folder.set('Sent')
        print(len(list(mb.fetch())))
except Exception as e:
    print(e)
