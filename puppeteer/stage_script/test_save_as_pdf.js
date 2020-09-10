const puppeteer = require('puppeteer');
/*
    https://github.com/puppeteer/puppeteer/issues/2278
*/

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://www.baidu.com/', {waitUntil: 'networkidle2'});

  await page.emulateMedia("print");   // screen
  await page.pdf({
    path: 'test_save_as_pdf.pdf',
    format: "A4",
    printBackground: true,
    displayHeaderFooter: false,
    // height: 139 + DELTA + 3 + 3 + 'mm', // Additional page margins of 3mm
    // width: 550 + DELTA + 3 + 3 + 'mm', // Additional page margins of 3mm
    // margin: {
    //     top: 0,
    //     right: 0,
    //     bottom: 0,
    //     left: 0,
    // },
  });

  await browser.close();
})();
