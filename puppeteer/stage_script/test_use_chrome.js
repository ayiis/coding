const puppeteer = require('puppeteer');
const pAll = require("p-all");
// cannot use useragent or platform to judge if you are using chromium or chrome

(async () => {
    const actions = [];
    const browser = await puppeteer.launch({
        executablePath: '/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: true,
        devtools: false,
        // headless: false,
        // devtools: true,
        slowMo: 10,
        defaultViewport: null
    });
    for (const search of ["时间", "时间"]) {
        actions.push(async()=>{
            const page = await browser.newPage();
            await page.goto('https://www.baidu.com');

            await page.click('#kw');
            page.keyboard.type(search);

            await Promise.all([
                page.click("#su"),
                page.waitForNavigation({ waitUntil: 'networkidle2' }),
            ]);

            // Get the "viewport" of the page, as reported by the page.
            const ts = await page.evaluate(() => {
                var date = $('.op-beijingtime-datebox>span:eq(1)').text().replace(/[^\d]/g, '');
                var time = $('.op-beijingtime-time').text().replace(/:/g, '');
                return date + time;
            });

            console.log('Now time:', ts);
        });
    }
    await pAll(actions, {concurrency: 2}) // <-- set how many to search at once
    await browser.close();
})();
