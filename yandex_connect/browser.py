import contextlib
import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.options import Options


class ConnectWeb:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = self.create_driver()

    @staticmethod
    def create_driver():
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if sys.platform in ('linux', 'linux2'):
            driver_dir = 'linux'
        elif sys.platform == "darwin":
            driver_dir = 'mac'
        else:
            raise RuntimeError("Unsupported platform")

        driver_location = os.path.join(os.path.dirname(__file__), os.pardir, 'drivers', driver_dir, 'chromedriver')
        driver = webdriver.Chrome(executable_path=os.path.abspath(driver_location), options=options)
        return driver

    def __del__(self):
        driver = getattr(self, 'driver', None)
        if driver:
            try:
                driver.close()
                driver.quit()
            except ValueError:
                pass

    def make_screenshot(self, filename):
        with open(filename, 'wb') as wf:
            wf.write(self.driver.get_screenshot_as_png())

    @contextlib.contextmanager
    def make_error_screen_wrapper(self):
        try:
            yield
        except BaseException as exc:
            filename = f'/tmp/ya_error_screen_{exc.__class__.__name__}.png'
            self.make_screenshot(filename)
            print(f'{filename} saved')
            raise

    def login(self, username, password):
        with self.make_error_screen_wrapper():
            self.driver.get('https://passport.yandex.ru/')
            wait = ui.WebDriverWait(self.driver, 10)
            username_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="text"][@name="login"]'))
            username_input.send_keys(username)
            username_input.send_keys(Keys.ENTER)
            password_input = wait.until(
                lambda driver: driver.find_element_by_xpath('//input[@type="password"][@name="passwd"]'))
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
            try:
                wait.until(lambda driver: driver.find_element_by_xpath('//div[@class="dheader-user"]'))
            except TimeoutException:
                try:
                    wait.until(lambda driver: driver.find_element_by_xpath('//div/button/span[text()="Завершить регистрацию"]')).find_element_by_xpath("..").click()
                except TimeoutException:
                    wait.until(lambda driver: driver.find_element_by_xpath('//div/button/span[text()="Не сейчас"]')).find_element_by_xpath("..").click()
                wait.until(lambda driver: driver.find_element_by_xpath('//div[@class="dheader-user"]'))

    def add_mail(self, domain, surname, name, username, password):
        with self.make_error_screen_wrapper():
            self.login(self.username, self.password)
            self.driver.get('https://connect.yandex.ru/?join=open')
            wait = ui.WebDriverWait(self.driver, 60)
            admin_btn = wait.until(lambda driver: driver.find_element_by_xpath('//div[@class="dashboard-item__content dashboard-item__name"][text()="Админка"]'))
            admin_btn.click()
            domain_select = wait.until(lambda driver: driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div[2]/div[2]/button'))
            domain_select.click()
            domain_btn = wait.until(lambda driver: driver.find_element_by_xpath(f'//div/span[text()="{domain}"]'))
            domain_btn.click()

            add_btn = wait.until(lambda driver: driver.find_element_by_xpath('//button/span[text()="Добавить"]'))
            add_btn.click()
            add_employee_btn = wait.until(lambda driver: driver.find_element_by_xpath('//div[text()="Добавить сотрудника"]'))
            add_employee_btn.click()

            surname_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@name="name[last][ru]"]'))
            surname_input.send_keys(surname)
            name_input = wait.until(lambda driver: driver.find_element_by_xpath('//input[@name="name[first][ru]"]'))
            name_input.send_keys(name)

            time.sleep(1)

            email_input = wait.until(lambda driver: driver.find_element_by_xpath('/html/body/div[9]/div/div/div/div/div[3]/div/div/form/div[3]/div/div[2]/div/span/span/input'))
            email_input.send_keys(username)
            email_password_input = wait.until(lambda driver: driver.find_element_by_xpath('/html/body/div[9]/div/div/div/div/div[3]/div/div/form/div[4]/div[1]/div/div[2]/div/span/span/input'))
            email_password_input.send_keys(password)
            repeat_email_password_input = wait.until(lambda driver: driver.find_element_by_xpath('/html/body/div[9]/div/div/div/div/div[3]/div/div/form/div[4]/div[2]/div/div[2]/div/span/span/input'))
            repeat_email_password_input.send_keys(password)
            repeat_email_password_input.send_keys(Keys.ENTER)
            confirm_wait = ui.WebDriverWait(self.driver, 5)
            try:
                save_confirm_btn = confirm_wait.until(lambda driver: driver.find_element_by_xpath('//button/span[text()="Сохранить"]'))
                save_confirm_btn.click()
            except TimeoutException:
                pass
            try:
                wait.until(lambda driver: driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[2]'))
            except TimeoutException:
                self.driver.find_element_by_xpath('//div[text()="Такой логин занят."]')
                return
            self.driver.close()
            self.driver.quit()

            self.driver = self.create_driver()
            self.login(username + '@' + domain, password)
