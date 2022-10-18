import re, html, base64, os, config
from util.BibleVerseParser import BibleVerseParser
import urllib.parse
try:
    import html_text
    isHtmlTextInstalled = True
except:
    isHtmlTextInstalled = False

try:
    from bs4 import BeautifulSoup
    import html5lib
    isBeautifulsoup4Installed = True
except:
    isBeautifulsoup4Installed = False

class TextUtil:

    @staticmethod
    def formatConfigLabel(text):
        text = re.sub("([a-z])([A-Z])", r"\1 \2", text)
        words = text.split(" ")
        words[0] = words[0].capitalize()
        return " ".join(words)

    @staticmethod
    def getQueryPrefix():
        return "PRAGMA case_sensitive_like = {0}; ".format("true" if config.enableCaseSensitiveSearch else "false")

    @staticmethod
    def regexp(expr, item):
        reg = re.compile(expr, flags=0 if config.enableCaseSensitiveSearch else re.IGNORECASE)
        #return reg.match(item) is not None
        return reg.search(item) is not None

    @staticmethod
    def highlightSearchString(text, searchString):
        if searchString == "z":
            return text
        if config.enableCaseSensitiveSearch:
            return re.sub("({0})".format(searchString), r"<z>\1</z>", text, flags=0)
        else:
            return re.sub("({0})".format(searchString), r"<z>\1</z>", text, flags=re.IGNORECASE)

    @staticmethod
    def colourTerminalText(text):
        if config.isColoramaInstalled:
            # Reference: https://github.com/tartley/colorama/blob/master/colorama/ansi.py
            # standard colours: "RESET", "BLACK", "WHITE", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN"
            # extended colours: "LIGHTBLACK_EX", "LIGHTRED_EX", "LIGHTGREEN_EX", "LIGHTYELLOW_EX", "LIGHTBLUE_EX", "LIGHTMAGENTA_EX", "LIGHTCYAN_EX", "LIGHTWHITE_EX"

            searchReplace = (
                ("(<u><b>|<h>|<h[0-9]>|<h[0-9] .*?>)", r"\1「Fore.{0}」".format(config.terminalHeadingTextColor)),
                ("(<ref>|<ref .*?>|<grk>|<grk .*?>|<heb>|<heb .*?>)", r"\1「Fore.{0}」".format(config.terminalResourceLinkColor)),
                ("(<vid .*?>)", r"\1「Fore.{0}」".format(config.terminalVerseNumberColor)),
                ("(</heb>|</grk>|</ref>|</vid>|</h[0-9]+?>|</h>|</b></u>)", r"\1「Fore.RESET」"),
                # insert a space before '「Back' below
                ("<z>", "「Fore.{1}」 「Back.{0}」".format(config.terminalSearchHighlightBackground, config.terminalSearchHighlightForeground)),
                ("</z>", "「Style.RESET_ALL」"),
            )
            for search, replace in searchReplace:
                #text = text.replace(search, replace)
                text = re.sub(search, replace, text)
        return text

    @staticmethod
    def htmlToPlainText(content, colours=True):
        if config.runMode == "terminal":
            content = re.sub("""(<heb|<grk)( [^<>]*?onclick="luW\([0-9]+?,')([0-9]+?)('[^<>]*?>)""", r"[<ref>\3</ref> ]\1\2\3\4", content)
            content = re.sub("""(<ref onclick="[^<>]+?\(')([^<>]+?)('\)">)""", r"[<ref>\2</ref> ] ", content)
        # Format text colours
        if config.runMode == "terminal" and config.isColoramaInstalled and colours:
            content = TextUtil.colourTerminalText(content)
        # cconvert text
        if isHtmlTextInstalled:
            content = html_text.extract_text(content)
        elif isBeautifulsoup4Installed:
            content = re.sub("(</th>|</td>)", r"\1&emsp;", content)
            content = re.sub("(<br>|<br/>|</tr>)", r"\1\n", content)
            content = re.sub("(</h[0-9]>|</p>|</div>|<hr>)", r"\1\n\n", content)
            content = BeautifulSoup(content, "html5lib").get_text()
        else:
            content = re.sub("<br/?>|<br>", "\n", content)
            content = re.sub('<[^<]+?>', '', content)
        if config.runMode == "terminal" and not colours:
            content = re.sub("「(Fore|Back|Style)\.[A-Z_]+?」", "", content)
        elif config.runMode == "terminal" and config.isColoramaInstalled and colours:
            from colorama import init
            init()
            from colorama import Fore, Back, Style
            searchReplace = (
                ("「Fore.BLACK」", Fore.BLACK),
                ("「Fore.WHITE」", Fore.WHITE),
                ("「Fore.RED」", Fore.RED),
                ("「Fore.GREEN」", Fore.GREEN),
                ("「Fore.YELLOW」", Fore.YELLOW),
                ("「Fore.BLUE」", Fore.BLUE),
                ("「Fore.MAGENTA」", Fore.MAGENTA),
                ("「Fore.CYAN」", Fore.CYAN),
                ("「Fore.LIGHTBLACK_EX」", Fore.LIGHTBLACK_EX),
                ("「Fore.LIGHTRED_EX」", Fore.LIGHTRED_EX),
                ("「Fore.LIGHTGREEN_EX」", Fore.LIGHTGREEN_EX),
                ("「Fore.LIGHTYELLOW_EX」", Fore.LIGHTYELLOW_EX),
                ("「Fore.LIGHTBLUE_EX」", Fore.LIGHTBLUE_EX),
                ("「Fore.LIGHTMAGENTA_EX」", Fore.LIGHTMAGENTA_EX),
                ("「Fore.LIGHTCYAN_EX」", Fore.LIGHTCYAN_EX),
                ("「Fore.LIGHTWHITE_EX」", Fore.LIGHTWHITE_EX),
                ("「Back.BLACK」", Back.BLACK),
                ("「Back.WHITE」", Back.WHITE),
                ("「Back.RED」", Back.RED),
                ("「Back.GREEN」", Back.GREEN),
                ("「Back.YELLOW」", Back.YELLOW),
                ("「Back.BLUE」", Back.BLUE),
                ("「Back.MAGENTA」", Back.MAGENTA),
                ("「Back.CYAN」", Back.CYAN),
                ("「Back.LIGHTBLACK_EX」", Back.LIGHTBLACK_EX),
                ("「Back.LIGHTRED_EX」", Back.LIGHTRED_EX),
                ("「Back.LIGHTGREEN_EX」", Back.LIGHTGREEN_EX),
                ("「Back.LIGHTYELLOW_EX」", Back.LIGHTYELLOW_EX),
                ("「Back.LIGHTBLUE_EX」", Back.LIGHTBLUE_EX),
                ("「Back.LIGHTMAGENTA_EX」", Back.LIGHTMAGENTA_EX),
                ("「Back.LIGHTCYAN_EX」", Back.LIGHTCYAN_EX),
                ("「Back.LIGHTWHITE_EX」", Back.LIGHTWHITE_EX),
                ("[ ]*「Fore.RESET」", Fore.RESET),
                ("[ ]*「Back.RESET」", Back.RESET),
                ("[ ]*「Style.RESET_ALL」", Style.RESET_ALL),
            )
            for search, replace in searchReplace:
                #content = content.replace(search, replace)
                content = re.sub(search, replace, content)

        searchReplace = (
            (" audiotrack", ""),
            (" [ ]+?([^ ])", r" \1"),
        )
        for search, replace in searchReplace:
            #content = content.replace(search, replace)
            content = re.sub(search, replace, content)
        return content

    @staticmethod
    def imageToText(filepath):
        fileBasename = os.path.basename(filepath)
        *_, fileExtension = os.path.splitext(fileBasename)
        if fileExtension.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            # read a binary file
            with open(filepath, "rb") as fileObject:
                binaryData = fileObject.read()
                encodedData = base64.b64encode(binaryData)
                binaryString = encodedData.decode("ascii")
                htmlTag = '<img src="data:image/{2};base64,{0}" alt="{1}">'.format(binaryString, fileBasename, fileExtension[1:])
            return htmlTag
        else:
            return "[File type not supported!]"

    @staticmethod
    def formulateUBACommandHyperlink(text):
        # Create hyperlink to UBA command
        # work on text formatted like ***[CROSSREFERENCE:::John 3:16@An hyperlink link to open cross-references of John 3:16]
        return re.sub("\*\*\*\[([^'{0}]*?)@([^'{0}]*?)\]".format('"\*\[\]@'), r"<ref onclick={0}document.title='\1'{0}>\2</ref>".format('"'), text)

    @staticmethod
    def fixTextHighlighting(text):
        # fix searching LXX / SBLGNT words
        text = re.sub(r"<z>([LS][0-9]+?)</z>'\)"'"'">(.*?)</grk>", r"\1'\)"'"'r"><z>\2</z></grk>", text)
        # remove misplacement of tags <z> & </z>
        p = re.compile("(<[^<>]*?)<z>(.*?)</z>", flags=re.M)
        s = p.search(text)
        while s:
            text = re.sub(p, r"\1\2", text)
            s = p.search(text)
        return text

    @staticmethod
    def plainTextToUrl(text):
        # https://wiki.python.org/moin/EscapingHtml
        text = html.escape(text)
        searchReplace = (
            (" ", "%20"),
            ("\n", "%0D%0A"),
        )
        for search, replace in searchReplace:
            text = text.replace(search, replace)
        return text

    # Return digits from a string
    @staticmethod
    def getDigits(text):
        return ''.join(c for c in text if c.isdigit())

    # Generate a web link for sharing
    @staticmethod
    def getWeblink(command, server=""):
        # https://stackoverflow.com/questions/40557606/how-to-url-encode-in-python-3
        command = urllib.parse.quote(command)
        htmlPages = {
            "ENG": "index.html",
            "TC": "traditional.html",
            "SC": "simplified.html",
        }
        htmlPage = "" if config.webUBAServer.endswith(".html") and not server else "/{0}".format(htmlPages.get(htmlPages[config.standardAbbreviation], "index.html"))
        return "{0}{1}?cmd={2}".format(server if server else config.webUBAServer, htmlPage, command)

    # Remove Hebrew vowels or Greek accents
    @staticmethod
    def removeVowelAccent(text):
        searchReplace = (
            (r"[\֑\֒\֓\֔\֕\֖\֗\֘\֙\֚\֛\֜\֝\֞\֟\֠\֡\֣\֤\֥\֦\֧\֨\֩\֪\֫\֬\֭\֮\ֽ\ׄ\ׅ\‍\‪\‬\̣\ְ\ֱ\ֲ\ֳ\ִ\ֵ\ֶ\ַ\ָ\ֹ\ֺ\ֻ\ׂ\ׁ\ּ\ֿ\־\׀\׆]", ""),
            ("[שׂשׁ]", "ש"),
            ("[ἀἄᾄἂἆἁἅᾅἃάᾴὰᾶᾷᾳ]", "α"),
            ("[ἈἌἎἉἍἋ]", "Α"),
            ("[ἐἔἑἕἓέὲ]", "ε"),
            ("[ἘἜἙἝἛ]", "Ε"),
            ("[ἠἤᾔἢἦᾖᾐἡἥἣἧᾗᾑήῄὴῆῇῃ]", "η"),
            ("[ἨἬἪἮἩἭἫ]", "Η"),
            ("[ἰἴἶἱἵἳἷίὶῖϊΐῒ]", "ι"),
            ("[ἸἼἹἽ]", "Ι"),
            ("[ὀὄὂὁὅὃόὸ]", "ο"),
            ("[ὈὌὉὍὋ]", "Ο"),
            ("[ῥ]", "ρ"),
            ("[Ῥ]", "Ρ"),
            ("[ὐὔὒὖὑὕὓὗύὺῦϋΰῢ]", "υ"),
            ("[ὙὝὟ]", "Υ"),
            ("[ὠὤὢὦᾠὡὥὧᾧώῴὼῶῷῳ]", "ω"),
            ("[ὨὬὪὮὩὭὯ]", "Ω"),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text

    # fix note font display
    @staticmethod
    def fixNoteFontDisplay(content):
        if config.overwriteNoteFont:
            content = re.sub("font-family:[^<>]*?([;'{0}])".format('"'), r"font-family:{0}\1".format(config.font),
                             content)
        if config.overwriteNoteFontSize:
            content = re.sub("font-size:[^<>]*?;", "", content)
        return content

    # fix note font display
    @staticmethod
    def fixNoteFont(note):
        note = re.sub("<body style={0}[ ]*?font-family:[ ]*?'[^']*?';[ ]*?font-size:[ ]*?[0-9]+?pt;".format('"'), "<body style={0}font-family:'{1}'; font-size:{2}pt;".format('"', config.font, config.fontSize), note)
        if not config.includeStrictDocTypeInNote:
            note = re.sub("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n""", "", note)
        return note

    # wrap with html
    @staticmethod
    def htmlWrapper(text, parsing=False, view="study", linebreak=True, html=True):
        searchReplace1 = (
            ("\r\n|\r|\n", "<br>"),
            ("\t", "&emsp;&emsp;"),
        )
        searchReplace2 = (
            ("<br>(<table>|<ol>|<ul>)", r"\1"),
            ("(</table>|</ol>|</ul>)<br>", r"\1"),
            ("<a [^\n<>]*?href=['{0}]([^\n<>]*?)['{0}][^\n<>]*?>".format('"'),
             r"<a href='javascript:void(0)' onclick='website({0}\1{0})'>".format('"')),
            ("onclick='website\({0}([^\n<>]*?).uba{0}\)'".format('"'), r"onclick='uba({0}\1.uba{0})'".format('"'))
        )
        if linebreak:
            for search, replace in searchReplace1:
                text = re.sub(search, replace, text)
        if html:
            for search, replace in searchReplace2:
                text = re.sub(search, replace, text)
        if parsing:
            # Export inline images to external files, so as to improve parsing performance. 
            text = TextUtil.exportAllImages(text)
            text = TextUtil.formulateUBACommandHyperlink(text)
            text = BibleVerseParser(config.parserStandarisation).parseText(text)
        if not "<!DOCTYPE html><html><head><meta charset='utf-8'><title>UniqueBible.app</title>" in text:
            text = TextUtil.wrapHtml(text, view)
        return text

    # export images
    @staticmethod
    def exportAllImages(htmlText):
        config.exportImageNumber = 0
        searchPattern = r'src=(["{0}])data:image/([^<>]+?);[ ]*?base64,[ ]*?([^ <>]+?)\1'.format("'")
        htmlText = re.sub(searchPattern, TextUtil.exportAnImage, htmlText)
        return htmlText

    @staticmethod
    def exportAnImage(match):
        exportFolder = os.path.join("htmlResources", "images", "export")
        if not os.path.isdir(exportFolder):
            os.makedirs(exportFolder)
        quotationMark, ext, asciiString = match.groups()
        # Note the difference between "groups" and "group"
        # wholeString = match.group(0)
        # quotationMark = match.group(1)
        # ext = match.group(2)
        # asciiString = match.group(3)
        config.exportImageNumber += 1
        binaryString = asciiString.encode("ascii")
        binaryData = base64.b64decode(binaryString)
        imageFilename = "tab{0}_image{1}.{2}".format(100, config.exportImageNumber, ext)
        exportPath = os.path.join(exportFolder, imageFilename)
        with open(exportPath, "wb") as fileObject2:
            fileObject2.write(binaryData)
        return "src={0}images/export/{1}{0}".format(quotationMark, imageFilename)

    # wrap with html 2
    @staticmethod
    def wrapHtml(content, view="", book=False):
        fontFamily = config.font
        fontSize = "{0}px".format(config.fontSize)
        if book:
            if config.overwriteBookFontFamily:
                fontFamily = config.overwriteBookFontFamily
            if config.overwriteBookFontSize:
                if type(config.overwriteBookFontSize) == str:
                    fontSize = config.overwriteBookFontSize
                elif type(config.overwriteBookFontSize) == int:
                    fontSize = "{0}px".format(config.overwriteBookFontSize)
        bcv = (config.studyText, config.studyB, config.studyC, config.studyV) if view == "study" else (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
        html = ("""<!DOCTYPE html><html><head><link rel="icon" href="icons/{9}"><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />"""
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                ".ubaButton {2} background-color: {10}; color: {11}; border: none; padding: 2px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 17px; margin: 2px 2px; cursor: pointer; {3}"
                "{8}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css?v=1.064'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.064'>"
                "<script src='js/common.js?v=1.064'></script>"
                "<script src='js/{7}.js?v=1.064'></script>"
                "<script src='w3.js?v=1.064'></script>"
                "<script src='js/http_server.js?v=1.064'></script>"
                """<script>
                var target = document.querySelector('title');
                var observer = new MutationObserver(function(mutations) {2}
                    mutations.forEach(function(mutation) {2}
                        ubaCommandChanged(document.title);
                    {3});
                {3});
                var config = {2}
                    childList: true,
                {3};
                observer.observe(target, config);
                </script>"""
                "{0}"
                """<script>var versionList = []; var compareList = []; var parallelList = [];
                var diffList = []; var searchList = [];</script>"""
                "<script src='js/custom.js?v=1.064'></script>"
                "</head><body><span id='v0.0.0'></span>{1}"
                "<p>&nbsp;</p><div id='footer'><span id='lastElement'></span></div><script>loadBible();document.querySelector('body').addEventListener('click', window.parent.closeSideNav);</script></body></html>"
                ).format(activeBCVsettings,
                         content,
                         "{",
                         "}",
                         fontSize,
                         fontFamily,
                         config.fontChinese,
                         config.theme,
                         TextUtil.getHighlightCss(),
                         config.webUBAIcon,
                         config.widgetBackgroundColor,
                         config.widgetForegroundColor,
                         )
        return html

    # get highlight css
    @staticmethod
    def getHighlightCss():
        css = ""
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            css += ".{2} {0} background: {3}; {1} ".format("{", "}", code, config.highlightDarkThemeColours[i] if config.theme == "dark" else config.highlightLightThemeColours[i])
        return css

    # Remove special characters
    @staticmethod
    def removeSpecialCharacters(text):
        searchReplace = (
            (r"[\-\—\,\;\:\\\?\.\·\·\‘\’\‹\›\“\”\«\»\(\)\[\]\{\}\⧼\⧽\〈\〉\*\‿\᾽\⇔\¦]", ""),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text


if __name__ == '__main__':

    print(TextUtil.getDigits("abc123def"))
