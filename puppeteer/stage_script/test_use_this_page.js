// https://github.com/puppeteer/puppeteer/issues/443
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({headless: true, devtools: false});
    // const browser = await puppeteer.launch({headless: false, devtools: true});
    const page = await browser.newPage();
    const pages = await browser.pages();
    const page2 = pages[1];

    if (pages.length != 2) {
        console.log("page init failed");
    }

    if (page2 != page) {
        console.log("wrong page");
    }

    await browser.close();
})();
