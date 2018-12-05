
import xml.etree.ElementTree as ET
import Const
import re
import os
from nltk.tokenize import word_tokenize
from collections import defaultdict
import pickle




def CleanSentence(text_origin):
    # filter all nonsense punctuation
    # alter into lowercase chars
    # replace some abbr with full text
    # replace some symbol with words, specifically @ $ &

    text = text_origin.lower()
    text = re.sub(r"[^A-Za-z0-9()@&$\''\`\\_\n]", " ", text)
    text = re.sub(r"\n", " ", text)

    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "can not ", text)
    text = re.sub(r"cannot", "can not ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)

    text = re.sub(r"\)", " ", text)
    text = re.sub(r"\(", " ", text)
    text = re.sub(r"\'", " ", text)

    text = text.replace('&', ' and')
    text = text.replace('@', ' at')
    text = text.replace('$', ' dollar')

    return text



class Doc:

    def __init__(self, path, filename, id):

        self.doc_id = id
        self.catchphrases = []  # inital version consists of sentences
        self.catchphrases_origin = []  # origin version consists of words
        self.catchphrases_clear = []  # clear version removes stop words
        self.sentences = []
        self.sentences_origin = []
        self.sentences_clear = []

        direc = Const.PathGenerator(path, filename)
        text = open(direc).read()
        # clear some typo in the .xml file
        text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", text)
        text = re.sub('"id=', 'id="', text)
        text = re.sub(u"&#?[\w]*;", u"\w", text)

        # phrase the .xml file using ElementTree
        tree = ET.fromstring(text)
        for item in tree:
            if item.tag == 'name':
                self.name = item.text
            if item.tag == 'AustLII':
                self.link = item.text
            if item.tag == 'catchphrases':
                for item2 in item:
                    self.catchphrases.append(item2.text)
            if item.tag == 'sentences':
                for item2 in item:
                    self.sentences.append(item2.text)

        # build origin version & clear version
        for sen in self.catchphrases:
            clean_sen = CleanSentence(sen)
            word_tokens = word_tokenize(clean_sen)
            filtered_words = [w for w in word_tokens if not w in Const.stop_words]
            self.catchphrases_origin.extend(word_tokens)
            self.catchphrases_clear.extend(filtered_words)
        # for sen in self.sentences:
        #     clean_sen = CleanSentence(sen)
        #     word_tokens = word_tokenize(clean_sen)
        #     filtered_words = [w for w in word_tokens if not w in Const.stop_words]
        #     self.sentences_origin.extend(word_tokens)
        #     self.sentences_clear.extend(filtered_words)



class DocList:

    doc_size = 0
    doc_list = []
    folder_path = ""

    def __init__(self, path):
        self.doc_size = 0
        self.folder_path = path
        file_list = os.listdir(self.folder_path)
        print(file_list)
        xml_files = []
        for file in file_list:
            if (not os.path.isdir(file)):
                xml_files.append(file)
        for xml_name in xml_files:
            print(xml_name)
            self.doc_list.append(Doc(self.folder_path, xml_name, self.doc_size))
            self.doc_size = self.doc_size + 1



if __name__ == '__main__':

    path = Const.path_to_data_FCA_fulltext
    docu_list = DocList(path)
    print(docu_list.doc_size)

    # generating corresponding label
    d = defaultdict(lambda : 0)
    for doc in docu_list.doc_list:
        print(doc.doc_id)
        for word in doc.catchphrases_clear:
            d[word] = d[word] + 1
    sorted_d = sorted(d.items(), key = lambda x: x[1], reverse=True)
    f = open("..\DataSrc\FCA_label_full.txt", 'w')
    for (key, value) in sorted_d:
        print("{0} {1}".format(key, value), file=f)
    f.close()
    list = []
    print("end sort")
    for (x,y) in sorted_d:
        list.append(x)
    f = open("..\DataSrc\FCA_label.txt", 'w')
    for value in list:
        print(value, file=f)
    f.close()

    # generating dat file for tf-idf
    # data only includes the abstract
    f = open("..\DataSrc\FCA_abstract_raw.dat", 'w')
    f1 = open("..\DataSrc\FCA_abstract_raw.txt", 'w')
    for doc in docu_list.doc_list:
        s = ""
        for sen in doc.catchphrases:
            s = s + " " + sen
        s = s + '\n'
        print(s)
        f.write(s)
        f1.write(s)
    f.close()
    f1.close()



