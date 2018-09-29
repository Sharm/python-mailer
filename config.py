"""
Global config file. Change variable below as needed but ensure that the log and
retry files have the correct permissions.
"""

from datetime import datetime

# file settings
LOG_FILENAME        = 'log/pymailer-%s.log' % str(datetime.now()).replace(' ', '-').replace(':', '-').replace('.', '-')
CSV_RETRY_FILENAME  = 'log/retry.csv'
CSV_BAD_EMAILS_FILENAME = 'log/bad_emails-%s.csv' % str(datetime.now()).replace(' ', '-').replace(':', '-').replace('.', '-')
STATS_FILE          = 'log/pymailer-%s.stat' % str(datetime.now()).replace(' ', '-').replace(':', '-').replace('.', '-')

# smtp settings
SMTP_HOST     = ''
SMTP_PORT     = '25'
SMTP_USER     = '' # Leave empty if not needed
SMTP_PASSWORD = '' # Leave empty if not needed
ENCRYPT_MODE  = 'none' # Choose between 'none', 'ssl' and 'starttls'

# the address and name the email comes from
FROM_NAME = 'Company Name'
FROM_EMAIL = 'company@example.com'

# The number of emails to send to each recipient
NB_EMAILS_PER_RECIPIENT = 1

# test recipients list
TEST_RECIPIENTS = [
    {'name': 'Name', 'email': 'someone@example.com'},
]
