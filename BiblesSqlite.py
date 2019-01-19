"""
Reading data from bibles.sqlite
"""
import os, sqlite3, config, re
from BibleVerseParser import BibleVerseParser

class BiblesSqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join("marvelData", "bibles.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.rtlTexts = ["original", "MOB", "MAB", "MTB", "MIB", "MPB", "OHGB"]

    def __del__(self):
        self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        Parser = BibleVerseParser("YES")
        verseReference = Parser.bcvToVerseReference(b, c, v)
        del Parser
        return verseReference

    def formTextTag(self, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}\"' onmouseover='textName(\"{0}\")'>".format(text)

    def formBookTag(self, b, text=config.mainText):
        bookAbb = self.bcvToVerseReference(b, 1, 1)[:-4]
        return "<ref onclick='document.title=\"_menu:::{0}.{1}\"' onmouseover='bookName(\"{2}\")'>".format(text, b, bookAbb)

    def formChapterTag(self, b, c, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}.{1}.{2}\"'>".format(text, b, c)

    def formVerseTag(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"BIBLE:::{3}:::{4}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, text, verseReference)

    def readTextChapter(self, text, b, c):
        t = (b, c)
        query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
        self.cursor.execute(query, t)
        textChapter = self.cursor.fetchall()
        if not textChapter:
            return [(b, c, 1, "")]
        # return a list of tuple
        return textChapter

    def readTextVerse(self, text, b, c, v):
        t = (b, c, v)
        query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? AND Verse=?".format(text)
        self.cursor.execute(query, t)
        textVerse = self.cursor.fetchone()
        if not textVerse:
            return (b, c, v, "")
        # return a tuple
        return textVerse

    def getBibleList(self):
        t = ("table",)
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, t)
        versions = self.cursor.fetchall()
        exclude = ("Details", "lexicalEntry", "morphology", "original", "title")
        return [version[0] for version in versions if not version[0] in exclude]

    def getTexts(self):
        textList = self.getBibleList()
        texts = ""
        for text in textList:
            texts += "{0}{1}</ref> ".format(self.formTextTag(text), text)
        return texts

    def getBookList(self, text=config.mainText):
        query = "SELECT DISTINCT Book FROM {0} ORDER BY Book".format(text)
        self.cursor.execute(query)
        return [book[0] for book in self.cursor.fetchall()]

    def getBooks(self, text=config.mainText):
        bookList = self.getBookList(text)
        books = ""
        for book in bookList:
            bookName = self.bcvToVerseReference(book, 1, 1)[:-4]
            books += "{0}{1}</ref> ".format(self.formBookTag(book, text), bookName)
        return books

    def getChapterList(self, b=config.mainB, text=config.mainText):
        t = (b,)
        query = "SELECT DISTINCT Chapter FROM {0} WHERE Book=? ORDER BY Chapter".format(text)
        self.cursor.execute(query, t)
        return [chapter[0] for chapter in self.cursor.fetchall()]

    def getChapters(self, b=config.mainB, text=config.mainText):
        chapterList = self.getChapterList(b, text)
        chapters = ""
        for chapter in chapterList:
            chapters += "{0}{1}</ref> ".format(self.formChapterTag(b, chapter, text), chapter)
        return chapters

    def getChaptersMenu(self, b=config.mainB, text=config.mainText):
        chapterList = self.getChapterList(b, text)
        chapters = ""
        for chapter in chapterList:
            chapters += "{0}{1}</ref> ".format(self.formVerseTag(b, chapter, 1, text), chapter)
        return chapters

    def getVerseList(self, b, c, text=config.mainText):
        t = (b, c)
        query = "SELECT DISTINCT Verse FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
        self.cursor.execute(query, t)
        return [verse[0] for verse in self.cursor.fetchall()]

    def getVerses(self, b=config.mainB, c=config.mainC, text=config.mainText):
        verseList = self.getVerseList(b, c, text)
        verses = ""
        for verse in verseList:
            verses += "{0}{1}</ref> ".format(self.formVerseTag(b, c, verse, text), verse)
        return verses

    def compareVerse(self, verseList, texts=["ALL"]):
        if len(verseList) == 1 and not texts == ["ALL"]:
            b, c, v = verseList[0]
            return self.compareVerseChapter(b, c, v, texts)
        else:
            verses = ""
            for verse in verseList:
                b, c, v = verse
                verses += self.readTranslations(b, c, v, texts)
            return verses

    def compareVerseChapter(self, b, c, v, texts):
        verseList = self.getVerseList(b, c, texts[0])
        chapter = "<h2>{0}</h2><table style='width: 100%;'>".format(self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        for verse in verseList:
            row = 0
            for text in texts:
                row = row + 1
                if row % 2 == 0:
                    chapter += "<tr>"
                else:
                    chapter += "<tr style='background-color: #f2f2f2;'>"
                if row == 1:
                    chapter += "<td style='vertical-align: text-top;'><vid>{0}{1}</ref></vid> ".format(self.formVerseTag(b, c, verse, text), verse)
                else:
                    chapter += "<td>"
                textTdTag = "<td>"
                if b < 40 and text in self.rtlTexts:
                    textTdTag = "<td style='direction: rtl;'>"
                chapter += "</td><td><sup>({0}{1}</ref>)</sup></td>{2}{3}</td></tr>".format(self.formVerseTag(b, c, verse, text), text, textTdTag, self.readTextVerse(text, b, c, verse)[3])
        chapter += "</table>"
        return chapter

    def readTranslations(self, b, c, v, texts):
        if texts == ["ALL"]:
            bibleList = self.getBibleList()
            texts = ["OHGB", "LXX"]
            exclude = ("LXX", "LXX1", "LXX1i", "LXX2", "LXX2i", "MOB", "MAB", "MIB", "MPB", "MTB", "OHGB")
            for bible in bibleList:
                if not bible in exclude:
                    texts.append(bible)
        verses = "<h2>{0}</h2>".format(self.bcvToVerseReference(b, c, v))
        for text in texts:
            book, chapter, verse, verseText = self.readTextVerse(text, b, c, v)
            divTag = "<div>"
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), text, verseText.strip())
        return verses

    def searchBible(self, text, mode, searchString, interlinear=False):
        query = "SELECT * FROM {0} WHERE ".format(text)
        if mode == "BASIC":
            t = ("%{0}%".format(searchString),)
            query += "Scripture LIKE ?"
        elif mode == "ADVANCED":
            t = ()
            query += searchString
        query += " ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query, t)
        verses = self.cursor.fetchall()
        formatedText = ""
        for verse in verses:
            b, c, v, verseText = verse
            divTag = "<div>"
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            formatedText += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), self.bcvToVerseReference(b, c, v), verseText.strip())
            if interlinear:
                if b < 40:
                    divTag = "<div style='direction: rtl;'>"
                else:
                    divTag = "<div>"
                formatedText += "{0}{1}</div>".format(divTag, self.readTextVerse("OHGB", b, c, v)[3])
        if mode == "BASIC":
            formatedText = re.sub("("+searchString+")", r"<span style='color:red;'>\1</span>", formatedText, flags=re.IGNORECASE)
        elif mode == "ADVANCED":
            searchWords = [m for m in re.findall("LIKE ['\"]%(.*?)%['\"]", searchString, flags=re.IGNORECASE)]
            print(searchWords)
            for searchword in searchWords:
                formatedText = re.sub("("+searchword+")", r"<span style='color:red;'>\1</span>", formatedText, flags=re.IGNORECASE)
        return formatedText

    def instantVerse(self, text, bcvList):
        query = "SELECT * FROM morphology WHERE Book = ? AND Chapter = ? AND Verse = ? ORDER BY WordID"
        self.cursor.execute(query, bcvList)
        words = self.cursor.fetchall()
        interlinearVerse = ""
        for word in words:
            wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation = word
            if b < 40:
                textWord = "<heb>{0}</heb>".format(textWord)
            else:
                textWord = "<grk>{0}</grk>".format(textWord)
            interlinearVerse += "{0}<gloss>{1}</gloss> ".format(textWord, interlinear)
        if bcvList[0] < 40:
            interlinearVerse = "<div style='direction: rtl;'>{0}</div>".format(interlinearVerse)
        return interlinearVerse

    def instantWord(self, book, wordId):
        t = (book, wordId)
        query = "SELECT * FROM morphology WHERE Book = ? AND WordID = ?"
        self.cursor.execute(query, t)
        word = self.cursor.fetchone()
        wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation = word
        morphology = morphology.replace(",", ", ")
        if b < 40:
            textWord = "<heb>{0}</heb>".format(textWord)
            lexeme = "<heb>{0}</heb>".format(lexeme)
        else:
            textWord = "<grk>{0}</grk>".format(textWord)
            lexeme = "<grk>{0}</grk>".format(lexeme)
        return "{0} <span style='color: gray'>{1}</span> {2} {3} <span style='color: brown'>{4}</span> <span style='color: blue'>{5}</span>".format(textWord, transliteration, lexeme, morphology, interlinear, translation)

    def searchMorphology(self, mode, searchString):
        query = "SELECT * FROM morphology WHERE "
        if mode == "LEMMA":
            t = ("%{0},%".format(searchString),)
            query += "LexicalEntry LIKE ?"
        elif mode == "CODE":
            searchList = searchString.split(',')
            t = ("%{0},%".format(searchList[0]), searchList[1])
            query += "LexicalEntry LIKE ? AND MorphologyCode = ?"
        elif mode == "ADVANCED":
            t = ()
            query += searchString
        query += " ORDER BY Book, Chapter, Verse, WordID"
        self.cursor.execute(query, t)
        words = self.cursor.fetchall()
        formatedText = ""
        for word in words:
            wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation = word
            if b < 40:
                textWord = "<heb>{0}</heb>".format(textWord)
            else:
                textWord = "<grk>{0}</grk>".format(textWord)
            formatedText += "({0}{1}</ref>) {2} {3}<br>".format(self.formVerseTag(b, c, v, config.mainText), self.bcvToVerseReference(b, c, v), textWord, morphologyCode)
        return formatedText

    def readMultipleVerses(self, text, verseList):
        verses = ""
        for verse in verseList:
            b, c, v = verse
            divTag = "<div>"
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), self.bcvToVerseReference(b, c, v), self.readTextVerse(text, b, c, v)[3])
        return verses

    def readPlainChapter(self, text, verse):
        # expect bcv is a tuple
        b, c, v = verse
        chapter = "<h2>{0}{1}</ref></h2>".format(self.formChapterTag(b, c, text), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        titleList = self.getVerseList(b, c, "title")
        verseList = self.readTextChapter(text, b, c)
        for verseTuple in verseList:
            b, c, v, verseText = verseTuple
            divTag = "<div>"
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            if v in titleList:
                if not v == 1:
                    chapter += "<br>"
                chapter += "{0}<br>".format(self.readTextVerse("title", b, c, v)[3])
            chapter += "{0}<vid>{1}{2}</ref></vid> {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), v, verseText)
        return chapter


class BibleSqlite:

    def __init__(self, text):
        # connect bibles.sqlite
        self.text = text
        self.database = os.path.join("marvelData", "bibles", text+".bible")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.rtlTexts = ["original", "MOB", "MAB", "MTB", "MIB", "MPB", "OHGB"]

    def __del__(self):
        self.connection.close()

    def readFormattedChapter(self, verse):
        b, c, v = verse
        biblesSqlite = BiblesSqlite()
        chapter = "<h2>{0}{1}</ref></h2>".format(biblesSqlite.formChapterTag(b, c, self.text), biblesSqlite.bcvToVerseReference(b, c, v).split(":", 1)[0])
        del biblesSqlite
        query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, verse[:-1])
        scripture = self.cursor.fetchone()
        chapter += re.sub('onclick="luV\(([0-9]+?)\)"', r'onclick="luV(\1)" onmouseover="qV(\1)" ondblclick="mV(\1)"', scripture[0])
        if not scripture:
            return "[No content is found for this chapter!]"
        else:
            divTag = "<div>"
            if self.text in self.rtlTexts and b < 40:
                divTag = "<div style='direction: rtl;'>"
            return "{0}{1}</div>".format(divTag, chapter)

#if __name__ == '__main__':
    # Bibles = BiblesSqlite()

    # test search bible - BASIC
    # searchString = input("Search Bible [Basic]\nSearch for: ")
    # print(Bibles.searchBible("NET", "BASIC", searchString))

    # test search bible - ADVANCED
    # e.g. Scripture LIKE '%God%' AND Scripture LIKE '%love%'
    # searchString = input("Search Bible [Advanced]\nFilter for search: ")
    # print(Bibles.searchBible("NET", "ADVANCED", searchString))

    # test search morphology - lexicalEntry
    # e.g. H7225
    # searchString = input("Search Morphology [Lexical Entry]\nSearch for: ")
    # print(Bibles.searchMorphology("LEMMA", searchString))

    # test search morphology - MorphologyCode
    # e.g. E70020,verb.qal.wayq.p1.u.sg
    # searchString = input("Search Morphology [Morphology Code]\nFilter for search: ")
    # print(Bibles.searchMorphology("CODE", searchString))

    # test search morphology - ADVANCED
    # e.g. LexicalEntry LIKE '%E70020,%' AND Morphology LIKE '%third person%' AND (Book = 9 OR Book = 10)
    # searchString = input("Search Morphology [ADVANCED]\nFilter for search: ")
    # print(Bibles.searchMorphology("ADVANCED", searchString))

    # del Bibles
