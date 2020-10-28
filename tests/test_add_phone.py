import bootstrap
bootstrap.setup()

from database.models import Accounts
from onlinesim.exceptions import NoSmsCode

from onlinesim import api as onlinesim_api


if __name__ == '__main__':
    account = Accounts.objects.get(username='sova_daniil')
    client = account.get_bot_client()
    client.login()
    max_attempts = 10
    attempts = 0
    while True:
        try:
            attempts += 1
            tzid, phone = onlinesim_api.get_tzid_phone()
            client.client.send_sms_code(phone)
            code = onlinesim_api.get_sms(tzid)
            client.client.verify_sms_code(phone, code)
            onlinesim_api.set_operation_ok(tzid)
            break
        except NoSmsCode:
            if attempts >= max_attempts:
                raise
            else:
                continue
    print(f"Get phone: {phone}")
    account.phone = phone
    account.save()

