'use strict';

const puppeteer = require('puppeteer');
const devices = require('puppeteer/DeviceDescriptors');

async function sleep(sec) {
    return new Promise(resolve => setTimeout(resolve, 1000*sec));
}

(async() => {
  // const browser = await puppeteer.launch();

    // 配置 puppeteer 使用固定的 Chrome，预先输入登录信息
    const browser = await puppeteer.launch({
        executablePath: "/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome",
        userDataDir: "/tmp/tmp",
        // headless: true,
        headless: false,
        devtools: false,
        // devtools: true,
        slowMo: 20,
        defaultViewport: null
    });

    const context = browser.defaultBrowserContext();
    await context.clearPermissionOverrides();

  const page = await browser.newPage();
  // await page.emulate(devices['iPhone 7']);
  // await page.goto('https://news.cnblogs.com/');
  await page.goto('https://time.geekbang.org/column/article/68728', {waitUntil: 'networkidle2'});
  await sleep(3);
  await page.screenshot({path: 'full.png', fullPage: true});
  await browser.close();
})();
