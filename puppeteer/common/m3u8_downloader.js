const https = require("https");
const http = require("http");
const fse = require("fs-extra");
const fs = require("fs");
const crypto = require("crypto");

const tool = require("./tool.js");
const aes = require("./aes.js");

async function http_get_data(target_url, headers, save_as_name) {
    return new Promise(async (resolve, reject) => {
        try {
            const scheme = tool.valid_http_type(target_url) ? https : http;
            const request = scheme.get(target_url, {
                "method": "GET",
                "timeout": 1000 * 60,
                "headers": headers
            }, (async response => {
                if(!!save_as_name) {
                    await fse.ensureFile(save_as_name);
                    const filestream = fse.createWriteStream(save_as_name);
                    filestream.on("finish", () => {
                        console.log("Saved:", save_as_name);
                        resolve();
                    });
                    response.pipe(filestream);
                } else {
                    let bin_data = [];
                    response.on("data", chunk => { bin_data.push(chunk); });
                    response.on("end", () => {
                        resolve(Buffer.concat(bin_data));
                    });
                }
            })).on("error", (err) => {
                reject(err);
            }).on("timeout", () => {
                // https://github.com/nodejs/node/issues/12005
                // timeout 事件需要主动触发行为
                request.abort();
            });
        } catch(err) {
            console.log("http_get_data:", err);
            reject(err);
        }
    });
}

async function download_file(target_url, headers, save_as_name) {
    return await http_get_data(target_url, headers, save_as_name);
}

async function get_url_text(target_url, headers) {
    return await http_get_data(target_url, headers);
}

async function join_to_one(filename_list, result_filename) {
    // 将所有媒体文件 写入到一个目标文件
    await fse.ensureFile(result_filename);
    await fse.writeFile(result_filename, "");

    console.log(`Writing ${filename_list.length} media files to ${result_filename}!`);

    // 组合所有的 媒体文件
    for(let i = 0 ; i < filename_list.length ; i++ ) {
        let filename = filename_list[i];
        let file_content = await fse.readFile(filename);
        await fse.appendFile(result_filename, file_content);
    }

}

async function download_file_from_m3u8(m3u8_url, headers, folder_name) {

    if(folder_name[folder_name.length - 1] !== "/") {
        folder_name = folder_name + "/";
    }

    const m3u8_save_path = `${folder_name}temp.m3u8`;

    let url_obj = new URL(m3u8_url);
    let base_path = `${url_obj.origin}${url_obj.pathname.substr(0, url_obj.pathname.lastIndexOf("/"))}`;

    // 失败重试，默认3次
    await tool.async_retry_until_times(async() => {
        return await download_file(m3u8_url, headers, m3u8_save_path);
    });

    console.log(`m3u8 saved to ${m3u8_save_path}!`);

    // 读取 m3u8 文件，过滤掉里面的注释 #
    let m3u8_contents = await fse.readFile(m3u8_save_path, "utf8");
    m3u8_contents = m3u8_contents.split("\n");

    console.log("m3u8 contents lines:", m3u8_contents.length);

    let filename_list = [];
    let file_index = 1;
    let x_method, x_key_uri, x_key, x_iv, encrypted;
    let prefix;
    let tmp_key_url;

    for(let i = 0; i < m3u8_contents.length; i++) {

        let content = m3u8_contents[i];
        if (!content.trim()) {
            continue;
        }
        // 处理 加密方式 的注释
        if(content.toLowerCase().startsWith("#ext-x-key:")) {
            let sss = content.split(",");
            if(sss.length == 3) {
                encrypted = true;
                x_method = sss[0].split("=")[1];
                x_key_uri = sss[1].substring(5, sss[1].length - 1);
                x_iv = sss[2].split("=")[1];

                // 如果 key 的 url 和之前的一样，直接返回之前的 key
                if(tmp_key_url == x_key_uri) {
                    console.log(`Using cached key..`);
                    continue;
                } else {
                    tmp_key_url = x_key_uri;
                }
                console.log(`Media files seems be encrypted..`);

                // 如果不是绝对路径
                if(tool.valid_http_type(x_key_uri) == -1) {
                    x_key_uri = `${base_path}/${x_key_uri}`;
                }

                // 请求 key 的 url，获取 key
                x_key = await tool.async_retry_until_times(async() => {
                    return await get_url_text(x_key_uri, headers);
                });

            } else {
                console.log(`[WARN] Key exists but not work: ${content}`);
                encrypted = false;
            }
        // 忽略其他类型的注释
        } else if(content && content.trim()[0] == "#") {
            continue;
        // 处理 媒体文件 链接
        } else {
            let resourse_url = content;
            if(tool.valid_http_type(resourse_url) == -1) {
                resourse_url = `${base_path}/${resourse_url}`;
            }
            console.log(`Working on: ${resourse_url}`);
            prefix = tool.last_item_of_array(resourse_url.split("?")[0].split("."));
            let filename = `${folder_name}${(file_index).toString().padStart(5, 0)}.${prefix}`;
            file_index = file_index + 1;

            // 下载 媒体文件
            await tool.async_retry_until_times(async() => {
                return await download_file(resourse_url, headers, filename);
            });

            // 直接解密 aes
            if(encrypted == true) {
                await aes.decrypt_file(filename, x_key, x_iv, filename);
            }
            filename_list.push(filename);
        }
    }

    // 命名为 result.*
    let result_filename = `${folder_name}result.${prefix}`;
    await join_to_one(filename_list, result_filename);
    
    console.log(`[Done] write to ${result_filename}!`);

    return result_filename;
}

module.exports = {
    "download_file_from_m3u8": download_file_from_m3u8,
}
