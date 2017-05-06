# -*- coding: utf-8 -*-


def loadDicts(senti_dpath="./lexicon/senti_dict.txt",
              fanzhuan_dpath="./lexicon/fanzhuan_dict.txt",
              degree_dpath="./lexicon/degree_dict.txt",
              dongtai_dpath="./lexicon/dongtai_dict.txt"):
    sentiDict = dict()
    degreeDict = dict()
    fanzhuanDict = dict()
    dongtaiDict = dict()

    inp_s = open(senti_dpath)

    for item in inp_s:
        i = item.strip().split(" ")
        try:
            sentiDict[i[0]] = float(i[1])
        except BaseException:
            print item

    inp_s.close()

    inp_d = open(degree_dpath)

    for item in inp_d:
        i = item.strip().split(" ")
        degreeDict[i[0]] = float(i[1])

    inp_d.close()

    inp_f = open(fanzhuan_dpath)

    for item in inp_f:
        fanzhuanDict[item.strip()] = -1

    inp_f.close()

    inp_t = open(dongtai_dpath)

    for item in inp_t:
        i = item.strip().split(" ")
        dongtaiDict[i[0]] = float(i[1])

    inp_t.close()

    return sentiDict, degreeDict, fanzhuanDict, dongtaiDict
