import os.path


# Revisa si el archivo está vacío
def isNonZeroFile(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


def getArticlesID(articles):
    IDList = []
    for entry in articles:
        IDList.append(entry["id"])
    return IDList


def loadArticleFromID(ID, articles):
    loadArticle = False
    for entry in articles:
        if ID == entry["id"]:
            loadArticle = entry
    return loadArticle


# Limpia el archivo si hay más de 12 líneas
def truncateFile():
    with open('entries.txt', 'r') as fin:
        entries = fin.readlines()
    if len(entries) > 12:
        with open('entries.txt', 'w') as fout:
            fout.writelines(entries[len(entries) - 12:])


# Guarda un archivo con los artículos que se enviaron
def saveEntries(listToSave):
    listID = getArticlesID(listToSave)
    file = open("entries.txt", "a")
    for index, article in enumerate(listID):
        file.write(article if index == 0 and not isNonZeroFile("entries.txt") else "\n" + article)
    file.close()
    truncateFile()


# Carga el archivo y devuelve cada línea en una lista
def loadFile():
    if os.path.isfile("entries.txt"):
        file = open("entries.txt", "r")
        lines = file.readlines()
        for x in range(len(lines)):
            lines[x] = lines[x].replace("\n", "")
        file.close()
        return lines
    else:
        file = open("entries.txt", "x")
        file.close()
        return []


# Este es la función principal, la cual va a devolver nuevas entradas (si las hay) para procesarlas luego
def checkForNewEntries(news_json):
    currentEntries = getArticlesID(news_json["data"]["information_list"])
    savedEntries = loadFile()

    newEntries = [entry for entry in currentEntries if entry not in savedEntries]
    newEntryList = [loadArticleFromID(entry, news_json["data"]["information_list"]) for entry in newEntries]

    if newEntryList:
        return {"success": True, "data": newEntryList[::-1], "error": None}
    else:
        return {"success": True, "data": None, "error": None}
