#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from xlrd import open_workbook
import subprocess

try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except Exception:
    pass

"""
0. 需要安装 ffmpeg 4.1.1 以上版本
1. moviepy模块有 bug 导致某些播放器不能播放声音，所以不用
2. ffmpeg 的 filter_complex 里的 trim 和 loop 对 MP4 效果很差，切不到准确 Keyframe，所以不用
3. ffmpeg 使用 -vcodec copy，生成视频不需要重新编码，加快生成速度
4. ffmpeg 的 concat 对视频和音频是分开处理的
5. 从打点位置开始循环播放0.1s~0.5s视频，直接设为0.1s
6. 循环播放时，音量设为0，避免底噪影响
7. 如果 补间后总时长 < 视频时长 , 不做处理
"""

class UnicodeStreamFilter:

    def __init__(self, target):
        self.target = target
        self.encoding = "utf-8"
        self.errors = "replace"
        self.encode_to = self.target.encoding

    def write(self, s):
        if type(s) == str:
            try:
                s = s.decode("utf-8")
            except:
                pass
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)

if sys.stdout.encoding == "cp936":
    sys.stdout = UnicodeStreamFilter(sys.stdout)
    sys_decode = "gb2312"
else:
    sys_decode = "utf8"

cache_path = "tmp"
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

assert os.path.isdir(cache_path), "%s is not a valid DIR" % cache_path


def execute_command(command):
    # print("command:", command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    return [unicode(line, sys_decode) for line in (out or err).splitlines()]


def get_video_info(video_path, ffmpeg_path):
    video_info = {
        "duration": 0.0,
        "fps": 0.0,
        "hz": 0.0,
    }
    # read info
    console_output = execute_command("%s -i %s" % (ffmpeg_path, video_path))
    for line in console_output:
        # print(line)
        if "configuration" not in line:
            if "Duration: " in line:
                duration = line.split(",")[0].strip()
                duration = duration.split(" ")[1].strip()
                if len(duration.split(":")) != 3:
                    continue
                hh, mm, ss = duration.split(":")
                duration = (float(hh) * 60 + float(mm)) * 60 + float(ss)
                video_info["duration"] = duration

            if " Video: " in line and " fps, " in line:
                fps = next((x for x in line.split(",") if " fps" in x), "")
                fps = fps.replace("fps", "").strip()
                video_info["fps"] = round(float(fps))

            if " Audio: " in line and " Hz, " in line:
                hz = next((x for x in line.split(",") if " Hz" in x), "")
                hz = hz.replace("Hz", "").strip()
                video_info["hz"] = round(float(hz))

    # read key frame
    # res = execute_command("ffprobe -select_streams v -skip_frame nokey -show_frames %s" % video_path)

    # do match frames between 0.1s~0.5s
    return video_info


def main(video_path, time0, time1, ffmpeg_path="ffmpeg", cover=False):
    video_info = get_video_info(video_path, ffmpeg_path)
    print("video_info:", video_info)
    if time1 <= video_info["duration"]:
        return video_path, video_info["duration"], video_info["duration"]

    fill_time = 0.1     # set loop clips time = 0.1s

    # 切割原视频
    res = execute_command("%s -y -i %s -ss 0.0 -t %s %s\\tmp.cut_start.mp4" % (ffmpeg_path, video_path, time0, cache_path))
    # print(res)
    res = execute_command("%s -y -i %s -ss %s %s\\tmp.cut_end.mp4" % (ffmpeg_path, video_path, time0, cache_path))
    # print(res)
    res = execute_command("%s -y -i %s -ss %s -t %s -af volume=volume=0 %s\\tmp.cut_fill.mp4" % (ffmpeg_path, video_path, time0, fill_time, cache_path))
    # print(res)

    fill_video_info = get_video_info("%s\\tmp.cut_fill.mp4" % (cache_path), ffmpeg_path)
    print("fill_video_info:", fill_video_info)

    repeat_time = (time1 - video_info["duration"]) / max(fill_video_info["duration"], fill_time)
    repeat_time = int(repeat_time)
    print("repeat_time: %s" % repeat_time)

    # 重新拼装视频直到达到指定[总时间]
    with open("%s\\tmp.txt" % cache_path, "w") as wf:
        wf.write("file %s" % ("%s/tmp.cut_start.mp4" % cache_path))
        wf.write("\r\n")
        for i in range(repeat_time):
            wf.write("file %s" % ("%s/tmp.cut_fill.mp4" % cache_path))
            wf.write("\r\n")
        wf.write("file %s" % ("%s/tmp.cut_end.mp4" % cache_path))
        wf.write("\r\n")

    if cover:
        target_video_path = video_path
    else:
        target_video_path = "%s.result.mp4" % (video_path.replace(".mp4", ""))

    # print("target_video_path:", target_video_path)
    res = execute_command("%s -y -f concat -i %s\\tmp.txt -vcodec copy %s" % (ffmpeg_path, cache_path, target_video_path))
    result_video_info = get_video_info(target_video_path, ffmpeg_path)
    print("result_video_info:", result_video_info)

    return target_video_path, video_info["duration"], result_video_info["duration"]


if __name__ == "__main__":
    xlsx_name = u"视频补间配置表.xlsx"
    ffmpeg_path = "Python27\\ffmpeg.exe"
    if not os.path.exists(xlsx_name):
        print("找不到 %s" % xlsx_name)
        exit(1)

    res_message = []
    content = open_workbook(xlsx_name)
    sh = content.sheet_by_index(0)
    for rx in range(sh.nrows)[1:]:
        line = sh.row(rx)
        print(line[0].value, line[1].value, line[2].value)

        try:
            video_path = """%s.mp4""" % line[0].value
            assert os.path.exists(xlsx_name), "找不到文件 %s" % video_path
            assert line[1].value and line[2].value, "时间设置错误"

            try:
                time0 = float(line[1].value) / 1000
                time1 = float(line[2].value) / 1000
            except Exception:
                assert 1, "时间设置错误"

            assert 0 < time0 < time1, "时间设置错误"

            res = main(video_path, time0, time1, ffmpeg_path, cover=True)
            print("%s 处理完毕。打点在%s，补间后总时长%s。视频总时长由%s延长到%s\r\n" % (res[0], time0, time1, res[1], res[2]))

        except Exception as e:
            res_message.append("第%s行: %s" % (rx + 1, e))

    print("[所有视频都已经处理完毕]")
    if res_message:
        print("\r\n处理错误如下：")
        print("\r\n".join(res_message))
    else:
        print("\r\n全部视频处理成功")
    print("\r\n")
