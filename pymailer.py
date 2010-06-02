#!/usr/bin/env python

import cStringIO
import csv
import logging
import os
import smtplib
import sys

from email import message, generator

from config import *

print FROM_NAME

# setup logging to specified log file
logging.basicConfig(filename=LOG_FILENAME, level=logging.ERROR)

class PyMailer():
    """
    A python bulk mailer commandline utility. Takes five arguments: the path to
    the html file to be parsed; the database of recipients (.csv); the subject
    of the email; email adsress the mail comes from; and the name the email is
    from. 
    """
    def __init__(self, html_path, csv_path, subject):
        self.html_path = html_path
        self.csv_path = csv_path
        self.subject = subject
        self.from_name = FROM_NAME
        self.from_email = FROM_EMAIL
        
    def _validate_email(self, email_address):
        """
        Validate the supplied email address.
        """
        if not email_address or len(email_address) > 7:
            return None
        if re.match('^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$', email_address):
            return None
        
    def _retry_handler(self, recipient_data):
        """
        Write failed recipient_data to csv file to be retried again later.
        """
        try:
            csv_file = open(CSV_RETRY_FILENAME, 'wb+')
        except IOError:
            raise IOError, "The retry csv file path is invalid."
        
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            recipient_data.get('name'),
            recipient_data.get('email')
        ])
        csv_file.close()
        
    def _html_parser(self, recipient_data):
        """
        Open, parse and substitute placeholders with recipient data.
        """
        try:
            html_file = open(self.html_path, 'rb')
        except IOError:
            raise IOError, "The html file path is invalid."
        
        html_content = html_file.read()
        if not html_content:
            raise Exception("The html file is empty.")
        
        # replace all placeolders associated to recipient_data keys    
        if recipient_data:
            for data in recipient_data:
                placeholder = "{{ %s }}" % data.key()
                html_content.replace(placeholder, data.value())
                
        return html_content
    
    def _form_email(self, recipient_data):
        """
        Form the html email, including mimetype and headers.
        """
        # form the recipient and sender headers
        recipient = "%s <%s>" % (recipient_data.get('name'), recipient_data.get('email'))
        sender = "%s <%s>" % (self.from_name, self.from_email)
        
        # instatiate the imetype and required headers
        output = cStringIO.StringIO()
        email_message = message.Message()
        
        email_message.add_header('From', sender)
        email_message.add_header('To', recipient)
        email_message.add_header('Subject', self.subject)
        email_message.add_header('MIME-Version', '1.0')
        email_message.add_header('Content-Type', 'text/html', [('charset', 'us-ascii')])
        email_message.set_payload(html_content)
        
        response = output.getvalue()
        output.close()
        
        return response
    
    def _map_data(self):
        pass
    
    def _parse_csv(self, csv_path=None):
        """
        Parse the entire csv file and return a list of dicts.
        """
        is_resend = csv_path is not None
        if not csv_path:
            csv_path = self.csv_path
        
        try:
            csv_file = open(csv_path, 'rwb')
        except IOError:
            raise IOError, "The csv file path is invalid."
        
        csv_reader = csv.reader(csv_file)
        recipient_data_list = []
        for i, row in enumerate(csv_reader):
            # test indexes exist and validate email address
            try:
                recipient_name = row[0]
                recipient_email = self._validate_email(row[1])
            except IndexError:
                recipient_name = ''
                recipient_email = None
            
            # log missing email addresses and line number
            if not recipient_email:
                logging.error("Recipient email missing in line %s" % i)
            else:
                recipient_data_list.append({
                    'name': name,
                    'email': email,
                })
        
        # clear the contents of the resend csv file
        if is_resend:
            csv_file.write('')
            
        csv_file.close()
        return recipient_data_list
    
    def send(self, is_resend=False, recipient_list=None):
        """
        Iterate over the recipient list and send the specified email. 
        """
        if not recipient_list:
            recipient_list = self._parse_csv()
            if is_resend:
                recipient_list = self._parse_csv(CSV_RETRY_FILENAME)
        
        for recipient_data in recipient_data_list:
            # instantiate the required vars to send email
            message = _form_email(recipient_data)
            recipient = "%s <%s>" % (recipient_data.get('name'), recipient_data.get('email'))
            sender = "%s <%s>" % (self.from_name, self.from_email)
            
            # send the actual email
            smtp_server = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
            try:
                smtp_server.sendmail(sender, recipient, message)
            except:
                logging.error("Recipient email address failed (%s)") % recipient
                self._retry_handler(recipient_data)
                
        # try and resend to reject recipients two more times
        for i in range(2):
            self.send(is_resend=True)
            
    def send_test(self):
        self.send(recipient_list=TEST_RECIPIENTS)
        
    def count_recipients():
        return len(self._parse_csv(csv_file))

def main(sys_args):
    try:
        action, html_path, csv_path, subject = sys_args
    except ValueError:
        print "Not enough argumants supplied. PyMailer requests 3 arguments: ./pymailer -s html_path csv_path subject"
        
    if os.path.splitext(html_path) != 'html':
        print "The html path doesn't seem to contain an html file."
        
    if os.path.splitext(csv_path) != 'csv':
        print "The csv path doesn't seem to contain an html file."
        
    pymailer = PyMailer(html_path, csv_path, subject)
    if action == '-s':
        if raw_input("You are about to send to %s recipients. Do you want to continue (yes/no)? ") == 'yes':
            pymailer.send()
        else:
            print "Aborted."
    elif action == '-t':
        if raw_input("You are about to send a test mail to all recipients as specified in config.py. Do you want to continue (yes/no)? ") == 'yes':
            pymailer.send_test()
        else:
            print "Aborted."
        pymailer.send_test()
    else:
        print "%s option is not support. Use either [-s] to send to all recipients or [-t] to send to test recipients" % option
    
if __name__ == '__main__':
    main(sys.argv[1:])
    