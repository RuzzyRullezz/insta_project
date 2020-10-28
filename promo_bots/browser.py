import contextlib
import os
import json
import sys
import time
import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.options import Options

from pyctogram.instagram_client.exceptions import InstagramAccountHasBeenDisabled
from imap_client.get_mail import get_security_code, mark_all_read
from onlinesim import api as onlinesim_api
from onlinesim.exceptions import NoSmsCode

from .exceptions import NotValidIP, WaitError


def verify(account):
    account.get_bot_client().login()


class CheckpointChallenger:
    def __init__(self, username, password, email_user, email_password, proxy_ip=None, proxy_port=None):
        self.username = username
        self.password = password
        self.email_user = email_user
        self.email_password = email_password
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.img_prefix = username
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=en-us")
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})
        if self.proxy_ip and self.proxy_port:
            options.add_argument(f"--proxy-server={self.proxy_ip}:{self.proxy_port}")
        if sys.platform in ('linux', 'linux2'):
            driver_dir = 'linux'
        elif sys.platform == "darwin":
            driver_dir = 'mac'
        else:
            raise RuntimeError("Unsupported platform")

        driver_location = os.path.join(os.path.dirname(__file__), os.pardir, 'drivers', driver_dir, 'chromedriver')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath(driver_location),
                                       options=options)

    def __del__(self):
        driver = getattr(self, 'driver', None)
        if driver:
            driver.close()
            driver.quit()

    def make_screenshot(self, filename):
        with open(filename, 'wb') as wf:
            wf.write(self.driver.get_screenshot_as_png())

    @contextlib.contextmanager
    def make_error_screen_wrapper(self):
        try:
            yield
        except BaseException as exc:
            filename = f'/tmp/{self.img_prefix}_challenger_error_screen_{exc.__class__.__name__}.png'
            self.make_screenshot(filename)
            print(f'{filename} saved')
            raise

    def check_ip(self):
        with self.make_error_screen_wrapper():
            self.driver.get('https://jsonip.com/')
            wait = ui.WebDriverWait(self.driver, 10)
            response = wait.until(lambda driver: driver.find_element_by_xpath('/html/body/pre'))
            print(json.loads(response.text)['ip'])

    def login(self):
        with self.make_error_screen_wrapper():
            self.driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
            wait = ui.WebDriverWait(self.driver, 10)

            username_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="text"][@name="username"]'))
            username_input.send_keys(self.username)
            password_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="password"][@name="password"]'))
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.ENTER)

    def select_bdate(self):
        self.login()
        wait = ui.WebDriverWait(self.driver, 20)
        with self.make_error_screen_wrapper():
            date_select = wait.until(lambda driver: driver.find_element_by_xpath('//select[@title="Year:"]'))
            date_select.send_keys('1989')
            submit_btn = wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Submit"]'))
            submit_btn.click()
            time.sleep(10)

    def challenge(self):
        self.login()
        wait = ui.WebDriverWait(self.driver, 10)
        with self.make_error_screen_wrapper():
            phone = None
            try:
                choice = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="radio"][@value="1"]'))
                choice.find_element_by_xpath("..").click()
            except TimeoutException:
                try:
                    self.driver.find_element_by_xpath("//body/pre")
                    raise WaitError("Wait several minutes.")
                except NoSuchElementException:
                    pass
                try:
                    self.driver.find_element_by_xpath("//p[text()='Please wait a few minutes before you try again.']")
                    raise WaitError("Wait several minutes.")
                except NoSuchElementException:
                    pass
                try:
                    self.driver.find_element_by_xpath('//input[@type="text"][@name="username"]')
                    raise NotValidIP("Not valid client ip")
                except NoSuchElementException:
                    pass
                try:
                    phone_input = wait.until(lambda driver: driver.find_element_by_xpath('//*[@id="phone_number"]'))
                    phone_input.clear()
                    tzid, phone = onlinesim_api.get_tzid_phone(owner_username=self.username)
                    phone_input.send_keys(phone)
                    phone_input.send_keys(Keys.ENTER)
                    code = onlinesim_api.get_sms(tzid)
                    onlinesim_api.set_operation_ok(tzid)
                except TimeoutException:
                    try:
                        email_input = self.driver.find_element_by_xpath('//*[@name="email"]')
                    except NoSuchElementException:
                        try:
                            self.driver.find_element_by_xpath('//*[@value="Request Download"]')
                        except NoSuchElementException:
                            self.driver.find_element_by_xpath('//*[@value="Download Your Data"]')
                        raise InstagramAccountHasBeenDisabled(msg='Challenge error - account banned.', status_code=200)
                    email_input.clear()
                    email_input.send_keys(self.email_user)
                    submit_btn = self.driver.find_element_by_xpath('//input[@type="submit"]')
                    submit_btn.click()
                    mark_all_read(self.email_user, self.email_password)
                    code = get_security_code(self.email_user, self.email_password)
            else:
                mark_all_read(self.email_user, self.email_password)
                submit_btn = wait.until(lambda driver: driver.find_elements_by_xpath('//button'))[1]
                submit_btn.click()
                code = get_security_code(self.email_user, self.email_password)
            code_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="tel"][@name="security_code"]'))
            code_input.send_keys(code)
            code_input.send_keys(Keys.ENTER)
            time.sleep(10)
            for attempt in range(0, 50):
                self.driver.get(f'https://www.instagram.com/{self.username}')
                try:
                    this_wasme_btn = wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="This Was Me"]'))
                    this_wasme_btn.click()
                    time.sleep(10)
                except TimeoutException:
                    break
            else:
                raise RuntimeError("Too many 'Was not me' errors.")
            cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
            return cookies, phone

    def phone_challenge(self, checkpoint_url):
        with self.make_error_screen_wrapper():
            wait = ui.WebDriverWait(self.driver, 10)
            max_attempts = 10
            attempts = 0
            while True:
                try:
                    attempts += 1
                    self.driver.get(checkpoint_url)
                    phone_input = wait.until(lambda driver: driver.find_element_by_xpath('//*[@id="phone_number"]'))
                    tzid, phone = onlinesim_api.get_tzid_phone(owner_username=self.username)
                    phone_input.send_keys(phone)
                    phone_input.send_keys(Keys.ENTER)
                    code = onlinesim_api.get_sms(tzid)
                    onlinesim_api.set_operation_ok(tzid)
                    break
                except NoSmsCode:
                    if attempts >= max_attempts:
                        raise
            code_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="tel"][@name="security_code"]'))
            code_input.send_keys(code)
            code_input.send_keys(Keys.ENTER)
            time.sleep(10)
            cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
            return cookies, phone


class Register:
    def __init__(self, full_name, username, password, email_user, email_password, proxy_protocol=None, proxy_ip=None, proxy_port=None):
        self.full_name = full_name
        self.username = username
        self.password = password
        self.email_user = email_user
        self.email_password = email_password
        self.proxy_protocol = proxy_protocol
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if self.proxy_protocol is not None and self.proxy_ip and self.proxy_port:
            options.add_argument(f"--proxy-server={self.proxy_protocol}{self.proxy_ip}:{self.proxy_port}")
        if sys.platform in ('linux', 'linux2'):
            driver_dir = 'linux'
        elif sys.platform == "darwin":
            driver_dir = 'mac'
        else:
            raise RuntimeError("Unsupported platform")

        driver_location = os.path.join(os.path.dirname(__file__), os.pardir, 'drivers', driver_dir, 'chromedriver')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath(driver_location),
                                       options=options)

    def __del__(self):
        driver = getattr(self, 'driver', None)
        if driver:
            driver.close()
            driver.quit()

    def reg(self):
        init_phone = '+79186391601'
        self.driver.get('https://www.instagram.com/')
        wait = ui.WebDriverWait(self.driver, 10)

        phone_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="text"][@name="emailOrPhone"]'))
        phone_input.send_keys(init_phone)
        fullname_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="text"][@name="fullName"]'))
        fullname_input.send_keys(self.full_name)
        username_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="text"][@name="username"]'))
        username_input.send_keys(self.username)
        password_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="password"][@name="password"]'))
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.ENTER)

        max_attempts = 10
        attempts = 0
        while True:
            try:
                attempts += 1
                phone_change_btn = wait.until(lambda driver: driver.find_element_by_xpath('//*[@id="confirmationCodeDescription"]/../div[position()=2]/button[1]'))
                phone_change_btn.click()
                new_phone_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="tel"][@name="newPhoneNumber"]'))
                tzid, phone = onlinesim_api.get_tzid_phone(owner_username=self.username)
                new_phone_input.send_keys(phone)
                new_phone_input.send_keys(Keys.ENTER)
                code_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="tel"][@name="confirmationCode"]'))
                code = onlinesim_api.get_sms(tzid)
                onlinesim_api.set_operation_ok(tzid)
                code_input.send_keys(code)
                code_input.send_keys(Keys.ENTER)
                break
            except NoSmsCode:
                if attempts >= max_attempts:
                    raise
        try:
            age_choice = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="radio"][@value="above_18"]'))
            age_choice.click()
            age_choice.find_element_by_xpath('../../../../..').find_element_by_xpath('div[3]/div/button').click()
        except TimeoutException:
            pass
        try:
            wait.until(lambda driver: driver.find_element_by_xpath('//*[@id="phoneSignupConfirmErrorAlert"]'))
            raise RuntimeError("Can't register account")
        except TimeoutException:
            pass
        try:
            wait.until(lambda driver: driver.find_element_by_xpath("//*[text()='Включить']")).click()
            return phone
        except TimeoutException:
            try:
                new_phone_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="tel"][@name="phone_number"]'))
                new_phone_input.clear()
                tzid, phone = onlinesim_api.get_tzid_phone(owner_username=self.username)
                new_phone_input.send_keys(phone)
                new_phone_input.send_keys(Keys.ENTER)
                code = onlinesim_api.get_sms(tzid)
                onlinesim_api.set_operation_ok(tzid)
                new_code_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="tel"][@name="security_code"]'))
                new_code_input.send_keys(code)
                new_code_input.send_keys(Keys.ENTER)
                time.sleep(10)
            except TimeoutException:
                pass
        return phone


class PhotoUploader:
    def __init__(self, username, password, fb_email, fb_pass, proxy_ip=None, proxy_port=None):
        self.username = username
        self.password = password
        self.fb_email = fb_email
        self.fb_pass = fb_pass
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.wait_time = 20
        options = Options()
        options.add_argument("--headless")
        mobile_emulation = {
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en'})
        if self.proxy_ip and self.proxy_port:
            options.add_argument(f"--proxy-server={self.proxy_ip}:{self.proxy_port}")
        if sys.platform in ('linux', 'linux2'):
            driver_dir = 'linux'
        elif sys.platform == "darwin":
            driver_dir = 'mac'
        else:
            raise RuntimeError("Unsupported platform")

        driver_location = os.path.join(os.path.dirname(__file__), os.pardir, 'drivers', driver_dir, 'chromedriver')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath(driver_location),
                                       options=options)
        self.wait = ui.WebDriverWait(self.driver, self.wait_time)

    def __del__(self):
        driver = getattr(self, 'driver', None)
        if driver:
            driver.close()
            driver.quit()

    @contextlib.contextmanager
    def make_error_screen_wrapper(self):
        try:
            yield
        except BaseException as exc:
            filename = f'/tmp/error_screen_{exc.__class__.__name__}.png'
            with open(filename, 'wb') as wf:
                wf.write(self.driver.get_screenshot_as_png())
                print(f'{filename} saved')
            raise

    def make_screenshot(self):
        filename = f'/tmp/screen_{datetime.datetime.now().isoformat()}.png'
        with open(filename, 'wb') as wf:
            wf.write(self.driver.get_screenshot_as_png())
            print(f'{filename} saved')

    def login(self):
        with self.make_error_screen_wrapper():
            self.driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
            wait = self.wait
            username_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="text"][@name="username"]'))
            username_input.send_keys(self.username)
            password_input = \
            wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="password"][@name="password"]'))
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.ENTER)

            try:
                wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Not Now"]')).click()
                wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Cancel"]')).click()
            except TimeoutException:
                self.facebook_auth()
            return self

    def facebook_auth(self):
        wait = self.wait
        wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Log In"]')).click()
        try:
            max_attempts = 10
            attempts = 0
            while True:
                try:
                    wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Continue with Facebook"]')).click()
                    break
                except StaleElementReferenceException:
                    if attempts > max_attempts:
                        raise
                    else:
                        continue
        except TimeoutException:
            wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Log In with Facebook"]')).click()

        fb_email_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@name="email"]'))
        fb_email_input.send_keys(self.fb_email)

        fb_pass_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@name="pass"]'))
        fb_pass_input.send_keys(self.fb_pass)
        fb_pass_input.send_keys(Keys.ENTER)

        wait.until(lambda driver: driver.find_element_by_xpath('//form[@action="/dialog/oauth/skip/submit/"]'))

        max_attempts = 10
        attempts = 0
        while True:
            attempts += 1
            try:
                wait.until(lambda driver: driver.find_element_by_xpath('(//button)[1]')).click()
                break
            except StaleElementReferenceException:
                if attempts > max_attempts:
                    raise
                else:
                    continue

        try:
            wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Not Now"]')).click()
            wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Cancel"]')).click()
        except TimeoutException:
            pass

    def upload(self, image_path):
        with self.make_error_screen_wrapper():
            wait = self.wait
            wait.until(lambda driver: driver.find_element_by_xpath('(//span[@aria-label="New Post"])[1]/..')).click()
            wait.until(lambda driver: driver.find_element_by_xpath('(//input[@type="file"])[1]')).send_keys(image_path)
            wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Next"]')).click()
            wait.until(lambda driver: driver.find_element_by_xpath('//button[text()="Share"]')).click()

            time.sleep(120)
            return self
