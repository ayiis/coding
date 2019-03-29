#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess

"""
0. 需要安装 ffmpeg 4.1.1 以上版本
1. moviepy模块有 bug 导致某些播放器不能播放声音，所以不用
2. ffmpeg 的 filter_complex 里的 trim 和 loop 对 MP4 效果很差，切不到准确 Keyframe，所以不用
3. ffmpeg 使用 -vcodec copy，生成视频不需要重新编码，加快生成速度
4. ffmpeg 的 concat 对视频和音频是分开处理的
5. 从打点位置开始循环播放0.1s~0.5s视频，直接设为0.1s
6. 循环播放时，音量设为0，避免底噪影响
"""

cache_path = "tmp"
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

assert os.path.isdir(cache_path), "%s is not a valid DIR" % cache_path


def execute_command(command):
    print("command:", command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    return [line.decode("utf8") for line in (out or err).splitlines()]


def get_video_info(video_path):
    video_info = {}
    # read info
    res = execute_command("ffmpeg -i %s" % video_path)
    for line in res:
        print(line)
        if "configuration" not in line:
            if "Duration: " in line:
                duration = line.split(",")[0].strip()
                duration = duration.split(" ")[1].strip()
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


def main(video_path, time0, time1):
    video_info = get_video_info(video_path)
    print("video_info:", video_info)

    fill_time = 0.1     # set loop clips time = 0.1s

    # 切割原视频
    res = execute_command("ffmpeg -y -i %s -ss 0.0 -t %s %s/tmp.cut_start.mp4" % (video_path, time0, cache_path))
    print(res)
    res = execute_command("ffmpeg -y -i %s -ss %s %s/tmp.cut_end.mp4" % (video_path, time0, cache_path))
    print(res)
    res = execute_command("ffmpeg -y -i %s -ss %s -t %s -af volume=volume=0 %s/tmp.cut_fill.mp4" % (video_path, time0, fill_time, cache_path))
    print(res)

    fill_video_info = get_video_info("%s/tmp.cut_fill.mp4" % (cache_path))
    print("fill_video_info:", fill_video_info)

    repeat_time = (time1 - video_info["duration"]) / fill_video_info["duration"]
    print("repeat_time: %s" % repeat_time)

    # 重新拼装视频直到达到指定[总时间]
    with open("%s/tmp.txt" % cache_path, "w") as wf:
        wf.write("file %s" % ("tmp.cut_start.mp4"))
        wf.write("\r\n")
        for i in range(int(repeat_time)):
            wf.write("file %s" % ("tmp.cut_fill.mp4"))
            wf.write("\r\n")
        wf.write("file %s" % ("tmp.cut_end.mp4"))
        wf.write("\r\n")

    print("video_path:", video_path)
    res = execute_command("ffmpeg -y -f concat -i %s/tmp.txt -vcodec copy %s.result.mp4" % (cache_path, video_path.replace(".mp4", "")))
    for line in res:
        print(line)


if __name__ == "__main__":

    # 输入
    # video_path = "C:\\Users\\Administrator\\Desktop\\workspace\\2019-03\\do\\mine.mp4"
    # time0 = 3.0     # [打点时间]
    # time1 = 10.0    # [总时间]

    # video_path = """\"C:\\Users\\Administrator\\Desktop\\workspace\\2019-03\\do\\zzz (1).mp4\""""
    # time0 = 7.5     # [打点时间]
    # time1 = 11.0    # [总时间]

    video_path = """/mine/github/coding/image/data/mine.mp4"""
    time0 = 3.5     # [打点时间]
    time1 = 11.0    # [总时间]
    main(video_path, time0, time1)
