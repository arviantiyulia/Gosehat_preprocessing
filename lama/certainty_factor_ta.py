import re
from itertools import groupby
import psycopg2
from config import config

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from operator import itemgetter


# def create_connection():
#     """ create MySQL connection """
#         #
#         # conn = mysql.connector.connect(user='root', password='',
#         #                                host='127.0.0.1',
#         #                                database='gosehatcoba')
#
#     return conn

def create_connection():

    """ Connect to the PostgreSQL database server """
    params = config()
    conn = psycopg2.connect(**params)

    return conn


def get_stopword(stopwordList):
    """ get stopword data from CSV file """

    stopwords = []

    fp = open(stopwordList, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopwords.append(word)
        line = fp.readline()
    fp.close()

    return stopwords


def tokenizing(docs):
    """tokenizing process to split by space and take alphabet only"""

    text = docs.lower()
    text = re.sub('[^A-Za-z]+', ' ', text)
    token = text.split(" ")
    token = list(filter(None, token))

    return token


def filtering(docs, stopwords):
    """filtering process to delete word is not important"""

    res_token = [text for text in docs if text not in stopwords]
    return res_token


def stemming(doc):
    """stemming process to get basic word"""

    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    stem = []

    len_array = len(doc)
    for i in range(len_array):
        temp = doc[i]
        result_stem = stemmer.stem(temp)
        stem.append(result_stem)

    return stem


def get_symptoms(conn, inputs):
    """fungsi yang digunakan untuk mendapatkan id dari tabel gejala sesuai input user"""

    cursor = conn.cursor()
    rows = []
    arr_id = []

    # looping untuk mengambil data yang sesuai di database dengan inputan
    for i in inputs:
        cursor.execute("SELECT * FROM gejala WHERE nama_gejala LIKE '%" + i + "%'")
        rows.append(cursor.fetchall())
        # print(rows)

    # looping untuk menyimpan data yang lebih dari 2 gejala
    for row in rows:
        if len(row) > 1:
            temp_id = []
            count_arr = []
            for j in range(len(row)):
                temp_id.append([row[j][0], 0])

                temp_gejala = row[j][1]  # mengambil nama_gejala dari tuple
                split_gejala = temp_gejala.split(" ")  # memisahkan tiap kata dari tuple

                id_new = get_max_id(inputs, split_gejala, temp_id, count_arr)
            arr_id.append(id_new)

        elif len(row) == 1:
            temp_gejala2 = row[0][0]
            arr_id.append(temp_gejala2)

    id_gejala = list(set(arr_id))

    # print(id_gejala)

    return id_gejala


def get_max_id(inputs, split_gejala, temp_id, count_arr):
    """mendapatkan id yang tertinggi dari inputan user"""

    count = 0

    # mencari banyak kata dari input dengan data
    for gj in split_gejala:
        if gj in inputs:
            count += 1
    count_arr.append(count)

    # mengupdate data mana yang memiliki jumlah kata lebih banyak
    for ti in range(len(temp_id)):
        new_id = [temp_id[ti][0], count_arr[ti]]
        temp_id[ti] = new_id

    sorted_ti = sorted(temp_id)
    max_ti = max(sorted_ti, key=itemgetter(1))
    id_max = max_ti[0]
    # print("max_ti = ", max_ti)

    return id_max


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
    # print(arr_item)
    arr_item.sort(key=lambda tup: tup[0])
    for k, g in groupby(arr_item, key=lambda tup: tup[0]):
        groups_id.append(list(g))  # Store group iterator as a list
        uniquekeys.append(k)

    # print(groups_id)
    return groups_id, uniquekeys


def calculate_cf(arr, length):
    # print(arr[0], " + ( ", arr[1], " * ( 1 - ", arr[0], " )")
    res = arr[0] + (arr[1] * (1 - arr[0]))
    arr.pop(0)
    # print(arr)
    arr[0] = res
    if length == 2:
        return res

    return calculate_cf(arr, length - 1)


def certainty_calculate(id_dis):
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

def get_disease(conn, cf, id):

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


def get_cf(text):

    conn = create_connection()
    input = text
    stopwords = get_stopword('konjungsi.csv')
    contents = tokenizing(input)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    symptoms = get_symptoms(conn, stems)
    count_disease_id, uniq_id = get_id_disease(conn, symptoms)

    cf_calculate = certainty_calculate(count_disease_id)

    disease = get_disease(conn, cf_calculate, uniq_id)

    return disease


def main():
    conn = create_connection()
    text = "batuk"
    stopwords = get_stopword('konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    symptoms = get_symptoms(conn, stems)
    count_disease_id, uniq_id = get_id_disease(conn, symptoms)

    cf_calculate = certainty_calculate(count_disease_id)

    get_disease(conn, cf_calculate, uniq_id)


if __name__ == "__main__":
    # main()
    get_cf("batuk")
