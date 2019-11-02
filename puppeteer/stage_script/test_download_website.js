// https://fettblog.eu/scraping-with-puppeteer/
const puppeteer = require('puppeteer'); // v 1.1.0
const { URL } = require('url');
const fse = require('fs-extra'); // v 5.0.0
const path = require('path');
// const iconv = require('iconv-lite');
// 囿于采用目录结构保存资源，不能缓存 参数式调用 的请求
// 可以改成 非目录式 或 将请求中的特殊字符转换

const domains_in_blacklist = [
    "ss1.bdstatic.com",
    "pos.baidu.com",
    "promotion.chinaso.com",
    "s3m.nzwgs.com",
]

// some resource with redirect to other location, save it here
// 捕获跳转后的请求（兼容多次跳转）
let redirect_list = {}

async function start(urlToFetch) {
  // const browser = await puppeteer.launch({headless: true, devtools: false});
  const browser = await puppeteer.launch({
    executablePath: '/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    devtools: true,
    // headless: false,
    // devtools: true,
    defaultViewport: null,
  });

  const page = await browser.newPage();

  await page.setRequestInterception(true);
  page.on('request', async(interceptedRequest) => {
      const url = new URL(interceptedRequest.url());
      // if (domains_in_blacklist.includes(url.host) || /(image|stylesheet)$/.test(interceptedRequest.resourceType())) {
      //     interceptedRequest.abort()
      // }
       // else {
      //     console.log(`[${interceptedRequest.resourceType()}]   ${interceptedRequest.url()}`);
      //     interceptedRequest.continue()
      // }
      if (domains_in_blacklist.includes(url.host)) {
        console.log(`[❌BLOCKED] ${interceptedRequest.method()} ${url.host}${url.pathname}`);
        return interceptedRequest.abort();
      }
      if (url.protocol == 'data:' || url.protocol == 'blob:') {
          return interceptedRequest.continue();
      }

      let local_path = `${output_dir}/${url.host}/${url.pathname}`;
      local_path = path.resolve(local_path);
      if (url.pathname === '/' || url.pathname === '') {
        local_path = local_path + "_";
      }
      const eee = await fse.pathExists(local_path);
      if (eee) {
        console.log(`[✅CACHED] ${interceptedRequest.method()} ${local_path}`);
        const buffer= await fse.readFile(local_path);
        // debugger;
        // iconv.decode(buffer, 'GBK').toString();
        // fse.readFileSync(local_path, "latin1");
        // buffer.toString('utf8')
        interceptedRequest.respond({
          status: 200,
          // contentType: 'text/html',  // leave the contentType to browser
          body: buffer,
        });
      } else {
        console.log(`[✖️ NO DATA] ${url}`);
        interceptedRequest.continue();
      }
  });

  page.on('response', async (response) => {
    const url = new URL(response.url());
    if (url.protocol == 'data:' || url.protocol == 'blob:') {
      console.log(`[☑️ skip] ${url.protocol} len: ${url.pathname.length}`);
      return;
    }
    if (300 <= response.status() && response.status() <= 400) {
      let got = false;
      for (let a in redirect_list ) {
        if(response.url() === redirect_list[a]) {
          redirect_list[a] = response.headers().location;
          got = true;
          break;
        }
      }
      if (got === false) {
        redirect_list[response.url()] = response.headers().location;
      }
      console.log(`[〇redirect]   ${response.status()}   ${response.url()}   ${response.headers().location}`);
      return;
    }
    let filePath = `${output_dir}/${url.host}/${url.pathname}`;
    for (let a in redirect_list ) {
      if(response.url() === redirect_list[a]) {
        const url = new URL(a);
        filePath = `${output_dir}/${url.host}/${url.pathname}`;
        console.log(`[〇 end redirect]   ${response.url()}   ${a}`);
        break;
      }
    }

    filePath = path.resolve(filePath);
    if (url.pathname === '/') {
      filePath = filePath + "_";
    }
    try {
      const buffer = await response.buffer();
      // debugger;
      // iconv.decode(buffer, 'GBK').toString();
      await fse.outputFile(filePath, buffer);
      // await fse.outputFile(filePath, buffer.toString());
    } catch (err) {
      if (err.code === 'ENAMETOOLONG') {
        console.log(`ENAMETOOLONG: ${filePath}`);
      } else {
        console.log(url);
        console.log(err);
      }
    }
  });

  // there haven’t been more than 2 open network connections in the last 500ms
  await page.goto(urlToFetch, {waitUntil: 'networkidle2'});

  // setTimeout(async () => {await browser.close(); }, 1000 * 60);
}

const output_dir = './vidlox';
// start('http://www.weather.com.cn/weather/101280101.shtml');
start('https://vidlox.me/mfd2fhlhnr0t');
// start('https://www.baidu.com');
