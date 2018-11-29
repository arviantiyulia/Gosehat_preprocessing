from db import create_connection
from preprocessing import get_stopword, tokenizing, filtering, stemming
from sinonim import get_sinonim
from symptoms import get_symptoms
from disease_symptoms import get_id_disease
from lama.certainty_factor import certainty_calculate
from disease import get_disease


def get_cf(text):
    conn = create_connection()
    stopwords = get_stopword('file/konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    symptoms = get_symptoms(conn, sinonim)
    count_disease_id, uniq_id = get_id_disease(conn, symptoms)
    cf_calculate = certainty_calculate(count_disease_id)
    disease = get_disease(conn, cf_calculate, uniq_id)

    return disease


if __name__ == "__main__":
    get_cf("saya batuk darah, demam, flu dan pusing, lidah putih")
