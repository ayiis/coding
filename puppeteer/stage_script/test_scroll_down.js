const puppeteer = require('puppeteer');
const fse = require('fs-extra'); // v 5.0.0
const { URL } = require('url');
const path = require('path');
const mongo = require('mongodb');
const https = require('https');
const fs = require('fs');
const ppt_request_intercept = require('../common/request_intercept.js');
const ppt_page_control = require('../common/page_control.js');
const ppt_base = require('../common/base.js');

const settings = {
    // "start_page": "https://time.geekbang.org/column/article/4906",
    // "start_page": "https://time.geekbang.org/column/article/14252",
    "start_page": "https://readhub.cn/topics",
}

;(async () => {

    // 配置 puppeteer 使用固定的 Chrome，预先输入登录信息
    const browser = await puppeteer.launch({
        executablePath: "/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome",
        // userDataDir: "/tmp/tmp",
        userDataDir: "/tmp/tmp2",
        // headless: true,
        // devtools: false,
        headless: false,
        devtools: true,
        slowMo: 200,
        defaultViewport: null,  // 
        // args: [
        //     "--window-size=1920,1080",
        // ],
    });

    const page = await browser.newPage();

    await page.goto(settings["start_page"], {waitUntil: "networkidle2"});
    await ppt_request_intercept.insert_jquery(page);

    await ppt_base.sleep(3);

    // await ppt_page_control.scroll_to_bottom_by_element(page);
    // await ppt_page_control.scroll_to_bottom_by_body(page);
    await ppt_page_control.scroll_to_bottom_by_keyboard(page);
    // await ppt_page_control.scroll_to_bottom(page);

    // await page.close();
    // await browser.close();

})();
