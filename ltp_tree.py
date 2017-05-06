# -*- coding: utf-8 -*-
from ltp_util import LTPUtil
from dict_util import loadDicts


class Node:
    def __init__(
            self,
            index,
            relation,
            head,
            postag,
            context,
            polarity,
            lchild=None,
            rchild=None,
            senti=0.0,
            degree=0.0,
            fanzhuan=0.0):
        self.index = index
        self.head = head
        self.relation = relation
        self.postag = postag
        self.context = context
        self.senti = senti
        self.degree = degree
        self.fanzhuan = fanzhuan
        self.polarity = polarity
        self.lindex = index
        self.rindex = index
        self.lchild = lchild
        self.rchild = rchild


class LTPTree:
    def __init__(
            self,
            index,
            relation,
            head,
            postag,
            context,
            polarity,
            senti,
            degree,
            fanzhuan):
        self.root = Node(
            index,
            relation,
            head,
            postag,
            context,
            polarity,
            senti=senti,
            degree=degree,
            fanzhuan=fanzhuan)

    def addChild(self, child_tree):
        if child_tree.root.index < self.root.index:
            if self.root.lindex > child_tree.root.lindex:
                self.root.lindex = child_tree.root.lindex
            if self.root.lchild is None:
                self.root.lchild = list()
                self.root.lchild.append(child_tree)
                #self.root.lindex = child_tree.root.lindex
            else:
                added_flag = False

                for iter in range(len(self.root.lchild))[::-1]:
                    if self.root.lchild[iter].root.head == child_tree.root.index:
                        sub_tree = self.root.lchild[iter]
                        child_tree.addChild(self.root.lchild[iter])
                        self.root.lchild.remove(sub_tree)
                if (child_tree.root.lchild is not None):
                    child_tree.root.lchild.sort(
                        lambda x, y: cmp(x.root.index, y.root.index))

                for iter in range(len(self.root.lchild)):
                    if child_tree.root.head == self.root.lchild[iter].root.index:
                        added_flag = True
                        self.root.lchild[iter].addChild(child_tree)
                    elif self.root.lchild[iter].inrange(child_tree.root.head):
                        added_flag = True
                        self.root.lchild[iter].addChild(child_tree)
                if not added_flag:
                    self.root.lchild.append(child_tree)
                self.root.lchild.sort(
                    lambda x, y: cmp(
                        x.root.index, y.root.index))

        else:
            if self.root.rindex < child_tree.root.rindex:
                self.root.rindex = child_tree.root.rindex
            if self.root.rchild is None:
                self.root.rchild = list()
                self.root.rchild.append(child_tree)
                #self.root.rindex = child_tree.root.rindex
            else:
                added_flag = False
                for iter in range(len(self.root.rchild))[::-1]:
                    if self.root.rchild[iter].root.head == child_tree.root.index:
                        sub_tree = self.root.rchild[iter]
                        child_tree.addChild(self.root.rchild[iter])
                        self.root.rchild.remove(sub_tree)
                # 如果出现顺序错误，可能要修改这里。
                if (child_tree.root.rchild is not None):
                    child_tree.root.rchild.sort(
                        lambda x, y: cmp(x.root.index, y.root.index))
                for iter in range(len(self.root.rchild)):
                    if self.root.rchild[iter].root.index == child_tree.root.head:
                        added_flag = True
                        self.root.rchild[iter].addChild(child_tree)
                    elif self.root.rchild[iter].inrange(child_tree.root.head):
                        added_flag = True
                        self.root.rchild[iter].addChild(child_tree)
                if not added_flag:
                    self.root.rchild.append(child_tree)
                self.root.rchild.sort(
                    lambda x, y: cmp(
                        x.root.index, y.root.index))

    def getLIndex(self):
        return self.root.lindex

    def getRIndex(self):
        return self.root.rindex

    def toString(self):
        return "====================\nhead: " + str(self.root.head) + "\nindex: " \
               + str(self.root.index) + "\nrelation: " + self.root.relation + "\npostage: " \
               + self.root.postag + "\ncontext: " + self.root.context + "\npolarity: " \
               + str(self.root.polarity) + "\nlindex: " + str(self.root.lindex) + "\nrindex: " \
               + str(self.root.rindex) + "\n====================\n"

    def find(self, index):
        if index < self.root.lindex or index > self.root.rindex:
            print "Error! Out of range!"
        if index == self.root.index:
            return self
        elif index < self.root.index:
            for tree in self.root.lchild:
                if tree.inrange(index):
                    return tree.find(index)
        else:
            for tree in self.root.rchild:
                if tree.inrange(index):
                    return tree.find(index)

    def inrange(self, index):
        return (self.root.lindex <= index and self.root.rindex >= index)


if __name__ == "__main__":
    ltpUtil = LTPUtil()

    s = "群众非常赞赏政府打击腐败的举措。"

    words = ltpUtil.Segmentor(s)
    postags = ltpUtil.Postagger(words)
    arcs = ltpUtil.Parser(words, postags)

    sentiDict, degreeDict, fanzhuanDict, dongtaiDict = loadDicts()

    hx_idnex = -1

    for i in range(len(arcs)):
        if arcs[i].head == 0:
            hx_idnex = i + 1

    # print hx_idnex
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
    # print root.toString()

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

        elif node.relation == "CMP":
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

        elif node.relation == "ATT":
            node_head = root.find(node_head_index).root
            if node.degree != 0.0 and node_head.polarity != 0.0:
                node_head.polarity = node.degree * node_head.polarity
            elif node.polarity != 0.0 and node_head.polarity != 0.0:
                node_head.polarity = node.degree + node_head.polarity
            elif node.fanzhuan == -1 and node_head.polarity != 0.0:
                node_head.polarity = -1 * node_head.polarity

        elif node.relation == "SBV":
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

        elif node.relation == "VOB":
            node_head = root.find(node_head_index).root
            if node_head.senti != 0.0 and node.degree != 0.0 and node.polarity == 0.0:
                node_head.polarity = node_head.polarity * node.degree
            elif node_head.fanzhuan == -1 and node.polarity != 0.0:
                node.polarity = -1 * node.polarity

    total = 0.0
    for i in range(root.getLIndex(), root.getRIndex() + 1):
        print root.find(i).toString()
        total += root.find(i).root.polarity

    print total
