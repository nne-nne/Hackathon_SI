def pixel_eq(pixel, value):
    if pixel[0] == value[0] and pixel[1] == value[1] and pixel[2] == value[2]:
        return True
    else:
        return False


def pixel_bcg(pixel):
    if pixel[0] == pixel[1] and pixel[1] == pixel[2]:
        return True
    else:
        return False
