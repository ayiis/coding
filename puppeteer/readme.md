When I got a list, I got a fire in my soul.

꧁༺༽༾ཊ࿈ཏ༿༼༻꧂

✅❌⭕️
☑️✖️ 

Stage and Target:


✖️ Stage 0x01:

✅    1. Init PP, install basic dependences

✅    2. Run <tc>.helloworld on Chromium

✅    3. Run basic <tc>

✅    0. Use specify page.

✅    4. Develop the basic action you can image:

        ✅ click a [ button | link | js_button ]

        ✅ make a time search on baidu

        ✅ open two page and make a time search in the same time on baidu

        ⭕️ right click and see the menu to do something [ can do nothing by now ]

        ⭕️ paste from clipboard [ the clipboard and content menu is control by the OS ]

        ✅ grep all link in the search result of www.baidu.com

        ✅ download a file and save to `/tmp`.

        ✅ execute some javascript codes before document load.

        ✅ wait for elements/events/lazyload-js/script-executed

            - https://stackoverflow.com/questions/53483578/puppeteer-wait-for-all-javascript-is-executed

✅    5. Block some url or site.

✅    6. use proxy to do a google search `puppeteer`.

✅    7. download a website to local and browser.

✖️    0. Download video from iqiyi

        *notice: voice and video may be apart to reduce the transfer size.

✖️    0. Download the m3u8 resources and concat as a workable.ts

        - as you are using Chromium. You can't do it directly. by `save as`

        - just by on('response')

        - find out why Thunder can be so fast like that.

            - Thunder need a function: multi URL to download one file, for some site have a expire time.

✖️    0.  upload files with <input file>

            https://dev.to/sonyarianto/practical-puppeteer-how-to-upload-a-file-programatically-4nm4

            https://github.com/puppeteer/puppeteer/issues/857

            https://github.com/puppeteer/puppeteer/issues/2946

            https://easyupload.io/

            /tmp/up/1.jpeg /tmp/up/2.png


⭕️    0. 屏蔽 chrome is being controlled
            每个版本的 chrome 都不一样

✅    0. 屏蔽 自动设置的宽和高
            pyppeteer 里面 defaultViewport 无效


✖️ Stage 0x02:

✅    1. use PP connect to Chrome

✅    2. pass all <tc>

✅    3. change `zuixinwine` to PP mode

✖️    4. challenge 1688 product

✖️    5. challenge jd to make an order


✖️ Stage 0x03:

✅    1. using user's data

✖️    0. Grep from douban zufang.

✖️    2. Who am I: Mess up all activities of my network accounts

        - https://adssettings.google.com/authenticated

        - 让谷歌猜猜你是一个什么样的人，数据投毒才能治用户画像


2013
2014
2015
2016

 4934 4934

```javascript

    - 打开多个网页时，chrome 会优先加载当前tab的页面，即使加载完也不会及时加载其他页面
      设置 headless=true 时没有此问题

    - BUG: Session closed. Most likely the page has been closed.
        - https://blog.csdn.net/qq_42004597/article/details/90033648
        ON: /usr/local/lib/python3.7/site-packages/pyppeteer/connection.py:L45

            self._url, max_size=None, loop=self._loop)
            =>
            self ._url, max_size=None, loop=self ._loop, ping_interval=None, ping_timeout=None)

    [debug](https://www.jianshu.com/p/6505515d73d5)
        node inspect test.js
        c n repl

    page.waitForSelector('#myId', {visible: true})

blobUrl = window.URL.createObjectURL(blob);


var link = document.createElement("a"); // Or maybe get it from the current document
link.href = blobUrl;
link.download = "aDefaultFileName.txt";
link.innerHTML = "Click here to download the file";
document.body.appendChild(link); // Or append it whereever you want



var saveData = (function () {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (data, fileName) {
        var json = JSON.stringify(data),
            blob = new Blob([json], {type: "octet/stream"}),
            url = window.URL.createObjectURL(blob);
        a.href = url;
        a.download = fileName;
        a.click();
        window.URL.revokeObjectURL(url);
    };
}());
var data = { x: 42, s: "hello, world", d: new Date() },fileName = "my-download.json";
saveData(data, fileName);




var saveData = (function () {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (blob, fileName) {
        var blob_url = window.URL.createObjectURL(blob);
        a.href = blob_url;
        a.download = fileName;
        a.click();
        window.URL.revokeObjectURL(blob_url);
    };
}());


var video_url = $0.src;

var blob = await fetch(video_url).then(r => r.blob());
var file = new File([blob], "test.mp4", { type: "octet/stream" });

saveData(file, "test.mp4");


var saveData = (function () {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (blob, fileName) {
        var blob_url = window.URL.createObjectURL(blob);
        a.href = blob_url;
        a.download = fileName;
        a.click();
        window.URL.revokeObjectURL(blob_url);
    };
}());
window.URL.revokeObjectURL = function(video_url){ 
    var xhr = new XMLHttpRequest(); xhr.open('get', video_url, true); xhr.responseType = 'blob';
    xhr.onload = () => { saveData(this.blob, "111.mp4"); }; xhr.send();
}

window.URL._createObjectURL = window.URL.createObjectURL;
window.URL.createObjectURL = function(blob) {
    a.href = blob_url;
    a.download = fileName;
    a.click();
    window.URL._createObjectURL(blob);
}

window.URL._createObjectURL = window.URL.createObjectURL;
window.URL.createObjectURL = (function () {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (blob) {
        var blob_url = window.URL._createObjectURL(blob);
        console.log("GOT:", blob_url, blob);
        if (blob.size > 1024 * 1024 || blob.duration !== undefined) {
            debugger;
            a.href = blob_url;
            a.download = "" + new Date().getTime() + ".mp4";
            a.click();
        }
        return window.URL._createObjectURL(blob);
    };
}());

------

var video_url = $('video').src;
var xhr = new XMLHttpRequest(); xhr.open('get', video_url, true); xhr.responseType = 'blob';
xhr.onload = () => { saveData(this.blob, "111.mp4"); }; xhr.send();


移花接木:

// <video width="100%" height="100%" x-webkit-airplay="allow" src="blob:https://www.iqiyi.com/2c59c3ee-79b9-4ea0-82e9-5a725a25518f"></video>

window.URL._createObjectURL = window.URL.createObjectURL;
window.URL.createObjectURL = (function () {
    var video = document.createElement("video");
    document.body.appendChild(video);
    video.width = "100%";
    video.height = "100%";
    video["x-webkit-airplay"] = "allow";
    return function (blob) {
        var blob_url = window.URL._createObjectURL(blob);
        console.log("GOT:", blob_url, blob);
        if (blob.size > 1024 * 1024 || blob.duration !== undefined) {
            video.src = blob_url;
        }
        return window.URL._createObjectURL(blob);
    };
}());


window.URL._createObjectURL = window.URL.createObjectURL;
window.URL.createObjectURL = (function () {
    var video = document.createElement("video");
    document.body.appendChild(video);
    video.setAttribute('width', '100%');
    video.setAttribute('height', '100%');
    video.setAttribute('x-webkit-airplay', 'allow');
    return function (blob) {
        var blob_url = window.URL._createObjectURL(blob);
        console.log("GOT:", blob_url, blob);
        if (blob.size > 1024 * 1024 || blob.duration !== undefined) {
            video.src = blob_url;
            return window.URL._createObjectURL(new Blob(["json"], {type: "octet/stream"}));
        }
        return blob_url;
    };
}());


https://simpl.info/video/offline/

------

function blob2file(blobData) {
    const fd = new FormData();
    fd.set('a', blobData);
    return fd.get('a');
}

window.URL._createObjectURL = window.URL.createObjectURL;
window.URL.createObjectURL = (function () {
    function blob2file(blobData) {
        const fd = new FormData();
        fd.set('a', blobData, 'filename_or_empty');
        return fd.get('a');
    }
    return function(blobData) {
        const zzz = blob2file(blobData);
        debugger;
        return window.URL._createObjectURL(blobData);
    }
}());

------

var file = new File([myBlob], "name");

------

let blob = await fetch(url).then(r => r.blob());

------

function blobToFile(theBlob, fileName){
    //A Blob() is almost a File() - it's just missing the two properties below which we will add
    theBlob.lastModifiedDate = new Date();
    theBlob.name = fileName;
    return theBlob;
}

------

function base64ToFile(base64Data, tempfilename, contentType) {
    contentType = contentType || '';
    var sliceSize = 1024;
    var byteCharacters = atob(base64Data);
    var bytesLength = byteCharacters.length;
    var slicesCount = Math.ceil(bytesLength / sliceSize);
    var byteArrays = new Array(slicesCount);

    for (var sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
        var begin = sliceIndex * sliceSize;
        var end = Math.min(begin + sliceSize, bytesLength);

        var bytes = new Array(end - begin);
        for (var offset = begin, i = 0 ; offset < end; ++i, ++offset) {
            bytes[i] = byteCharacters[offset].charCodeAt(0);
        }
        byteArrays[sliceIndex] = new Uint8Array(bytes);
    }
    var file = new File(byteArrays, tempfilename, { type: contentType });
    return file;
}

function dataURLToBlob(dataURL) {
    var BASE64_MARKER = ';base64,';
    if (dataURL.indexOf(BASE64_MARKER) == -1) {
        var parts = dataURL.split(',');
        var contentType = parts[0].split(':')[1];
        var raw = decodeURIComponent(parts[1]);
        return new Blob([raw], {type: contentType});
    }
    var parts = dataURL.split(BASE64_MARKER);
    var contentType = parts[0].split(':')[1];
    var raw = window.atob(parts[1]);
    var rawLength = raw.length;
    var uInt8Array = new Uint8Array(rawLength);
    for (var i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
    }
    return new Blob([uInt8Array], {type: contentType});
}

------

https://medium.com/@jsoverson/bypassing-captchas-with-headless-chrome-93f294518337

------ https://stackoverflow.com/questions/8022425/getting-blob-data-from-xhr-request

var xhr = new XMLHttpRequest();
xhr.open('get', 'doodle.png', true);

// Load the data directly as a Blob.
xhr.responseType = 'blob';

xhr.onload = () => {
  document.querySelector('#myimage').src = URL.createObjectURL(this.response);
};

xhr.send(); 

------

## STOP ALL JAVASCRIPT
page.evaluate('debugger;');
await page.setJavaScriptEnabled( false );
await page.evaluate('document.body.innerHTML = document.body.innerHTML')

------

var blob = ... // Your Blob capture from the stream
 
var tempVideoEl = document.createElement('video');
tempVideoEl.addEventListener('loadedmetadata', function() {
  // duration is now available here -- store it somewhere as you like
  console.log(tempVideoEl.duration);
  if(tempVideoEl.duration === Infinity) {
    console.log(0);
  }
});

tempVideoEl.src = window.URL.createObjectURL(blob);

------


```


```python

# 可以作为一个判断爬虫的特征
"""
    输入没有直接粘贴的方法，不能直接粘贴
        delay 并不能很好的模拟人类的输入
"""
```


ppt connect to existing Chrome browser
```bash

# 启动一个接受远程调试的Chrome，用户data放在指定目录
"/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9999 --no-first-run --no-default-browser-check --user-data-dir=/tmp/tmp1

# 从输出里找到远程连接的ws地址:
#     DevTools listening on ws://127.0.0.1:9999/devtools/browser/xxxx-xxxx
# 或者访问:
#     http://127.0.0.1:9999/json/version

# ppt 里使用 connect 方法
    const browser = await puppeteer.connect({
        browserWSEndpoint: 'ws://127.0.0.1:9999/devtools/browser/xxxx-xxxx',
    });

    # 获取 pages
    # 需要注意的是，pages的顺序并不按照 页面顺序 或 打开顺序，未确认
    const pages = await browser.pages();

# 参考链接:
    + https://github.com/puppeteer/puppeteer/issues/4579
        - Puppeteer can connect only to a browser target
    + https://medium.com/@jaredpotter1/connecting-puppeteer-to-existing-chrome-window-8a10828149e0
        - Connecting Puppeteer to Existing Chrome

```
