// https://fettblog.eu/scraping-with-puppeteer/
const puppeteer = require('puppeteer'); // v 1.1.0
const { URL } = require('url');
const fse = require('fs-extra'); // v 5.0.0
const path = require('path');

async function start(urlToFetch) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  page.on('response', async (response) => {
    const url = new URL(response.url());
    if (url.protocol == 'data:') {
        console.log(`[SKIP] data len: ${url.pathname.length}`);
        return;
    }
    console.log("getting:", url.pathname)
    let filePath = path.resolve(`./output${url.pathname}`);
    if (url.pathname === '/') {
      filePath = `${filePath}/index.html`;
    }
    await fse.outputFile(filePath, await response.buffer());
  });

  await page.goto(urlToFetch, {
    waitUntil: 'networkidle2'   // there haven’t been more than 2 open network connections in the last 500ms
  });

  setTimeout(async () => {
    await browser.close();
  }, 1000 * 6);
}

start('https://www.baidu.com');
