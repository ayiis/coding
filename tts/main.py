#!/bin/env python
import subprocess
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

result2 = subprocess.check_output([
    "script/festival",
    "-b",
    "data/scheme_file",
])
print("result2:", result2)


result3 = subprocess.check_output([
    "script/dumpfeats",
    "-eval",
    "script/extra_feats.scm",
    "-relation",
    "Segment",
    "-feats",
    "script/label.feats",
    "-output",
    "data/prompt-lab/tmp",
    "data/prompt-utt/arctic_1.utt",
])
print("result3:", result3)

with os.popen("gawk -f script/label-full.awk data/prompt-lab/tmp > data/prompt-lab/arctic_1.lab") as result4:
    res = result4.read()
    for line in res.splitlines():
        print(line)

with os.popen("rm -f data/prompt-lab/tmp") as re:
    pass
