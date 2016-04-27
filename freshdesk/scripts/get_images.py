"""
Python script to download all images from Freshdesk.
"""

import re
import os
import urllib
import glob

def main():
    articles = glob.glob("posts/*/*/*")
    for article in articles:
        article_id = article.split("/")[3]
        print "Processing article #" + str(article_id)
        download_images(article)


def download_images(image_path):
    body = open(image_path + "/index.html", 'r+')
    for line in body:
        image = re.search('src="([A-Z,a-z,0-9,\-,:,_,/,\.]*)">', line)
        # Only download if there is an image
        if image:
            image_url = image.group(1)
            image_name = image_url.split("/")[-1]
            urllib.urlretrieve(image_url, image_path + "/" + image_name)
            print "Downloaded: " + image_name

if __name__ == '__main__':
    main()
