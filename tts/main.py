#!/usr/bin/env python
# -*- coding: utf-8 -*-
# - author: ayiis@2019/02/26
import os
import ubelt
import evaluation_tts


def create_label(text):

    TARGET = {"arctic_1": text}

    with open("data/file_id_list.scp", "w") as wf:
        wf.write(os.linesep.join(TARGET.keys()))
        wf.write(os.linesep)

    with open("data/scheme_file", "w") as wf:
        for key, val in TARGET.items():
            wf.write("""(utt.save (utt.synth (Utterance Text "%s" )) "data/%s.utt")""" % (val, key))
            wf.write(os.linesep)

    with os.popen("script/festival -b data/scheme_file") as re:
        pass

    for key in TARGET.keys():

        with os.popen("script/festival --script script/dumpfeats -eval script/extra_feats.scm -relation Segment -feats script/label.feats -output data/tmp data/%s.utt" % key) as re:
            pass

        with os.popen("gawk -f script/label-full.awk data/tmp > data/%s.lab" % key) as re:
            pass

        with os.popen("rm -f data/tmp") as re:
            pass

        with open("data/%s.lab" % key, "r") as rf:
            with open("data/%s.none" % key, "w") as wf:
                for line in rf.readlines():
                    if not line.strip():
                        continue
                    wf.write(os.linesep.join(["%s[%s]" % (line.strip().split(" ")[-1], i + 2) for i in range(5)]))
                    wf.write(os.linesep)

                return "data/%s.none" % key


if __name__ == "__main__":
    ubelt.ensuredir("data")
    do_tts = evaluation_tts.init("./model/checkpoint_epoch50_Generator.pth", "./model/checkpoint_epoch100_Generator.pth", "./cmu_arctic_tts_order59")

    try:
        input = raw_input
    except NameError:
        pass

    while True:
        text = input("input a text to be tts: ")
        print("text:", text)
        re = create_label(text)
        do_tts(re, "./data/result.wav")
        os.popen("aplay ./data/result.wav")
