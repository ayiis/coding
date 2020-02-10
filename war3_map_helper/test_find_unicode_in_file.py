import q
import re

rre = r"[~½§äö\u4e00-\u9fa5|a-z0-9|\ -\}\r\n\a\d\t|\u3002|\uff1f|\uff01|\uff0c|\u3001|\uff1b|\uff1a|\u201c|\u201d|\u2018|\u2019|\uff08|\uff09|\u300a|\u300b|\u3008|\u3009|\u3010|\u3011|\u300e|\u300f|\u300c|\u300d|\ufe43|\ufe44|\u3014|\u3015|\u2026|\u2014|\uff5e|\ufe4f|\uffe5|\ ]+"

"""
¨æ§½％·ä~ö
\ufeff \u200b
"""


def main(arg):
    with open(arg["file_path"], "r") as rf:
        contents = rf.readlines()

    with open(arg["file_path_out"], "w") as wf:
        for lineno, rawline in enumerate(contents):
            line = rawline.split("\x00")[-1]
            if re.match(r"^[¨æ§½％·ä~ö\u4e00-\u9fa5|a-z0-9|\ -\}\r\n\a\d\t|\u3002|\uff1f|\uff01|\uff0c|\u3001|\uff1b|\uff1a|\u201c|\u201d|\u2018|\u2019|\uff08|\uff09|\u300a|\u300b|\u3008|\u3009|\u3010|\u3011|\u300e|\u300f|\u300c|\u300d|\ufe43|\ufe44|\u3014|\u3015|\u2026|\u2014|\ ]+$", line, flags=re.I):
                pass
            else:
                print("line:", lineno, repr(re.sub(rre, "", line, re.I)))
                print(repr(re.sub(r"[\0\u200b]+", "", line, flags=re.I)))

            wf.write(re.sub(r"[\u200b¨æ§½％·ä~ö]+", "", rawline, flags=re.I))


if __name__ == "__main__":
    main({
        "file_path": "/mine/war3work/The-Chosen-Ones-1.0_x/map/war3campaign.wts",
        "file_path_out": "/mine/war3work/The-Chosen-Ones-1.0_x/map/war3campaign.wts.out",
        # "file_path": "./data/dict_base.en-zh.log",
        # "file_path_out": "./data/dict_base.en-zh.log.out",
    })


