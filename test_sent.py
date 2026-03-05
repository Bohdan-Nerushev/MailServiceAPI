import os
import sys
from imap_tools import MailBox, MailMessageFlags
from email.message import EmailMessage

try:
    with MailBox('localhost').login('admin', 'admin') as mailbox:
        folders = [f.name for f in mailbox.folder.list()]
        print("Initial Folders:", folders)
        
        if 'Sent' not in folders:
            print("Creating 'Sent'...")
            mailbox.folder.create('Sent')
            print("After Create:", [f.name for f in mailbox.folder.list()])
        
        msg = EmailMessage()
        msg['Subject'] = 'Test persistence'
        msg['From'] = 'admin@localhost'
        msg['To'] = 'admin@localhost'
        msg.set_content('Just testing')
        
        mailbox.append(msg.as_bytes(), 'Sent', [MailMessageFlags.SEEN])
        print("Appended message")
        
        mailbox.folder.set('Sent')
        print("Messages in Sent:", len(list(mailbox.fetch())))
except Exception as e:
    print(e)
