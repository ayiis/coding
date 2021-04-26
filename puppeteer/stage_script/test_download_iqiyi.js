// https://fettblog.eu/scraping-with-puppeteer/
const puppeteer = require('puppeteer'); // v 1.1.0
const { URL } = require('url');
const fse = require('fs-extra'); // v 5.0.0
const path = require('path');

const domains_in_blacklist = [
    // "ss1.bdstatic.com",
    // "jvc.flashapp.cn",
    // "hm.baidu.com",     // block main site
];
// application/octet-stream
let re_dont_save_type = [
  // "^image/.*$",
  "^text/.*$",
  "^application/.*$",
].join("|");
re_dont_save_type = new RegExp(`(${re_dont_save_type})`);

let re_save_type = [
  // "^application/octet-stream.*$",
  "^image/.*$",
].join("|");
re_save_type = new RegExp(`(${re_save_type})`);

async function start(urlToFetch) {
  // const browser = await puppeteer.launch({headless: true, devtools: false});
  const browser = await puppeteer.launch({
    executablePath: '/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    devtools: true,
    // headless: false,
    // devtools: true,
    slowMo: 10,
    defaultViewport: null,
    // args: [
    //   '--proxy-server=127.0.0.1:1087',
    //   '--proxy-bypass-list=<-loopback>',
    // ],
  });

  const page = await browser.newPage();

  await page.setRequestInterception(true);
  page.on('request', async(interceptedRequest) => {
      // const url = new URL(interceptedRequest.url())
      // if (domains_in_blacklist.includes(url.host) || /(image|stylesheet)$/.test(interceptedRequest.resourceType())) {
      //     interceptedRequest.abort()
      // } else {
      //     console.log(`[${interceptedRequest.resourceType()}]   ${interceptedRequest.url()}`);
      //     interceptedRequest.continue()
      // }
      // // console.log(`[getting] => [${interceptedRequest.resourceType()}]   ${interceptedRequest.url()}`);
      // if (url.pathname == "/video/video/chrome.webm") {
      //   interceptedRequest.abort();
      //   return;
      // }

      const url = new URL(interceptedRequest.url());
      let converted_path = url.pathname.replace(/\//g, '#');
      let filePath = path.resolve(`./${output_dir}/${converted_path}`);
      let eee = await fse.pathExists(filePath);
      if(eee) {
        console.log(`[✅CACHED] ${interceptedRequest.method()} ${filePath}`);
        const buffer= await fse.readFile(filePath);
        if(buffer.length > 0) {
          interceptedRequest.respond({
            status: 200,
            headers: {
              "access-control-allow-origin": "*",
              "ayskip": "1",
            },
            body: buffer,
          });
          return;
        }
      }
      interceptedRequest.continue();
  });

  page.on('response', async (response) => {
    const url = new URL(response.url());
    if (url.protocol == 'data:' || url.protocol == 'blob:') {
        console.log(`[skip] ${url.protocol} len: ${url.pathname.length}`);
        return;
    }
    if (response.status() >= 300) {
      console.log(`[redirect]   ${response.status()}   ${url.pathname}`);
      return;
    }
    if(response.headers()['ayskip']) {
      return;
    }
    const content_type = response.headers()['content-type'];
    if(content_type.match(re_dont_save_type) && !content_type.match(re_save_type)) {
      console.log(`[pass]   ${content_type}   ${url.pathname}`);
      return;
    } else {
      console.log(`[saving]   ${content_type}   ${url.pathname}`);
    }
    let converted_path = url.pathname.replace(/\//g, '#');
    // let converted_path = url.pathname;
    let filePath = path.resolve(`./${output_dir}/${converted_path}`);
    try {
      // console.log(url)
      // const data = ;
      await fse.outputFile(filePath, await response.buffer());
    } catch (err) {
      if (err.code === 'ENAMETOOLONG') {
        console.log(`ENAMETOOLONG: ${filePath}`)
      } else {
        console.log(url);
        console.log(err);
        // debugger;
      }
    }
  });

  await page.goto(urlToFetch, {
    waitUntil: 'networkidle2'   // there haven’t been more than 2 open network connections in the last 500ms
  });

  // setTimeout(async () => {
  //   await browser.close();
  // }, 1000 * 60);
}

const output_dir = 'acgbox';

// start('https://www.iqiyi.com/v_19rvma2gwk.html');
start('https://tu.acgbox.org/index.php/category/srww/');
// start('http://www.weather.com.cn/weather/101280101.shtml');
// start('https://simpl.info/video/offline/');
