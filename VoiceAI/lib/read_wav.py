#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2019/03/07
"""
    可视化音频文件内的各种信息
"""
import q
import re
import struct
import pretty_table


def read_next_chunk_header(chunk_handler, name_size=4, chunk_data_size=4):

    chunk_name = chunk_handler.read(name_size)
    chunk_size = chunk_handler.read(chunk_data_size)
    if not chunk_name or not chunk_size:
        raise EOFError

    return chunk_name, struct.unpack("<L", chunk_size)[0]


def read_chunk_of(chunk_type, chunk_handler, chunk_size):

    if chunk_type == "fmt ":
        """ https://sites.google.com/site/musicgapi/technical-documents/wav-file-format#fmt
            Size    Description
            2   Compression code 固定编码格式 1==PCM/uncompressed
            2   Number of channels  1==单声道, 2==立体声, 采样声道数
            4   Sample rate 16000 每秒采样频率
            4x  Average bytes per second 每秒的字节数 ==> AvgBytesPerSec = SampleRate * BlockAlign
            2x  Block align 每个采样切片的字节数 ==> BlockAlign = SignificantBitsPerSample / 8 * NumChannels
            2   Significant bits per sample 16位宽 == 2字节, 每个采样占用的位数, a multiple of 8, 1byte = 8bits
            即 内容长度 == 每秒采样频率 * 采样声道数 * (每个采样占用的位数 / 8)
        """
        return struct.unpack("<HHiiHH", chunk_handler.read(chunk_size))

    elif chunk_type == "data":
        return chunk_handler.read(chunk_handler.tell() + chunk_size)

    else:
        return struct.unpack("<%ss" % chunk_size, chunk_handler.read(chunk_size))


def do(wav_path):

    res = {
        "riff_len": 0,
        "fmt": [],
        "data": "",
        "data_len": 0,
        "text": [],
        "duration": 0,
    }
    with open(wav_path, "rb") as file_handler:

        chunk_header, chunk_size = read_next_chunk_header(file_handler)
        assert chunk_header == b"RIFF", "file does not start with RIFF id"
        assert chunk_size >= 36, "RIFF data size illegal"

        res["riff_len"] = chunk_size

        header_wave = file_handler.read(4)
        assert header_wave == b"WAVE", "not a WAVE file"

        chunk_header, header_wave = chunk_header.decode("utf8"), header_wave.decode("utf8")
        print(pretty_table.construct_a_line(zip((4, 4, 4), (chunk_header, chunk_size, header_wave))))

        while True:
            """ RIFF里的每一个CHUNK都满足以下格式：
                Size    Description
                4   Chunk ID
                4   Chunk Data Size
                ...Chunk Data Bytes...
            """
            try:
                chunk_name, chunk_size = read_next_chunk_header(file_handler)
            except EOFError:
                print("[ END OF FILE ]")
                break

            if chunk_name == b"fmt ":
                assert chunk_size == 16, "chunk_size %s of `fmt ` is illegal" % chunk_size
                fmt_data = read_chunk_of("fmt ", file_handler, chunk_size)
                res["fmt"] = {
                    "compression_code": fmt_data[0],
                    "channels": fmt_data[1],
                    "sample_rate": fmt_data[2],
                    # "avg_bytes_per_sec": fmt_data[3],   # == sample_rate * block_align, to easily calc duration
                    # "block_align": fmt_data[4],         # == sample_width / 8 * channels
                    "sample_width": fmt_data[5],
                }
                print(pretty_table.construct_a_line(zip((4, 4, 2, 2, 4, 4, 2, 2), ("fmt ", chunk_size) + fmt_data)))

            elif chunk_name == b"data":
                wav_data = read_chunk_of("data", file_handler, chunk_size)
                res["data"], res["data_len"] = wav_data, chunk_size
                res["duration"] = chunk_size / (res["fmt"]["sample_rate"] * res["fmt"]["channels"] * (res["fmt"]["sample_width"] / 8))
                print(pretty_table.construct_a_line(zip((4, 4, 8), ("data", chunk_size, "..."))))

            elif True or chunk_name == b"LIST":
                text_data = read_chunk_of("text", file_handler, chunk_size)
                text_data = re.sub(br"[\x00-\x1F\x7F]", b" ", text_data[0]).decode("utf8")
                res["text"].append(text_data)
                print(pretty_table.construct_a_line(zip((4, 4, chunk_size), ("LIST", chunk_size, text_data))))

    return res


if __name__ == "__main__":
    res = do("../000.wav")
    res["data"] = "..."
    print("res:", res)
