import csv

def get_sinonim(inputs):
    """
    fungsi ini digunakan untuk mencari sinonim dari gejala yang didapat dari input user
    :param inputs: inputan user berupa gejala
    :return: list sin_input yang berisi daftar gejala yang baru dari hasil sinonim
    """
    sinonims = []
    sin_inputs = []

    with open('file/sinonim.csv', 'r') as csvfile:
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

    return sin_inputs
