import itertools


def union(a, b):
    x = min(a[0], b[0])
    y = min(a[1], b[1])
    w = max(a[0] + a[2], b[0] + b[2]) - x
    h = max(a[1] + a[3], b[1] + b[3]) - y
    return x, y, w, h


def intersection(a, b):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    w = min(a[0] + a[2], b[0] + b[2]) - x
    h = min(a[1] + a[3], b[1] + b[3]) - y
    if w < 0 or h < 0:
        return None
    return x, y, w, h


def combine_rectangles(boxes):
    if len(boxes) < 2:
        return boxes

    new_rectangles = []
    for box_a, box_b in itertools.combinations(boxes, 2):
        if intersection(box_a, box_b):
            new_rectangles.append(union(box_a, box_b))
        else:
            new_rectangles.append(box_a)
    return new_rectangles
