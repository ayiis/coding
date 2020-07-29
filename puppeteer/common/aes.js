const fse = require("fs-extra");
const crypto = require("crypto");
const algorithm = "aes-128-cbc";
const tool = require("./tool.js");

module.exports = {
    encrypt_File: async function(bin_file, key, iv, aes_file) {
        key = this.wrap_key(key);
        iv = this.wrap_key(iv);
        const inputData = await fse.readFile(bin_file);
        const cipher = crypto.createCipheriv(algorithm, key, iv);
        const output = Buffer.concat([cipher.update(inputData), cipher.final()]);
        await fse.writeFile(aes_file, output);
    },
    decrypt_file: async function(aes_file, key, iv, bin_file) {
        key = this.wrap_key(key);
        iv = this.wrap_key(iv);
        const inputData = await fse.readFile(aes_file);
        const cipher = crypto.createDecipheriv(algorithm, key, iv);
        const output = Buffer.concat([cipher.update(inputData), cipher.final()]);
        await fse.writeFile(bin_file, output);
    },
    wrap_key: function(key) {
        const key_type = tool.get_type(key);
        if(key_type == "Uint8Array") {
            ;
        } else if(key_type == "String") {
            // 32 bytes hex string like "0x00000000000000000000000000000000"
            if(key.toLowerCase().startsWith("0x") && key.length == 32 + 2) {
                key = key.substr(2);
                key = new Buffer.from(key, "hex");
            } else {
                key = new Buffer.from(key);
            }
            fse.writeFileSync("bin_file.key", key);
        } else {
            throw "Nothing to do to convert to Uint8Array";
        }

        return key;
    },
};
