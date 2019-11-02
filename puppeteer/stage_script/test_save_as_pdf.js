const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://www.baidu.com/', {waitUntil: 'networkidle2'});
  await page.pdf({path: 'test_save_as_pdf.pdf', format: 'A4'});

  await browser.close();
})();