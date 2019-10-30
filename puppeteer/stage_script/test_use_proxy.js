
'use strict';

const puppeteer = require('puppeteer');

(async() => {
  const browser = await puppeteer.launch({
    // Launch chromium using a proxy server on port 9876.
    // More on proxying:
    //    https://www.chromium.org/developers/design-documents/network-settings
    headless: true,
    devtools: false,
    // headless: false,
    // devtools: true,
    args: [
      '--proxy-server=127.0.0.1:1087',
      // Use proxy for localhost URLs
      '--proxy-bypass-list=<-loopback>',
    ]
  });
  const page = await browser.newPage();
  await page.goto('https://google.com');

  await page.click('input[name="q"]');
  await page.keyboard.type('puppeteer');
  await page.keyboard.press('Enter');

  await page.waitForNavigation({ waitUntil: 'networkidle2' });

  const href = await page.evaluate(() => {
    return document.querySelector('.rc>.r>a').getAttribute('href');
  });

  console.log(href);
  await browser.close();
})();
