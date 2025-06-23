import os
import urllib.request


def get_image(card_hash):
    localPath = 'files/' + card_hash + ".png"
    if not os.path.exists("files/"):
        os.makedirs("files/")
    if not os.path.isfile(localPath):
        urllib.request.urlretrieve(f"https://shadowverse-wb.com/uploads/card_image/eng/card/{card_hash}.png", localPath)
    return localPath
