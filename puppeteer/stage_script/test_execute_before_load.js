'use strict';

const puppeteer = require('puppeteer');

function sniffDetector() {
  // execute in chrome
  // return true if someone get you user agent
  const userAgent = window.navigator.userAgent;
  const platform = window.navigator.platform;

  window.navigator.__defineGetter__('userAgent', function() {
    window.navigator.sniffed = true;
    return userAgent;   // makeup one
  });

  window.navigator.__defineGetter__('platform', function() {
    window.navigator.sniffed = true;
    return platform;   // makeup one
  });
}

(async() => {
  const browser = await puppeteer.launch({headless: true, devtools: false});
  // const browser = await puppeteer.launch({headless: false, devtools: true});
  const page = await browser.newPage();
  await page.evaluateOnNewDocument(sniffDetector);
  await page.goto('https://www.baidu.com', {waitUntil: 'networkidle2'});
  console.log('Sniffed: ' + (await page.evaluate(() => !!navigator.sniffed)));

  await page.evaluate("debugger");

  await browser.close();
})();
