def bound_value(lower, val, higher):
    return min(max(val, lower), higher)


def print_rect_info(rect):
    print(rect.x(), rect.y(), rect.width(), rect.height())
