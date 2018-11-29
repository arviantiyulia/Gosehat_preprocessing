import re
import mysql.connector
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from operator import itemgetter
from collections import Counter
import psycopg2
from db import config
import csv


# def create_connection():
#     """ create MySQL connection """
#
#     conn = mysql.connector.connect(user='root', password='',
#                                    host='127.0.0.1',
#                                    database='gosehat')
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

def get_sinonim(inputs):

    sinonims = []
    sin_inputs = []

    with open('sinonim.file', 'r') as csvfile:
        read_data = csv.reader(csvfile)
        for r in read_data:
            sinonims.append(r)


    for input in inputs:
        found = False
        for index in range(len(sinonims)):
            if input==sinonims[index][1]:
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

    # looping untuk menyimpan data yang lebih dari 2 gejala
    for row in rows:
        if len(row) > 1:
            temp_id = []
            count_arr = []
            for j in range(len(row)):
                temp_id.append([row[j][0], 0, row[j][1]])

                temp_gejala = row[j][1]  # mengambil nama_gejala dari tuple
                split_gejala = temp_gejala.split(" ")  # memisahkan tiap kata dari tuple

                id_new = get_max_id(inputs, split_gejala, temp_id, count_arr)
            arr_id.append(id_new)

        elif len(row) == 1:
            temp_gejala2 = row[0][0]
            arr_id.append(temp_gejala2)

    id_gejala = list(set(arr_id))

    return id_gejala


def get_max_id(inputs, split_gejala, temp_id, count_arr):
    """mendapatkan id yang tertinggi dari inputan user"""

    count = 0
    temp_max_count = []

    # mencari banyak kata dari input dengan data
    for gj in split_gejala:
        if gj in inputs:
            count += 1
    count_arr.append(count)

    # mengupdate data mana yang memiliki jumlah kata lebih banyak
    for ti in range(len(temp_id)):
        new_id = [temp_id[ti][0], count_arr[ti], temp_id[ti][2]]
        temp_id[ti] = new_id

    sorted_ti = sorted(temp_id)
    max_ti = max(sorted_ti, key=itemgetter(1))
    max_count = max_ti[1]

    for sort in sorted_ti:
        if sort[1] == max_count:
            # print(sort)
            temp_max_count.append(sort)

    min_item = 1000
    id_min_count = 0

    # looping digunakan untuk mencari gejala yang jumalh katanya paling sedikit
    for len_count in range(len(temp_max_count)):
        if len(temp_max_count[len_count][2].split()) < min_item:
            min_item = len(temp_max_count[len_count][2].split())
            id_min_count = temp_id[len_count][0]

    # print("temp_max = ", temp_max_count)
    id_max = id_min_count
    # print(id_max)

    # print("max_count = ", max_count)
    # print("sorted_ti = ", sorted_ti)
    # print("max_ti = ", max_ti)

    return id_max


def get_id_disease(conn, symptoms):
    """fungsi yang digunakan untuk mendapatkan id penyakit sesuai gejala"""

    cursor = conn.cursor()
    rows = []
    arr_item = []

    # looping untuk mengambil data yang sesuai di database gejala_penyakit dengan id gejala
    for i in symptoms:
        cursor.execute(
            "SELECT penyakit.id_penyakit FROM gejala_penyakit JOIN penyakit ON gejala_penyakit.id_penyakit=penyakit.id_penyakit WHERE id_gejala = " + str(
                i))
        rows.append(cursor.fetchall())

    # looping untuk menyimpan id penyakit berdasarkan gejala
    for row in rows:
        for item in row:
            arr_item.append(item[0])

    # digunakan untuk menghitung banyak id penyakit
    count_item = Counter(arr_item)

    return count_item


def count_highest_disease(conn, count_id):
    """fungsi untuk menghitung sistem pakar dengan id penyakit"""

    counts = []
    temp_id_penyakit = []
    jumlah_penyakit = []
    max_item = 0
    id_disease = 0

    count_penyakit = count_id_disease(conn, count_id, counts, temp_id_penyakit)

    # looping untuk menghitung sistem pakar antara id inputan dengan jumlah di database
    for cp in range(len(counts)):
        jumlah_penyakit.append((counts[cp] / count_penyakit[cp]) * 100)

    # looping untuk mencari id mana yang memiliki nilai paling banyak dari perhitungan diatas
    for jp in range(len(jumlah_penyakit)):
        if jumlah_penyakit[jp] > max_item:
            max_item = jumlah_penyakit[jp]
            id_disease = temp_id_penyakit[jp]

    print('jumlah perhitungan adalah ', max_item)
    print('id nya adalah ', id_disease)
    return id_disease


def count_id_disease(conn, count_id, counts, temp_id_penyakit):
    """fungsi untuk menghitung banyak id penyakit di database"""

    rows_count = []
    count_penyakit = []
    cursor = conn.cursor()

    # digunakan untuk menghitung banyaknya jumlah id penyakit yang didapat sebelumnya di database
    for id_dis, count in count_id.items():
        # print(id_dis)
        cursor.execute("SELECT COUNT(*) FROM gejala_penyakit WHERE id_penyakit = " + str(id_dis))
        rows_count.append(cursor.fetchone())
        counts.append(count)  # menampung jumlah id penyakit
        temp_id_penyakit.append(id_dis)  # menampung id penyakit sementara

    # digunakan untuk menampung hasil jumlah id di database
    for rw in rows_count:
        count_penyakit.append(rw[0])

    return count_penyakit


def get_disease(conn, id_disease):
    """fungsi untuk get disease sesuai id tertinggi"""

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_disease))
    disease = cursor.fetchall()

    return disease


def main():

    conn = create_connection()
    text = "saya merasa lelah, sakit tenggorokan, flu, batuk. kira-kira saya kenapa ?"
    stopwords = get_stopword('konjungsi.file')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    symptoms = get_symptoms(conn, sinonim)
    count_disease_id = get_id_disease(conn, symptoms)
    id_disease = count_highest_disease(conn, count_disease_id)
    disease = get_disease(conn, id_disease)
    print(disease)

if __name__ == "__main__":
    main()
