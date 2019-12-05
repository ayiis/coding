import wrap_request
import argparse
import uuid

parser = argparse.ArgumentParser()

parser.add_argument("target_url")
parser.add_argument("-s", "--chunk_size", type=int)
parser.add_argument("-t", "--chunk_timeout", type=int)
parser.add_argument("-m", "--thread_max", type=int)
parser.add_argument("-o", "--output_file", type=str)

args = parser.parse_args()
wrap_request.CHUNK_SIZE = (args.chunk_size or 0) * 1024 or wrap_request.CHUNK_SIZE
wrap_request.CHUNK_TIMEOUT = args.chunk_timeout or (wrap_request.CHUNK_SIZE // (8 * wrap_request.KB))
wrap_request.HEAD_TIMEOUT = 8
wrap_request.THREAD_MAX = args.thread_max or wrap_request.THREAD_MAX
# print(args)


def main():

    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    req_data = {
        "target_url": args.target_url,
        "file_name": args.output_file or args.target_url.split("/")[-1],
    }
    if not req_data["file_name"] or len(req_data["file_name"]) > 64:
        req_data["file_name"] = uuid.uuid4().hex

    print("target_url:", req_data["target_url"])
    print("save as file:", req_data["file_name"])
    print()

    # print(req_data)

    # exit(1)
    w = wrap_request.Wrapper(req_data)
    w.start_task()


if __name__ == "__main__":
    main()
