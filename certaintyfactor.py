def calculate_cf(arr, length):
    """fungsi ini digunakan untuk looping hasil cf"""

    res = arr[0] + (arr[1] * (1 - arr[0]))
    arr.pop(0)
    arr[0] = res
    if length == 2:
        return res

    return calculate_cf(arr, length - 1)


def certainty_calculate(id_dis):
    """fungsi digunakan untuk menghitung id gejala dengan rumus certainty factor"""
    arr_cf = []

    for i in range(len(id_dis)):
        cf_ur = []
        cf_old = 0

        for j in range(len(id_dis[i])):
            cf_ur.append(1 * id_dis[i][j][1])

        if len(cf_ur) < 2:
            cf_old = cf_ur[0]

        elif len(cf_ur) >= 2:
            cf_old = calculate_cf(cf_ur, len(cf_ur))

        arr_cf.append(cf_old)
    return arr_cf
