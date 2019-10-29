const puppeteer = require('puppeteer');

// function sleep(ms) {
//   return new Promise(resolve => setTimeout(resolve, ms));
// }

(async () => {
    const browser = await puppeteer.launch({headless: true, devtools: false});
    // const browser = await puppeteer.launch({headless: false, devtools: true});
    const page = await browser.newPage();
    await page.goto('https://www.baidu.com');

    // await page.focus('#kw');
    await page.click('#kw');
    page.keyboard.type('时间');
    await page.click("#su");
    console.log('Now time:', 1);
    // await page.waitForNavigation({ waitUntil: 'networkidle2' });
    await page.mainFrame().waitForSelector('.op-beijingtime-time');
    console.log('Now time:', 2);

    // Get the "viewport" of the page, as reported by the page.
    const ts = await page.evaluate(() => {
        var date = $('.op-beijingtime-datebox>span:eq(1)').text().replace(/[^\d]/g, '');
        var time = $('.op-beijingtime-time').text().replace(/:/g, '');
        return date + time;
    });
    console.log('Now time:', ts);
    await browser.close();
})();
