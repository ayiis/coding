#!/usr/local/bin/python
#encoding:utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
古代数学巨著《九章算数》中有这么一道题叫“五家共井，甲二绠（汲水用的井绳）不足，如（接上）乙一绠；乙三绠不足，如丙一绠；

丙四绠不足，如丁一绠；丁五绠不足，如戊一绠；戊六绠不足，如甲一绠，皆及。

意思就是说五家人共用一口井，甲家的绳子用两条不够，还要再用乙家的绳子一条才能打到井水；乙家的绳子用三条不够，还要再用丙家的绳子

一条才能打到井水；丙家的绳子用四条不够，还要再用丁家的绳子一条才能打到井水；丁家的绳子用五条不够，还要再用戊家的绳子一条才能打

到井水；戊家的绳子用六条不够，还要再用甲家的绳子一条才能打到井水。

最后问：井有多深？每家的绳子各有多长？
"""
'''
z

a, b, c, d, e

z = 2a + b
z = 3b + c
z = 4c + d
z = 5d + e
z = 6e + a

b = 3z - 2a
c =

'''

js = "(function() {"
js += "function ajaxEventTrigger(event) {"
js += "var ajaxEvent = new CustomEvent(event, { detail: this });"
js += "window.dispatchEvent(ajaxEvent);"
js += "}"
js += "var oldXHR = window.XMLHttpRequest;"
js += "function newXHR() {"
js += "var realXHR = new oldXHR();"
js += "realXHR.addEventListener('abort', function () { ajaxEventTrigger.call(this, 'ajaxAbort'); }, false);"
js += "realXHR.addEventListener('error', function () { ajaxEventTrigger.call(this, 'ajaxError'); }, false);"
js += "realXHR.addEventListener('load', function () { ajaxEventTrigger.call(this, 'ajaxLoad'); }, false);"
js += "realXHR.addEventListener('loadstart', function () { ajaxEventTrigger.call(this, 'ajaxLoadStart'); }, false);"
js += "realXHR.addEventListener('progress', function () { ajaxEventTrigger.call(this, 'ajaxProgress'); }, false);"
js += "realXHR.addEventListener('timeout', function () { ajaxEventTrigger.call(this, 'ajaxTimeout'); }, false);"
js += "realXHR.addEventListener('loadend', function () { ajaxEventTrigger.call(this, 'ajaxLoadEnd'); }, false);"
js += "realXHR.addEventListener('readystatechange', function() { ajaxEventTrigger.call(this, 'ajaxReadyStateChange'); }, false);"
js += "realXHR.oldSend = realXHR.send;"
js += "realXHR.send = function(data) {"
js += "realXHR.requestData = data;"
js += "realXHR.oldSend(data);"
js += "};"
js += "realXHR.oldOpen = realXHR.open;"
js += "realXHR.open = function(method, url, async) {"
js += "realXHR.myURL = url;"
js += "realXHR.oldOpen(method, url, async);"
js += "};"
js += "return realXHR;"
js += "}"
js += "window.XMLHttpRequest = newXHR;"
js += "})();"

js += "window.addEventListener('ajaxReadyStateChange', function (e) {"
js += "if (e.detail.readyState === 4 && ((e.detail.responseURL && e.detail.responseURL.indexOf('https://gateway.igola.com/api-flight-polling-data-hub/separatedPolling') !== -1) || e.detail.myURL.indexOf('https://gateway.igola.com/api-flight-polling-data-hub/separatedPolling') !== -1)) {"
js += "window.igShoppingXHR = e.detail;"
js += "}"
js += "});"


print js





