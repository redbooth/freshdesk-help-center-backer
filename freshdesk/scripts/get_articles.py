"""
Python script to download all articles from Freshdesk in proper format.
"""

import os
import file_constants
from API.freshdesk import API

IMAGE_FORMATS = file_constants.IMAGE_FORMATS

def main():
    make_folder("posts")
    freshdesk = API("guigobbler.freshdesk.com", "QY24RPklkWtTQVIKamXd")
    articles = freshdesk.articles.get_all_articles()

    for article in articles:
        article_id = str(article['id'])
        folder_id = str(article['folder_id'])
        category_id = str(article['parent_id'])
        print "Processing article #" + article_id

        article_path = file_constants.get_path_from_article_data(article_id, folder_id, category_id)
        make_folder(article_path)

        body = open(article_path + "/index.html", "a")
        body.write(article['description'])

        title = open(article_path + "/title.html", "a")
        title.write(article['title'])

        tags = open(article_path + "/tags.txt", "a")
        tags.write('')


def make_folder(path):
    try:
        os.stat(path)
    except:
        os.mkdir(path)

if __name__ == "__main__":
    main()
