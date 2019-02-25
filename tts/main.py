#!/bin/env python
import json
import ubelt
import os
import q

ubelt.ensuredir("data/prompt-utt")
ubelt.ensuredir("data/prompt-lab")


with open("script/txt2.data", "r") as rf:
    result1 = json.loads(rf.read())

with open("data/file_id_list.scp", "w") as wf:
    wf.write(os.linesep.join(result1.keys()))
    wf.write(os.linesep)

with open("data/scheme_file", "w") as wf:
    for key, val in result1.items():
        wf.write("""(utt.save (utt.synth (Utterance Text "%s" )) "data/prompt-utt/%s.utt")""" % (val, key))
        wf.write(os.linesep)


with os.popen("script/festival -b data/scheme_file") as result2:
    res = result2.read()
    for line in res.splitlines():
        print(line)

for key in result1.keys():
    with os.popen("script/festival --script script/dumpfeats -eval script/extra_feats.scm -relation Segment -feats script/label.feats -output data/prompt-lab/tmp data/prompt-utt/%s.utt" % key) as result3:
        res = result3.read()
        for line in res.splitlines():
            print(line)

    with os.popen("gawk -f script/label-full.awk data/prompt-lab/tmp > data/prompt-lab/%s.lab" % key) as result4:
        res = result4.read()
        for line in res.splitlines():
            print(line)

    with os.popen("rm -f data/prompt-lab/tmp") as re:
        pass

    with open("data/prompt-lab/%s.lab" % key, "r") as rf:
        with open("data/prompt-lab/%s.none" % key, "w") as wf:
            for line0 in rf.readlines():
                if not line0.strip():
                    continue
                for i in range(5):
                    line = line0.strip().split(" ")
                    line = line[-1]
                    wf.write(line + "[%s]" % (i + 2))
                    wf.write(os.linesep)
