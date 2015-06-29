__author__ = "jerryzhujian9@gmail.com"

__doc__ = """web related functions.
requires pdfkit, feedparser

json2dict(url)
rss2list(url)
ValidEmail(email, check=False, verify=False), validemail: is email format valid
export(input,output,options,**kwargs): # Convert url, file (html, txt), string to a single pdf
"""

def json2dict(url):
    """read in a json into a dictionary"""
    import json, re, urllib, urllib2
    req = urllib2.Request(url)
    handler = urllib2.urlopen(req)
    content = handler.read()
    data = json.loads(content)
    return data


def rss2list(url):
    import feedparser
    feed = feedparser.parse(url)
    posts = feed.entries
    return posts


def ValidEmail(email, check=False, verify=False):
    """Indicate whether the given string is a valid email address
    according to the 'addr-spec' portion of RFC 2822 (see section
    3.4.1).  Parts of the spec that are marked obsolete are *not*
    included in this test, and certain arcane constructions that
    depend on circular definitions in the spec may not pass, but in
    general this should correctly identify any email address likely
    to be in use as of 2011.

    For check the domain mx and verify email exits you must have the pyDNS package installed:
    pip install pyDNS

    Check if the host has SMTP Server: ('example@example.com',check=True)
    Check if the host has SMTP Server and the email really exists: ('example@example.com',verify=True)  <--not working sometimes?
    """
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # modified from https://github.com/syrusakbary/validate_email
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # RFC 2822 - style email validation for Python
    # (c) 2012 Syrus Akbary <me@syrusakbary.com>
    # Extended from (c) 2011 Noel Bush <noel@aitools.org>
    # for support of mx and user check (i.e., whether the mail server actually exists, user actually exists)
    # This code is made available to you under the GNU LGPL v3.
    #
    # returns True or False to indicate whether a given address
    # is valid according to the 'addr-spec' part of the specification
    # given in RFC 2822.  Ideally, we would like to find this
    # in some other library, already thoroughly tested and well-
    # maintained.  The standard Python library email.utils
    # contains a parse_addr() function, but it is not sufficient
    # to detect many malformed addresses.
    #
    # This implementation aims to be faithful to the RFC, with the
    # exception of a circular definition (see comments below), and
    # with the omission of the pattern components marked as "obsolete".

    check_mx = check
    import re
    import smtplib
    import socket

    try:
        import DNS
        ServerError = DNS.ServerError
    except:
        DNS = None
        class ServerError(Exception): pass
    # All we are really doing is comparing the input string to one
    # gigantic regular expression.  But building that regexp, and
    # ensuring its correctness, is made much easier by assembling it
    # from the "tokens" defined by the RFC.  Each of these tokens is
    # tested in the accompanying unit test file.
    #
    # The section of RFC 2822 from which each pattern component is
    # derived is given in an accompanying comment.
    #
    # (To make things simple, every string below is given as 'raw',
    # even when it's not strictly necessary.  This way we don't forget
    # when it is necessary.)
    #
    WSP = r'[ \t]'                                       # see 2.2.2. Structured Header Field Bodies
    CRLF = r'(?:\r\n)'                                   # see 2.2.3. Long Header Fields
    NO_WS_CTL = r'\x01-\x08\x0b\x0c\x0f-\x1f\x7f'        # see 3.2.1. Primitive Tokens
    QUOTED_PAIR = r'(?:\\.)'                             # see 3.2.2. Quoted characters
    FWS = r'(?:(?:' + WSP + r'*' + CRLF + r')?' + \
                WSP + r'+)'                                    # see 3.2.3. Folding white space and comments
    CTEXT = r'[' + NO_WS_CTL + \
                    r'\x21-\x27\x2a-\x5b\x5d-\x7e]'              # see 3.2.3
    CCONTENT = r'(?:' + CTEXT + r'|' + \
                         QUOTED_PAIR + r')'                        # see 3.2.3 (NB: The RFC includes COMMENT here
                                                                                                             # as well, but that would be circular.)
    COMMENT = r'\((?:' + FWS + r'?' + CCONTENT + \
                        r')*' + FWS + r'?\)'                       # see 3.2.3
    CFWS = r'(?:' + FWS + r'?' + COMMENT + ')*(?:' + \
                 FWS + '?' + COMMENT + '|' + FWS + ')'         # see 3.2.3
    ATEXT = r'[\w!#$%&\'\*\+\-/=\?\^`\{\|\}~]'           # see 3.2.4. Atom
    ATOM = CFWS + r'?' + ATEXT + r'+' + CFWS + r'?'      # see 3.2.4
    DOT_ATOM_TEXT = ATEXT + r'+(?:\.' + ATEXT + r'+)*'   # see 3.2.4
    DOT_ATOM = CFWS + r'?' + DOT_ATOM_TEXT + CFWS + r'?' # see 3.2.4
    QTEXT = r'[' + NO_WS_CTL + \
                    r'\x21\x23-\x5b\x5d-\x7e]'                   # see 3.2.5. Quoted strings
    QCONTENT = r'(?:' + QTEXT + r'|' + \
                         QUOTED_PAIR + r')'                        # see 3.2.5
    QUOTED_STRING = CFWS + r'?' + r'"(?:' + FWS + \
                                    r'?' + QCONTENT + r')*' + FWS + \
                                    r'?' + r'"' + CFWS + r'?'
    LOCAL_PART = r'(?:' + DOT_ATOM + r'|' + \
                             QUOTED_STRING + r')'                    # see 3.4.1. Addr-spec specification
    DTEXT = r'[' + NO_WS_CTL + r'\x21-\x5a\x5e-\x7e]'    # see 3.4.1
    DCONTENT = r'(?:' + DTEXT + r'|' + \
                         QUOTED_PAIR + r')'                        # see 3.4.1
    DOMAIN_LITERAL = CFWS + r'?' + r'\[' + \
                                     r'(?:' + FWS + r'?' + DCONTENT + \
                                     r')*' + FWS + r'?\]' + CFWS + r'?'  # see 3.4.1
    DOMAIN = r'(?:' + DOT_ATOM + r'|' + \
                     DOMAIN_LITERAL + r')'                       # see 3.4.1
    ADDR_SPEC = LOCAL_PART + r'@' + DOMAIN               # see 3.4.1

    # A valid address will match exactly the 3.4.1 addr-spec.
    VALID_ADDRESS_REGEXP = '^' + ADDR_SPEC + '$'

    try:
        assert re.match(VALID_ADDRESS_REGEXP, email) is not None
        check_mx |= verify
        if check_mx:
            if not DNS: raise Exception('For check the mx records or check if the email exists you must have installed pyDNS python package')
            DNS.DiscoverNameServers()
            hostname = email[email.find('@')+1:]
            mx_hosts = DNS.mxlookup(hostname)
            for mx in mx_hosts:
                try:
                    smtp = smtplib.SMTP()
                    smtp.connect(mx[1])
                    if not verify: return True
                    status, _ = smtp.helo()
                    if status != 250: continue
                    smtp.mail('')
                    status, _ = smtp.rcpt(email)
                    if status != 250: return False
                    break
                except smtplib.SMTPServerDisconnected: #Server not permits verify user
                    break
                except smtplib.SMTPConnectError:
                    continue
    except (AssertionError, ServerError):
        return False
    return True
validemail = ValidEmail


def export(input,output=None,options=None,**kwargs):
    """Convert url, html file, html string to a single pdf

    (input,output,options,**kwargs)
    input:  could be a list of urls, files, strings
            url should start with 'http' or 'https'
            string could be htlm codes
            html file
    output: pdf file path, if not provided, use default file name
    options: default
            options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'image-dpi': 1200,
            'image-quality': 100}
            If option without value, use None, False or '' for dict value
            By default, PDFKit will show all wkhtmltopdf output. 
            If you dont want it, you need to pass quiet option: 'quiet': ''
    css = css
    see more options at: https://pypi.python.org/pypi/pdfkit
                         http://wkhtmltopdf.org/usage/wkhtmltopdf.txt
                         wkhtmltopdf -H
    
    wrapper of pdfkit which in turn based on wkhtmltopdf, pyqt
    """
    import pdfkit
    if not output: output = 'Out_' + Moment().datetime + '.pdf'
    if not options: options = {'page-size': 'Letter',
                               'margin-top': '0.75in',
                               'margin-right': '0.75in',
                               'margin-bottom': '0.75in',
                               'margin-left': '0.75in',
                               'encoding': "UTF-8",
                               'no-outline': None,
                               'image-dpi': 1200,
                               'image-quality': 100}
    if type(input) in [list]: 
        temp = input[0]
    else:
        temp = input
    if temp.startswith('http'):
        pdfkit.from_url(input,output,options=options,**kwargs)
    elif exists(temp):
        pdfkit.from_file(input,output,options=options,**kwargs)
    else:
        pdfkit.from_string(input,output,options=options,**kwargs)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# debugging
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == "__main__":
    pass