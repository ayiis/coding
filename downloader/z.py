import q

def fff():
    packge = [0] * 8
    total = 12124142
    chunk = 1024
    already = 0

    while True:

        for i in range(8):
            packge[i] += min(chunk, total - already)
            already += packge[i]
            if already >= total:
                break
        else:
            continue

        break


import math
READ_CHUNK_SIZE = 3
MAX_TRUNK_SIZE = READ_CHUNK_SIZE * 2
THREAD = 8

"""
    先计算背包数量：

        1. 8¥ 以下按 1¥ 一个计算
        2. 8*1024¥ 以上，按 1024¥ 一个计算

"""


def do_cut(total_size):

    if total_size // READ_CHUNK_SIZE < THREAD:
        package_count = math.ceil(total_size / READ_CHUNK_SIZE)

    elif THREAD * MAX_TRUNK_SIZE < total_size:
        package_count = math.ceil(total_size / MAX_TRUNK_SIZE)

    else:
        package_count = THREAD

    bc1 = total_size // READ_CHUNK_SIZE
    pd1 = total_size % READ_CHUNK_SIZE

    bc2 = bc1 // package_count
    pd2 = bc1 % package_count

    result = []
    tmp_size = 0
    for i in range(package_count):
        pad = pd2 > i and READ_CHUNK_SIZE or 0
        if i == package_count - 1:
            pad += pd1
        end_size = tmp_size + bc2 * READ_CHUNK_SIZE + pad
        result.append((tmp_size, min(end_size, total_size)))
        tmp_size = end_size

    z = result
    z_list = [(z[i][1] - z[i][0]) for i in range(len(z))]
    if not (sum(z_list) == total_size):
        print(total_size, sum(z_list), total_size)
        q.d()

    return result


def main():
    for i in range(99):
        if i <= 2:
            continue

        # if i != 95:
        #     continue

        # if i <= 17:
        #     continue
        # if i < 8:
        #     continue

        # if i != 13:
        #     continue

        z = do_cut(i)
        print(i, len(z), z)
        z_list = [(z[i][1] - z[i][0]) for i in range(len(z))]
        print(", ".join([str(k) for k in z_list]))
        # print(sum(z_list))
        print()

        assert sum(z_list) == i, "Not right: %s != %s" % (sum(z_list), i)


if __name__ == "__main__":
    main()
