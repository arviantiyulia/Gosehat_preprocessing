import csv
import psycopg2
from config import config

def open_csv():
    gejala = []
    with open('gejala_penyakit.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile)
        for r in read_data:
            gejala.append(r)

    return gejala


def create_connection():
    """ Connect to the PostgreSQL database server """
    params = config()
    conn = psycopg2.connect(**params)

    return conn

def import_gejala(conn, gj):
    cursor = conn.cursor()

    for g in gj:
        cursor.execute("INSERT INTO gejala(nama_gejala) VALUES('"+g+"')")
        conn.commit()
    return g

def import_gejala_penyakit(conn, gp):

    cursor = conn.cursor()
    penyakit_gejala = []

    for idx_gp in range(len(gp)):
        len_gp = len(gp[idx_gp])
        penyakit = gp[idx_gp][0]

        gejala = gp[idx_gp][1:len_gp]

        penyakit_gejala.append([penyakit,gejala])

    print(penyakit_gejala)
    for pg in penyakit_gejala:
        for p in range(len(pg)):
            # print(pg[p])
            penyakit = pg[0]
            daftar_gejala = pg[1]
            for g in daftar_gejala:
                cursor.execute("INSERT INTO gejala_penyakit(id_penyakit, id_gejala) VALUES('"+penyakit+"','"+g+"')")
                conn.commit()

    return gejala, penyakit


def main():
    conn = create_connection()
    gj = open_csv()
    # import_gejala(conn,gj)
    import_gejala_penyakit(conn, gj)

if __name__ == "__main__":
    main()