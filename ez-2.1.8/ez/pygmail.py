
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email import encoders
import os
from email.header import Header
from mimetypes import guess_type


def Mail(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None):
    # only mixed or alternative valid; alternative has a problem when attachemnt has text file
    msg = MIMEMultipart('mixed')
    msg.set_charset('utf8')

    msg['From'] = "Memory Lab"
    if type(to) not in [str, unicode]: to = ', '.join(to)
    msg['To'] = to
    msg['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
    #This solve the problem with the encode on the subject.

    to = [to]
    if cc:
        # cc gets added to the text header as well as list of recipients
        if type(cc) in [str, unicode]:
            msg.add_header('Cc', cc)
            cc = [cc]
        else:
            msg.add_header('Cc', ', '.join(cc))
        to += cc
    if bcc:
        # bcc does not get added to the headers, but is a recipient
        if type(bcc) in [str, unicode]:
            bcc = [bcc]
        to += bcc
    if reply_to:
        msg.add_header('Reply-To', reply_to)

    if body.startswith('<'):
        # html email
        msg.attach(MIMEText(body.encode('utf-8'), 'html', 'UTF-8'))
    else:
        # text email
        msg.attach(MIMEText(body.encode('utf-8'), 'plain', 'UTF-8'))

    if attachment:
        if type(attachment) in [str, unicode]: attachment = [attachment]
        for att in attachment:
            mimetype, encoding = guess_type(att)
            if mimetype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                mimetype = 'application/octet-stream'
            maintype, subtype = mimetype.split('/', 1)
            if maintype == 'text':
                fp = open(att)
                # Note: we should handle calculating the charset
                part = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(att, 'rb')
                part = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(att, 'rb')
                part = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(att, 'rb')
                part = MIMEBase(maintype, subtype)
                part.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                     'attachment; filename="%s"' % os.path.basename(att))
            msg.attach(part)
 
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    print 'logging into email account...'
    mailServer.login(EMAIL, PASSWORD)
    print 'sending...'
    mailServer.sendmail(EMAIL, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    print 'finishing...'
    mailServer.close()
    print 'done!'