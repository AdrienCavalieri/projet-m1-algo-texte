import math
import os
import string
from bs4 import BeautifulSoup
from Page import Page
from progress.bar import Bar


class Index_inverse():

    def __init__(self, dirPath):
        dir = os.listdir(dirPath)  # liste tous les fichiers d'un répertoire
        pages = list()
        i = 0
        j = 0
        bar = Bar('Chargement des pages dans l\'index', max=len(dir), suffix='%(percent).1f%% - %(eta)ds')
        for fileName in dir:
            j = j + 1
            filePath = dirPath + "/" + fileName
            try:
                file = open(filePath, 'r', encoding="utf8")  # lis le fichier avec encodage utf8
                content = file.read()
                soup = BeautifulSoup(content, "html.parser")  # lib pour parser une page html
                text = soup.get_text()  # recupere uniquement le texte

                mots = text.split()
                mots = [mot.lower() for mot in mots]
                table = str.maketrans('', '', string.punctuation)
                mots = [mot.translate(table) for mot in mots]

                href = soup.find_all('a', href=True)  # recupere les balises de lien
                liens = list()
                for a in href:
                    liens.append(a['href'])  # recupere les liens contenus dans les balises
                pages.append(Page(fileName, mots, liens))  # créer un objet page
                file.close()
            except:
                i = i + 1  # nb de fichiers ignoré
            bar.next()
        bar.finish()
        self._urlsLoad = len(pages)
        self._pages = pages
        self._indexInverse = dict()
        self.loadIndex()

    def loadIndex(self):  # on rempli l'index inversé par rapport au page chargée
        i = 0
        bar = Bar('Chargement des mots de chaque page dans l\'index', max=len(self._pages),
                  suffix='%(percent).1f%% - %(eta)ds')
        for page in self._pages:
            i = i + 1
            for mot in page.get_mots():
                if mot in self._indexInverse:
                    if page.get_nom() not in self._indexInverse[mot]:
                        self._indexInverse[mot].append(page.get_nom())
                else:
                    self._indexInverse[mot] = list()
                    self._indexInverse[mot].append(page.get_nom())
            bar.next()
        bar.finish()

    def printIndex(self):
        if os.path.exists("log.txt"):
            os.remove("log.txt")
        f = open("log.txt", "a+", encoding="utf8")

        for name, liste in self._indexInverse.items():
            try:
                f.write(name + ":" + str(liste) + "\r\n")
                # f.write(name + ":\r\n")
            except:
                pass
        f.close()

    def tf(self, mot, namePage):
        for page in self._pages:
            if page.get_nom() == namePage:
                #print(page)
                return page.getScoreMot(mot)/page.getTotalScore()
        return 0

    def idf(self,mot):
        if mot not in self._indexInverse:
            return 0
        else:
            #print(self._indexInverse[mot])
            return math.log(len(self._pages)/len(self._indexInverse[mot]))

    def tf_idf(self,mot,namePage):
        return self.tf(mot,namePage)*self.idf(mot)