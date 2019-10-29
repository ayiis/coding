const puppeteer = require('puppeteer');

function sleep(ms) {
    return new Promise(resolve=>{
        setTimeout(resolve,ms)
    })
}

(async () => {

    console.log("YOU CAN DO NOTHING FOR NOW");
    return;

    const browser = await puppeteer.launch({headless: true, devtools: true});
    const page = await browser.newPage();
    await page.goto('https://www.baidu.com');

    await page.click("#su", {button : 'right'});
    await sleep(1);
    console.log(1);
    await page.keyboard.down('Shift');
    await sleep(1);
    console.log(2);
    await page.keyboard.press('ArrowDown');
    await sleep(1);
    console.log(3);
    await page.keyboard.up('Shift');
    await sleep(1);
    console.log(4);
    await page.keyboard.press('Enter');
    await sleep(1);
    console.log(5);
    debugger;

    await browser.close();
})();
