// https://medium.com/@jaredpotter1/connecting-puppeteer-to-existing-chrome-window-8a10828149e0
// https://github.com/puppeteer/puppeteer/issues/4579
// http://127.0.0.1:9999/json/version
const puppeteer = require('puppeteer');
const program = require('commander');

program.option('-w, <type>', 'ws debug url');
program.option('-t, <type>', 'title contains');
program.option('-c, <type>', '1:close, else:disconnect');
program.parse(process.argv);


function sleep(ms) {
    return new Promise(resolve=>{
        setTimeout(resolve,ms)
    })
}

if(!program.W) {

    console.log(program.opts());
    console.log("Must provide a ws url!");

} else {
    (async () => {
        const browser = await puppeteer.connect({
            defaultViewport: null,
            slowMo: 10,
            ignoreHTTPSErrors: true,
            browserWSEndpoint: program.W,
        });
        // console.log("Total pages:", pages.length);

        // const page = await browser.newPage();
        // debugger;

        let good_result = false;
        for (let n = 0 ; n < 100 ; n++ ) {
            try {
                let pages = await browser.pages();
                for(let i = 0 ; i < pages.length ; i++ ) {
                    let title = await pages[i].title();
                    if(title.match(program.T)) {
                        good_result = true;
                        break;
                    }
                }
            } catch ( err ) {
                // await pages[i].title() may cause exception when goto other pages
            }
            if (good_result) {
                break;
            }
            await sleep(100);
        }

        if(program.C == "1") {
            await browser.close();
        } else {
            await browser.disconnect();
        }
        if (good_result) {
            console.log("pass");
        } else {
            console.log("fail");
        }
    })();
}
