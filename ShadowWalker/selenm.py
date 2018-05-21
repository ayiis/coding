#!/usr/local/bin/python
#encoding=utf8

from selenium import webdriver

options = webdriver.ChromeOptions()
options.binary_location = "/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome"
chrome_driver_binary = "/mine/soft/chromedriver"
driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
# driver = webdriver.PhantomJS()
print "start"
driver.implicitly_wait(30) # seconds
driver.get("https://www.wego.tw/flights/searches/cTPE-cOSA/2018-07-17:2018-07-23/economy/1a:0c:0i?sort=price&order=asc")

body = driver.find_element_by_tag_name("body")

print "========================="

shadowRoot = body.find_element_by_id('app').get_property('shadowRoot')

print dir(shadowRoot)

print shadowRoot.get_property('innerHTML')

print "-------------------------"

print


driver.quit()
