def get_disease(conn, cf, id):
    """mencari penyakit dari database sesuai id gejala maks yang didapat"""
    max_item = 0
    id_disease = 0
    cursor = conn.cursor()

    for len_cf in range(len(cf)):
        if cf[len_cf] > max_item:
            max_item = cf[len_cf]
            id_disease = id[len_cf]

    cursor.execute("SELECT nama_penyakit FROM penyakit WHERE id_penyakit = " + str(id_disease))
    disease = cursor.fetchall()

    print(disease)

    return disease
