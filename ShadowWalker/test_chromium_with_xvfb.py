#!/usr/local/bin/python
#encoding:utf8
# import sys
# reload(sys).setdefaultencoding("utf-8")


from selenium import webdriver
import datetime
start_time = datetime.datetime.now()
print (1)
driver = webdriver.Chrome()
print (2)
driver.get("https://www.baidu.com")
print (3)
driver.find_element_by_xpath("./*//input[@id='kw']").send_keys("哎哟卧槽")
driver.find_element_by_xpath("./*//input[@id='su']").click()
print (driver.page_source)
print ("done!")

print ("cost time:", (start_time-datetime.datetime.now()).total_seconds())
# cost time: -6.14491
print (2)
driver.get("https://www.baidu.com")
print (3)
driver.find_element_by_xpath("./*//input[@id='kw']").send_keys("哎哟卧槽")
driver.find_element_by_xpath("./*//input[@id='su']").click()
print (driver.page_source)
print ("done!")

print ("cost time:", (start_time-datetime.datetime.now()).total_seconds())
# cost time: -6.14491