#!/usr/local/bin/python
#encoding:utf8
# import sys
# reload(sys).setdefaultencoding("utf-8")


from selenium import webdriver
import datetime
start_time = datetime.datetime.now()

options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/chromium"
chrome_driver_binary = "/mine/soft/chromedriver"
# options.add_argument("user-agent=\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0\"")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
print (1)
driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
print (2)
driver.get("https://www.baidu.com")
print (3)
driver.find_element_by_xpath("./*//input[@id='kw']").send_keys("哎哟卧槽")
driver.find_element_by_xpath("./*//input[@id='su']").click()
print (driver.page_source)
print ("done!")

print ("cost time:", (start_time-datetime.datetime.now()).total_seconds())
# cost time: -9.77149
print (2)
driver.get("https://www.baidu.com")
print (3)
driver.find_element_by_xpath("./*//input[@id='kw']").send_keys("哎哟卧槽")
driver.find_element_by_xpath("./*//input[@id='su']").click()
print (driver.page_source)
print ("done!")

print ("cost time:", (start_time-datetime.datetime.now()).total_seconds())
# cost time: -9.77149