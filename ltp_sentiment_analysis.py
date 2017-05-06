# -*- coding: utf-8 -*-
from ltp_util import LTPUtil
from dict_util import loadDicts
from ltp_tree import LTPTree

ltpUtil = LTPUtil()
sentiDict, degreeDict, fanzhuanDict, dongtaiDict = loadDicts()


def calPolarity(in_string):
    global ltpUtil
    global sentiDict
    global degreeDict
    global fanzhuanDict
    global dongtaiDict

    in_string = in_string.encode('utf8')

    words = ltpUtil.Segmentor(in_string)
    postags = ltpUtil.Postagger(words)
    arcs = ltpUtil.Parser(words, postags)

    hx_idnex = -1

    for i in range(len(arcs)):
        if arcs[i].head == 0:
            hx_idnex = i + 1

    senti = sentiDict.get(words[hx_idnex - 1], 0.0)
    degree = degreeDict.get(words[hx_idnex - 1], 0.0)
    fanzhuan = fanzhuanDict.get(words[hx_idnex - 1], 0.0)
    root = LTPTree(hx_idnex,
                   'HED',
                   0,
                   postags[hx_idnex - 1],
                   words[hx_idnex - 1],
                   senti,
                   senti,
                   degree,
                   fanzhuan)

    for i in range(len(arcs)):
        act_index = i + 1
        if act_index != hx_idnex:
            senti = sentiDict.get(words[i], 0.0)
            degree = degreeDict.get(words[i], 0.0)
            fanzhuan = fanzhuanDict.get(words[i], 0.0)
            p_tree = LTPTree(
                act_index,
                arcs[i].relation,
                arcs[i].head,
                postags[i],
                words[i],
                senti,
                senti,
                degree,
                fanzhuan)
            # print p_tree.toString()
            root.addChild(p_tree)

    processADV(root)
    processCMP(root)
    processATT(root)
    processSBV(root)
    processVOB(root)

    total = 0.0
    for i in range(root.getLIndex(), root.getRIndex() + 1):
        total += root.find(i).root.polarity

    return normalize(total)


def processADV(root):
    for i in range(root.getLIndex(), root.getRIndex() + 1):
        node = root.find(i).root
        node_head_index = node.head
        if node.relation == "ADV":
            node_head = root.find(node_head_index).root
            if node.degree != 0.0 and node_head.polarity != 0.0:
                node_head.polarity = node.degree * node_head.polarity
            elif node.degree != 0.0 and node_head.degree != 0.0:
                node_head.degree = node.degree * node_head.degree
            elif node.fanzhuan == -1 and node_head.polarity != 0.0:
                node_head.polarity = -1.0 * node_head.polarity
            elif node.context == "不" and node_head.context == "是" or \
                    node_head.context == "会" or node_head.context == "能" or \
                    node_head.context == "可以" or node_head.context == "应该":
                node_head.degree = -1.0


def processCMP(root):
    for i in range(root.getLIndex(), root.getRIndex() + 1):
        node = root.find(i).root
        node_head_index = node.head
        if node.relation == "CMP":
            node_head = root.find(node_head_index).root
            cmp_context = node_head.context + node.context
            if sentiDict.get(cmp_context, 0.0) != 0.0:
                node_head.polarity = sentiDict.get(cmp_context, 0.0)
            elif node.degree != 0.0 and node_head.polarity != 0.0:
                node_head.polarity = node.degree * node_head.polarity
            elif node.degree != 0.0 and node_head.degree != 0.0:
                node_head.degree = node.degree * node_head.degree
            elif node.fanzhuan == -1 and node_head.degree != 0.0:
                node_head.polarity = -1 * node_head.polarity


def processATT(root):
    for i in range(root.getLIndex(), root.getRIndex() + 1):
        node = root.find(i).root
        node_head_index = node.head
        if node.relation == "ATT":
            node_head = root.find(node_head_index).root
            if node.degree != 0.0 and node_head.polarity != 0.0:
                node_head.polarity = node.degree * node_head.polarity
            elif node.polarity != 0.0 and node_head.polarity != 0.0:
                node_head.polarity = node.degree + node_head.polarity
            elif node.fanzhuan == -1 and node_head.polarity != 0.0:
                node_head.polarity = -1 * node_head.polarity


def processSBV(root):
    for i in range(root.getLIndex(), root.getRIndex() + 1):
        node = root.find(i).root
        node_head_index = node.head
        if node.relation == "SBV":
            node_head = root.find(node_head_index).root
            if dongtaiDict.get(
                    node_head.context) is not None and node.polarity != 0.0:
                node.polarity = dongtaiDict.get(
                    node_head.context) * node.polarity
            elif node_head.polarity != 0.0:
                if node.fanzhuan == -1:
                    node_head.polarity = -1 * node_head.polarity
                elif node.polarity != 0.0:
                    node.polarity = node.polarity + node_head.polarity


def processVOB(root):
    for i in range(root.getLIndex(), root.getRIndex() + 1):
        node = root.find(i).root
        node_head_index = node.head
        if node.relation == "VOB":
            node_head = root.find(node_head_index).root
            if node_head.senti != 0.0 and node.degree != 0.0 and node.polarity == 0.0:
                node_head.polarity = node_head.polarity * node.degree
            elif node_head.fanzhuan == -1 and node.polarity != 0.0:
                node.polarity = -1 * node.polarity


def normalize(value):
    middle = abs(value)
    if middle < 1.0:
        middle = 0.4 * middle
    elif middle > 1.0 and middle < 3.0:
        middle = 0.1 * middle + 0.3
    elif middle > 3.0 and middle < 6.0:
        middle = 0.2 * middle / 3 + 0.4
    elif middle > 6.0 and middle < 10.0:
        middle = 0.1 * middle / 4 + 0.65
    else:
        middle = 1 - 1 / middle

    result = 0
    if value < 0:
        result = -1 * middle
    else:
        result = middle
    return result
