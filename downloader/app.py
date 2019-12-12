# import wrap_request
import argparse
import uuid
import core

parser = argparse.ArgumentParser()

parser.add_argument("target_url")
parser.add_argument("-s", "--chunk_size", type=int)
parser.add_argument("-t", "--chunk_timeout", type=int)
parser.add_argument("-m", "--max_thread", type=int)
parser.add_argument("-o", "--output_file", type=str)

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
