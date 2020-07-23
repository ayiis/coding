// https://fettblog.eu/scraping-with-puppeteer/
const puppeteer = require('puppeteer'); // v 1.1.0
const { URL } = require('url');
const fse = require('fs-extra'); // v 5.0.0
const path = require('path');

async function start(urlToFetch) {
  // const browser = await puppeteer.launch({headless: true, devtools: false});
  const browser = await puppeteer.launch({
    executablePath: '/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    // devtools: true,
    // headless: false,
    devtools: false,
    defaultViewport: null,  // disable viewport =||
    // excludeSwitches: ["enable-automation"],
    // useAutomationExtension: false,
    // args: [
    //   '--enable-automation',
      // '--proxy-bypass-list=<-loopback>',
    // ],
  });

  const page = await browser.newPage();

  // there haven’t been more than 2 open network connections in the last 500ms
  await page.goto(urlToFetch, {waitUntil: 'networkidle2'});

  // setTimeout(async () => {await browser.close(); }, 1000 * 60);
}

start('https://www.baidu.com');
