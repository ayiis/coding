"""
    超级无敌神速霹雳下载器
    - github
    - uuu9
    - epicwar3

    通常，在 nginx 中，range 和 content-encoding:gzip 是不可共存的

        - 因为 CE:gzip 是实时进行的，返回的大小未知，而 AR:bytes 要求服务器必须返回文件总大小 (content-length 和 1-1024/4096)
            1. github 表现是，第一次请求触发`打包`，`打包`完成后可以用range分批下载，需要多次下载才会触发，隔一段时间后失效
                一开始是 'Transfer-Encoding': 'chunked' && 'Accept-Ranges': 'bytes'，后来是 'Content-Range'，两次是不同的返回
            2. ayiis 表现是(错误)，只要设置了nginx的压缩，就无视 range
            3. sksedu 表现是(正确)，只要请求里有 range，就无视 content-encoding:gzip
"""
# import wrap_request
import argparse
import uuid
import core

parser = argparse.ArgumentParser()

parser.add_argument("target_url")
parser.add_argument("-m", "--max_thread", type=int, help="threads: maximum threads to download the file, default <8> threads")
parser.add_argument("-s", "--chunk_size", type=int, help="core setting: chunk size, default <10> KB")
parser.add_argument("-t", "--chunk_timeout", type=int, help="core setting: chunk timeout, default <8> seconds")
parser.add_argument("-o", "--output_file", type=str, metavar="FILE_NAME", help="save to file as FILE_NAME")

args = parser.parse_args()


def main():

    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    req_data = {
        "target_url": args.target_url,
        "file_name": args.output_file,
        "max_thread": args.max_thread,
        "chunk_timeout": args.chunk_timeout,
    }
    if not req_data["file_name"]:
        req_data["file_name"] = args.target_url.split("/")[-1]
        req_data["file_name"] = req_data["file_name"].split("?")[0]

    if not req_data["file_name"] or len(req_data["file_name"]) > 64:
        req_data["file_name"] = uuid.uuid4().hex

    print("target_url:", req_data["target_url"])
    print("save as file:", req_data["file_name"])
    print()

    db = core.DownloadBuilder(req_data)
    db.start_task()


if __name__ == "__main__":
    main()
