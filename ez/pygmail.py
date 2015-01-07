import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
from email.header import Header


def Mail(G_EMAIL, G_PASSWORD, to, subject, body, attach=None):
        msg = MIMEMultipart('alternative')
        msg.set_charset('utf8')

        msg['From'] = "Memory Lab"
        msg['To'] = to
        msg['Subject'] =Header(subject.encode('utf-8'), 'UTF-8').encode()
        #This solve the problem with the encode on the subject.

        #And this on the body
        msg.attach(MIMEText(body.encode('utf-8'), 'html', 'UTF-8'))
        if attach:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(attach, 'rb').read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                         'attachment; filename="%s"' % os.path.basename(attach))
                msg.attach(part)
     
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(G_EMAIL, G_PASSWORD)
        mailServer.sendmail(G_EMAIL, to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()


mail = Mail