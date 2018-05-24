def merge(a, b):
    c = []
    h = j = 0
    while j < len(a) and h < len(b):
        if a[j] < b[h]:
            c.append(a[j])
            j += 1
        else:
            c.append(b[h])
            h += 1

    return c + b[h:] + a[j:]


def merge_sort(lists):
    if len(lists) <= 1:
        return lists
    middle = len(lists)/2
    left = merge_sort(lists[:middle])
    right = merge_sort(lists[middle:])
    return merge(left, right)


if __name__ == '__main__':
    a = [1,6,8,9,4,5,2,1,3,7,5,-5,-2,55,33,44,99,-9]
    print merge_sort(a)
    print merge_sort(a) == sorted(a)