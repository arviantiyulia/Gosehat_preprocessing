import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


def get_stopword(stopwordList):
    """
    get stopword data from CSV file
    :param stopwordList: berisi file konjungsi.csv
    :return: list stopword berdasarkan file csv
    """

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
    """
    fungsi ini digunakan untuk memisahkan kalimat berdasarkan spasi dan tanda baca
    :param docs: inputan user
    :return: list token dari tiap kata dari inputan user
    """

    text = docs.lower()
    text = re.sub('[^A-Za-z]+', ' ', text)
    token = text.split(" ")
    token = list(filter(None, token))

    return token


def filtering(docs, stopwords):
    """
    fungsi ini digunakan untuk mengambil kata penting yang dibutuhkan yaitu gejala
    :param docs: inputan hasil tokenizing
    :param stopwords: list yang berisi kata konjungsi/kata yang tidak dibutuhkan
    :return: list res_token dari filtering input tokenizing dengan kata konjungsi
    """

    res_token = [text for text in docs if text not in stopwords]

    return res_token


def stemming(doc):
    """
    fungsi ini digunakan untuk mencari kata dasar berdasarkan gejala
    :param doc: inputan hasil filtering
    :return: list stem berisi kata dasar dari hasil filtering
    """

    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    stem = []

    len_array = len(doc)
    for i in range(len_array):
        temp = doc[i]
        result_stem = stemmer.stem(temp)
        stem.append(result_stem)

    return stem
