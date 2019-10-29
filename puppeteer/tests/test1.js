const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({headless: false, devtools: true});
  const page = await browser.newPage();
  await page.goto('https://www.baidu.com');
  await page.screenshot({path: 'www.baidu.png'});

  await page.click('#su');
  await page.evaluate(() => {console.log(1,2,3);});
  await page.evaluate(() => {debugger;});
  await browser.close();
})();

// chrome://inspect/#devices
// node --inspect-brk node_modules/.bin/jest test1.js