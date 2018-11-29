from itertools import groupby

def get_id_disease(conn, symptoms):
    """fungsi yang digunakan untuk mendapatkan id penyakit sesuai gejala"""

    cursor = conn.cursor()
    rows = []
    arr_item = []
    groups_id = []
    uniquekeys = []

    # looping untuk mengambil data yang sesuai di database gejala_penyakit dengan id gejala
    for i in symptoms:
        cursor.execute(
            "SELECT penyakit.id_penyakit, gejala_penyakit.bobot FROM gejala_penyakit JOIN penyakit ON gejala_penyakit.id_penyakit=penyakit.id_penyakit WHERE id_gejala = " + str(
                i))
        rows.append(cursor.fetchall())

    # looping untuk menyimpan id penyakit berdasarkan gejala
    for row in rows:
        for item in row:
            arr_item.append(item)

    arr_item.sort(key=lambda tup: tup[0])
    for k, g in groupby(arr_item, key=lambda tup: tup[0]):
        groups_id.append(list(g))  # Store group iterator as a list
        uniquekeys.append(k)

    return groups_id, uniquekeys
