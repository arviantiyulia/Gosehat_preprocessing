import csv
from db import create_connection

def open_csv():
    """
    fungsi digunakan untuk membaca file csv
    @:param gejala(list):digunakan untuk menyimpan hasil baca file csv tiap baris nya
    @:return list: hasil dari tiap baris dari file csv
    """
    gejala = []

    with open('file/gejala_penyakit.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile, delimiter=';')
        #looping tiap baris dari file csv
        for r in read_data:
            gejala.append(r)
    print(gejala)
    return gejala

def import_gejala(conn, gj):
    """
    fungsi ini digunakan untuk menginputkan data hasil dari cvs kedalam database
    :param conn: koneksi ke database
    :param gj: array yang berisi data hasil csv
    :return: list hasil dari gejala
    """
    cursor = conn.cursor()

    for g in gj:
        print(g[0])
        cursor.execute("INSERT INTO gejala(nama_gejala) VALUES('"+g[0]+"')")
        conn.commit()
    return g

def import_penyakit(conn, gj):
    """
    fungsi ini digunakan untuk menginputkan data hasil dari cvs kedalam database
    :param conn: koneksi ke database
    :param gj: array yang berisi data hasil csv
    :return: list hasil dari gejala
    """
    cursor = conn.cursor()

    for g in gj:
        print(g[0])
        cursor.execute("INSERT INTO penyakit(nama_penyakit) VALUES('"+g[0]+"')")
        conn.commit()
    return g

def import_gejala_penyakit(conn, gp):

    cursor = conn.cursor()
    penyakit_gejala = []

    # for idx_gp in range(len(gp)):
    #     len_gp = len(gp[idx_gp])
    #     penyakit = gp[idx_gp][0]
    #
    #     gejala = gp[idx_gp][1:len_gp]
    #
    #     penyakit_gejala.append([penyakit,gejala])
    #
    # print(penyakit_gejala)
    for pg in gp:
        # for g in daftar_gejala:
        #     cursor.execute("INSERT INTO gejala_penyakit(id_penyakit, id_gejala) VALUES('"+penyakit+"','"+g+"')")
        #     conn.commit()
        cursor.execute("INSERT INTO gejala_penyakit(id_penyakit, id_gejala, bobot) VALUES('"+pg[0]+"','"+pg[1]+"','"+pg[2]+"')")
        conn.commit()

    return pg


def main():
    conn = create_connection()
    gj = open_csv()
    # import_gejala(conn,gj)
    # import_penyakit(conn, gj)
    import_gejala_penyakit(conn, gj)

if __name__ == "__main__":
    main()