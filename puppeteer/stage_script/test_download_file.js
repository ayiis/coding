// https://github.com/GoogleChrome/puppeteer/issues/299
// https://github.com/GoogleChrome/puppeteer/issues/1478
// Not work if element under z-index discover
// $("#btnsFirst>.inst.need_to_fixed.ie-down")[0].click()
const puppeteer = require('puppeteer')
const fs = require('fs')
const mkdirp = require('mkdirp')
const path = require('path')
const uuid = require('uuid/v1');

function sleep(ms) {
    return new Promise(resolve=>{
        setTimeout(resolve,ms)
    })
}

async function download(page, selector) {
    // const downloadPath = path.resolve(__dirname, 'download', uuid())
    const downloadPath = path.resolve("/tmp", uuid())
    mkdirp(downloadPath)
    // console.log('Downloading file to:', downloadPath)
    await page._client.send('Page.setDownloadBehavior', { behavior: 'allow', downloadPath: downloadPath })
    await page.mainFrame().waitForSelector(selector, {visible: true});
    // await page.click(selector)
    await page.evaluate(() => {
        $("#btnsFirst>.inst.need_to_fixed.ie-down")[0].click();
        return true;
    });
    let filename = await waitForFileToDownload(downloadPath)
    return path.resolve(downloadPath, filename)
}

async function waitForFileToDownload(downloadPath) {
    // console.log('Waiting to download file...')
    let filename
    while (!filename || filename.endsWith('.crdownload')) {
        filename = fs.readdirSync(downloadPath)[0]
        await sleep(500)
    }
    return filename
}

(async () => {

    const browser = await puppeteer.launch({headless: true, devtools: false});
    // const browser = await puppeteer.launch({headless: false, devtools: true});
    const page = await browser.newPage();
    await page.goto('https://www.360.cn/');
    
    await page.mainFrame().waitForSelector(".slide-pcws", {visible: true});

    // https://dl.360safe.com/360/inst.exe
    const file_path = await download(page, "#btnsFirst>.inst.need_to_fixed.ie-down");
    console.log(file_path);
    await browser.close();
})();

