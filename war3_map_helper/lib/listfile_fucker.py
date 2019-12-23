import q


def test():
    args = {
        "target_path": "/Volumes/h/war3work/raw/(listfile)",
    }
    with open(args["target_path"], "r") as rf:
        contents = rf.readlines()
        contents = [line.strip().lower() for line in contents]

    print("raw len is :", len(contents))
    print("set len is :", len(set(contents)))


if __name__ == "__main__":
    test()
