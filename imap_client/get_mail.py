import imaplib
import email
import email.message
import time
import re
import base64

from .exceptions import NoNewEmails, CantParseHtml

server = 'imap.yandex.ru'

subject_security_code = 'Verify Your Account'
subject_verify_link = 'Confirm your email address for Instagram'

ru_translate = {
    subject_security_code: 'Подтвердите сво',
}

max_attempts = 100
timeout = 5  # Seconds
utf_marker = '=?UTF-8?B?'


def mark_all_read(email_user, email_password):
    conn_attempts = 0
    max_conn_attempts = 100
    while True:
        try:
            conn_attempts += 1
            imap = imaplib.IMAP4_SSL(server)
            imap.login(email_user, email_password)
            break
        except imaplib.IMAP4.abort:
            if conn_attempts < max_conn_attempts:
                raise
            time.sleep(timeout)
    imap.select('INBOX')
    status, search_data = imap.search(None, '(UNSEEN)')
    assert status == 'OK'
    msg_id_list = search_data[0].split()
    for msg_id in msg_id_list:
        imap.store(msg_id, '+FLAGS', '\\Seen')
    try:
        imap.logout()
    except imaplib.IMAP4.abort:
        pass


def get_ig_mail_content(email_user, email_password, subject):
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        conn_attempts = 0
        max_conn_attempts = 100
        while True:
            try:
                conn_attempts += 1
                imap = imaplib.IMAP4_SSL(server)
                imap.login(email_user, email_password)
                break
            except imaplib.IMAP4.abort:
                if conn_attempts < max_conn_attempts:
                    raise
                time.sleep(timeout)
        try:
            imap.select('INBOX')
            status, search_data = imap.search(None, '(UNSEEN)')
            assert status == 'OK'
            msg_id_list = search_data[0].split()
            for msg_id in msg_id_list:
                _, msg_data = imap.fetch(msg_id, '(RFC822)')
                msg_raw = msg_data[0][1]
                msg = email.message_from_bytes(msg_raw, _class=email.message.EmailMessage)
                msg_subject = msg['Subject']
                if utf_marker in msg_subject:
                    msg_subject = base64.b64decode(msg_subject.replace(utf_marker, '')).decode()
                    subject = ru_translate.get(subject)
                if msg_subject == subject:
                    html_data = msg.get_payload()
                    imap.store(msg_id, '+FLAGS', '\\Seen')
                    return html_data
            time.sleep(timeout)
            continue
        finally:
            try:
                imap.logout()
            except imaplib.IMAP4.abort:
                pass
    raise NoNewEmails()


def get_security_code(email_user, email_password):
    ig_payload = get_ig_mail_content(email_user, email_password, subject_security_code)
    pattern = re.compile(r'<font size=3D"6">(.*)<\/font>')
    found = pattern.findall(ig_payload)
    if found:
        code = found[0]
    else:
        raise CantParseHtml()
    return code


def get_verify_link(email_user, email_password):
    ig_payload = get_ig_mail_content(email_user, email_password, subject_verify_link).replace('=\r\n', '')
    pattern = re.compile(r'(https://instagram.com/accounts/confirm_email[^\s]+)')
    found = pattern.findall(ig_payload)
    if found:
        link = found[0]
    else:
        raise CantParseHtml()
    return link
