import q
import re


def main(args):
    lineno = 0
    print_line = 0
    with open(args["fa"], "r") as ra:
        with open(args["fb"], "r") as rb:
            while True:
                la = ra.readline()
                lb = rb.readline()
                lineno += 1
                # if lineno < 65701:
                #     continue
                if not la and not lb:
                    print("[DONE]")
                    break
                la = la.strip()
                lb = lb.strip()
                if la != lb:
                    # # 无关
                    # if len(lb.encode("utf8")) > 900:
                    #     print("len > 999", len(lb.encode("utf8")))
                    #     print(lb)
                    #     q.d()
                    # continue
                    # if la.count("\"") == lb.count("\"") == 2:
                    #     pass
                    # else:
                    #     continue

                    # while True:
                    #     if not la or not lb:
                    #         break
                    #     if la[-1] == lb[-1]:
                    #         la = la[:-1]
                    #         lb = lb[:-1]
                    #     elif la[0] == lb[0]:
                    #         la = la[1:]
                    #         lb = lb[1:]
                    #     else:
                    #         break

                    # if re.match(r"^[a-z0-9\ \?\!]*$", la, flags=re.I) and re.match(r"^[a-z0-9\ \?\!\u4e00-\u9fa5\u3002|\uff1f|\uff01|\uff0c|\u3001|\uff1b|\uff1a|\u201c|\u201d|\u2018|\u2019|\uff08|\uff09|\u300a|\u300b|\u3008|\u3009|\u3010|\u3011|\u300e|\u300f|\u300c|\u300d|\ufe43|\ufe44|\u3014|\u3015|\u2026|\u2014|\uff5e|\ufe4f|\uffe5|\ ]+$", lb, flags=re.I):
                    #     continue
                    # else:
                    #     pass

                    if re.search(r"[\<\>]", la, flags=re.I):
                    # if re.search(r"[\{\}]", lb, flags=re.I):
                    # if re.search(r"[\[\]]", lb, flags=re.I):
                    # if re.search(r"[\(\)]", lb, flags=re.I):
                        pass
                    else:
                        continue

                    print("-" * 64, lineno, ":")
                    print(la)
                    print(lb)
                    print_line += 1
                    if print_line % 10 == 9:
                        q.d()
                        print("=" * 128)
                        print("=" * 128)


if __name__ == "__main__":
    main({
        "fa": "/mine/war3work/Daemonic Sword ORPG 6.79.bak/table/ability.ini",
        "fb": "/mine/war3work/Daemonic Sword ORPG 6.79/table/ability.ini.mta2.cache",
    })

