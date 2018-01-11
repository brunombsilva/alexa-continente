from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from threading import Thread
import re

class Summary:
    def __init__(self, quantity, price):
        self.quantity = quantity
        self.price = price

class Product:
    def __init__(self, id, name, title=None, brand=None, notes=None, unit_price=None, small_image=None, large_image=None):
        self.id = id
        self.name = name
        self.title = title
        self.brand = brand
        self.notes = notes
        self.unit_price = unit_price
        self.small_image = small_image
        self.large_image = large_image

class Continente:
    URLS = {
        'login': 'http://www.continente.pt/',
        'cart': 'https://www.continente.pt/pt-pt/private/Pages/checkout.aspx',
        'product': 'https://www.continente.pt/stores/continente/pt-pt/public/Pages/ProductDetail.aspx?ProductId={}',
    }

    def __init__(self, username, password, driver, products = {}):
        self.driver = driver
        self.wait = wait = WebDriverWait(self.driver, 10)

        self.username = username
        self.password = password

        self.thread = None

	self.products = []
        for k,v in products.iteritems():
            self.products.append(Product(id=k, name=v))

    def dispose(self):
        if self.thread:
            self.thread.join()
        self.driver.close()

    def login_async(self):
        if self.thread is not None and self.thread.isAlive():
	    return False
	self.thread = Thread(target = self.login, args = ())
	self.thread.start()
	return True

    def login(self):
        driver = self.driver

        driver.get(self.URLS['login'])
        assert "Continente" in driver.title

	try:
	    driver.find_element_by_id('myAccountLogin')
	    return
        except:
	    pass

        username_element = driver.find_element_by_name("username")
        username_element.clear()
        username_element.send_keys(self.username)

        password_element = driver.find_element_by_name("password")
        password_element.clear()
        password_element.send_keys(self.password)

        login_button = driver.find_element_by_name('btnLogin')
        login_button.click()

	self.wait.until(EC.element_to_be_clickable((By.ID, 'myAccountLogin')))

        try:
            promos_modal = self.wait.until(EC.element_to_be_clickable((By.ID, 'blockUIClose')))
            promos_modal.click()
        except TimeoutException:
            pass

    def search(self, text):
	for i,p in enumerate(self.products):
		if p.name == text or p.id == text:
		    return p
        return None

    def add(self, product):
        self.driver.get(self.URLS['product'].format(product.id))

        self.driver.find_element_by_id('myAccountLogin')

        title = self.driver.find_element_by_css_selector('.productTitle').text
        brand = self.driver.find_element_by_css_selector('.productSubtitle').text
        notes = self.driver.find_element_by_css_selector('.productSubsubtitle').text

        small_image = self.driver.find_element_by_id('smallProduct').get_attribute('src')
        large_image = self.driver.find_element_by_id('bigProduct').get_attribute('href')

        unit_price_element = self.driver.find_element_by_css_selector('.pricePerUnit')
        unit_price = re.sub(r"[ \n]+", '', unit_price_element.text)

        add_button = self.driver.find_element_by_name('AddToBasket')
        add_button.click()

        product.title = title
        product.brand = brand
        product.notes = notes
        product.unit_price = unit_price
        product.small_image = small_image
        product.large_image = large_image

        return product
    
    def summary(self):
        self.driver.get(self.URLS['cart'])

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.totalPrice')))
        price = re.sub(r".* (\d+),(\d+)$", '\g<1>.\g<2>', element.text)
        
        try:
            element = self.driver.find_element_by_css_selector('.deliveryProductsNumber')
            quantity = re.sub(r"^\((\d+) artigos?\)$", '\g<1>', element.text)
        except:
            quantity = '0'

        return Summary(quantity, price)

