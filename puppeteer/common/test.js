const m3u8 = require("./m3u8_downloader.js");

const test_header = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6,ja;q=0.5",
    "origin": "https://class.dxy.cn",
    "referer": "https://class.dxy.cn/clazz/course/3?sr=22&nm=sylxhy&pd=class",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
}

// https://class.dxy.cn/clazz/course/313
let ttt = "https://1252348479.vod2.myqcloud.com/92e0c654vodtransgzp1252348479/c5f76bd25285890785806231691/drm/voddrm.token.7226ad2f87a4e3595777c7ee024a24c9fb718e50030b360aa300f96f1a5ec9f236edcbb7d0c5512c53121c02c0c9bf90e06c498b090137f71eec12d3aa70cecb4189c39356ad0011b75a98ae180b03f022cc136113139abf84c92051252dfb02c77a88f46b1bbc907cade999f8dfae95318759e4a491727fbdc468eca7a9bb4bbe41a34214eb8713b9c0f2d55e7ed262aa8cf1d132c70061fe42a3f3a5a912a61210231f83fba414f79594938dad9c9e.v.f230.m3u8?t=5f20ec46&us=vaVGnpbBmD&sign=287675e68ed5ec7ffdbba7da412a4a35";

;(async () => {

    try {
        await m3u8.download_file_from_m3u8(ttt, test_header, "./log/");
    } catch(err) {
        console.log("main:", err);
        console.log(err);
    }

})();
