import re
from itertools import groupby
import psycopg2
from config import config
import csv

import mysql.connector
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from operator import itemgetter
from collections import Counter


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
    # print(res_token)
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

    # print(stem)
    return stem


def get_sinonim(inputs):
    sinonims = []
    sin_inputs = []

    with open('sinonim.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile)
        for r in read_data:
            sinonims.append(r)

    for input in inputs:
        found = False
        for index in range(len(sinonims)):
            if input == sinonims[index][1]:
                found = True
                sin_inputs.append(sinonims[index][0])
                break
        if found == False:
            sin_inputs.append(input)
    # print(sin_inputs)
    return sin_inputs


def get_symptoms(conn, inputs):
    """fungsi yang digunakan untuk mendapatkan id dari tabel gejala sesuai input user"""

    cursor = conn.cursor()
    rows = []
    arr_id = []

    # looping untuk mengambil data yang sesuai di database dengan inputan
    for i in inputs:
        cursor.execute("SELECT * FROM gejala WHERE nama_gejala LIKE '%" + i + "%'")
        rows.append(cursor.fetchall())
    # print(len(rows))

    # looping untuk menyimpan data yang lebih dari 2 gejala
    for row in rows:
        if len(row) > 1:
            id_new = get_max_id(inputs, row)
            arr_id.append(id_new)

        elif len(row) == 1:
            temp_gejala2 = row[0][0]
            arr_id.append(temp_gejala2)

    id_gejala = list(set(arr_id))

    print(id_gejala)

    return id_gejala


def get_max_id(input, row):
    """mendapatkan id yang tertinggi dari inputan user"""
    gejala_arr = []
    temp_max_count = []
    min_item = 1000
    id_min_count = 0

    for r in row:
        gejala_new = [r[0], 0, r[1]]
        gejala_arr.append(gejala_new)

    #digunakan untuk melakukan stemming hasil gejala yang didapat dari database
    for gj in gejala_arr:
        gejala_split = gj[2].split(" ")
        gejala_stemm = stemming(gejala_split)
        gejala_join = ' '.join(gejala_stemm)
        gj[2] = gejala_join

    for gj in gejala_arr:
        count = 0
        for nama_gejala in gj[2].split(" "):
            if nama_gejala in input:
                count += 1;
        gj[1] = count

    max_ti = max(gejala_arr, key=itemgetter(1))
    max_count = max_ti[1]

    # mencari data yang memiliki jumlah kata yang sama dengan max
    for sort in gejala_arr:
        if sort[1] == max_count:
            temp_max_count.append(sort)

    # looping digunakan untuk mencari gejala yang jumalh katanya paling sedikit
    for len_count in range(len(temp_max_count)):
        if len(temp_max_count[len_count][2].split()) < min_item:
            min_item = len(temp_max_count[len_count][2].split())
            id_min_count = temp_max_count[len_count][0]

    id_max = id_min_count

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
        # print(i)
    # looping untuk menyimpan id penyakit berdasarkan gejala
    for row in rows:
        for item in row:
            arr_item.append(item)

    arr_item.sort(key=lambda tup: tup[0])
    for k, g in groupby(arr_item, key=lambda tup: tup[0]):
        groups_id.append(list(g))  # Store group iterator as a list
        uniquekeys.append(k)

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
        cf_kali = 0

        for j in range(len(id_dis[i])):
            cf_ur.append(1 * id_dis[i][j][1])

        if len(cf_ur) < 2:
            cf_old = cf_ur[0]

        elif len(cf_ur) >= 2:
            cf_old = calculate_cf(cf_ur, len(cf_ur))

        arr_cf.append(cf_old)
        # print("arr_cf = ", arr_cf)
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
    sinonim = get_sinonim(stems)
    symptoms = get_symptoms(conn, sinonim)
    count_disease_id, uniq_id = get_id_disease(conn, symptoms)

    cf_calculate = certainty_calculate(count_disease_id)

    disease = get_disease(conn, cf_calculate, uniq_id)

    return disease


def main():
    conn = create_connection()
    text = "saya merasa lelah, sakit tenggorokan, pilek, bercak merah di kulit. kira-kira saya kenapa ?"
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
    get_cf("saya batuk darah, demam, flu dan pusing, lidah berwarna putih")
