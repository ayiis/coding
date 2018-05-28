#encoding:utf8
from selenium import webdriver
import datetime
start_time = datetime.datetime.now()

print (1)
driver = webdriver.PhantomJS(executable_path="/mine/soft/phantomjs-2.1.1-macosx/bin/phantomjs")
print (2)
driver.get("http://www.baidu.com")
print (3)
driver.find_element_by_xpath("./*//input[@id='kw']").send_keys(u"哎哟卧槽")
driver.find_element_by_xpath("./*//input[@id='su']").click()
driver.page_source

print ("cost time:", (start_time-datetime.datetime.now()).total_seconds())

print (2)
driver.get("http://www.baidu.com")
print (3)
driver.find_element_by_xpath("./*//input[@id='kw']").send_keys(u"哎哟卧槽")
driver.find_element_by_xpath("./*//input[@id='su']").click()
driver.page_source

print ("cost time:", (start_time-datetime.datetime.now()).total_seconds())
