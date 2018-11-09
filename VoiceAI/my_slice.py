#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'ayiis'
# create on 2018/11/07
"""
    切分目录下所有子目录里的wav文件
    用于切分喜马拉雅的儿童读英语的音频
"""

import sys
import numpy as np
import re
import ubelt
from pathlib import Path
import wave

reload(sys).setdefaultencoding("utf8")


class Slicer(object):
    """docstring for Slicer"""
    def __init__(self, arg):
        super(Slicer, self).__init__()
        self.arg = arg
        self.filename = arg["filename"]
        self.save_dir = arg["save_dir"]
        self.num_samples = 2048  # pyaudio内置缓冲大小
        self.sampling_rate = 16000  # 取样频率
        self.level = 1000  # 声音保存的阈值
        self.count_num = 20  # count_num个取样之内出现COUNT_NUM个大于LEVEL的取样则记录声音
        self.save_length = 10  # 声音记录的最小长度：save_length * num_samples 个取样
        self.channels = 1  # 声道，单声道
        self.sampwidth = 2  # 录音取样点
        self.save_buffer = []
        self.save_2_buffer = ""
        self.save_num = 0
        self.MAGIC_VALUE = 8

    def save_2_file(self, content):
        self.save_num += 1
        ubelt.ensuredir(self.save_dir)
        self.save_wav_path = "%s/%s.wav" % (self.save_dir, str(self.save_num).rjust(3, "0"))

        print "save to: %s" % self.save_wav_path
        wf = wave.open(self.save_wav_path, "wb")

        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth)
        wf.setframerate(self.sampling_rate)
        wf.writeframes(content)
        wf.close()

    def do(self):

        offset = []

        with open(self.filename) as fr:
            fr.seek(44)
            while True:
                string_audio_data = fr.read(self.num_samples)
                if not string_audio_data:
                    break
                self.save_2_buffer += string_audio_data
                audio_data = np.fromstring(string_audio_data, dtype=np.short)
                large_sample_count = np.sum(audio_data > self.level)
                if large_sample_count > self.count_num:
                    offset.append(1)
                else:
                    offset.append(0)

        # print offset
        # print len([x for x in offset if x == 1]), "/", len(offset)
        # c_count = [0] * 24

        cut_pos = [0]
        c0 = 0
        r_start = False
        for pos, i in enumerate(offset):
            if i == 0:
                c0 += 1
            else:
                # for k in range(c0+1):
                #     if k >= 24:
                #         continue
                #     c_count[k] += 1

                if c0 >= self.MAGIC_VALUE and r_start is True:
                    cut_pos.append(pos - c0 / 2)
                c0 = 0

                r_start = True

        # print "------"
        # print cut_pos[-1], len(offset)-1
        cut_pos.append(len(offset))

        # print "\t".join([str(x+1) for x in range(24)])
        # print "\t".join([str(x) for x in c_count])
        # print "cut at:"
        print cut_pos
        # print len(cut_pos)
        # print "cut result:"
        # print "end_pos:", cut_pos
        for i, val in enumerate(cut_pos):
            if i == 0:
                continue
            print offset[cut_pos[i-1]: val]
            self.save_2_file(self.save_2_buffer[cut_pos[i-1]*self.num_samples:val*self.num_samples])


source_path = "/home/1109"
target_path = "/home/1109_done/"


def main():

    for wav_dir in Path(source_path).glob("*"):
        for wav_file in Path(wav_dir).glob("*.wav"):
            wav_file_name = wav_file.name.lower().replace(".wav", "")
            wav_file_name = re.sub(r"[\d]+[.][\d]+", "", wav_file_name)
            wav_file_name = re.sub(r"raz[ -]?[a-z][ ]", "", wav_file_name)
            # fixed \W
            wav_file_name = re.sub(r"[\W]", "_", "%s" % wav_file_name)
            wav_file_name = wav_file_name.strip()
            new_file_path = "%s%s___%s" % (
                target_path,
                wav_dir.name.replace(" ", "").replace("-", "").lower().replace("raz", ""),
                wav_file_name
            )
            # new_file_path = re.sub(r"[\W]", "_", new_file_path)
            # print wav_dir, wav_file
            # print new_file_path
            ubelt.ensuredir(new_file_path + "/wav")
            ubelt.ensuredir(new_file_path + "/etc")

            # if "Fruit" not in "%s" % wav_file:
            #     continue

            sc = Slicer({
                "filename": "%s" % wav_file,
                # "filename": "/home/data2/18988369 - Raz d/Raz d maria's halloween.wav",
                # "filename": "/home/data/12338138 - RAZ-A/Fruit.wav",
                "save_dir": new_file_path + "/wav",
                "txt_path": new_file_path + "/etc/prompts-original",
            })
            sc.do()

            # exit(1)


if __name__ == "__main__":
    pass
    # main()
