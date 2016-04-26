"""
Python script to create a new article in a given section id.
"""

import os
import sys


from requests import HTTPError
from API.freshdesk import API
from scripts import file_constants

from colorama import init
from colorama import Fore

init()


def main(category_id, folder_id):
    # Get domain
    try:
        domain = os.environ["FRESHDESK_DOMAIN"]
    except KeyError:
        print(Fore.RED + "Please set the environment variable FRESHDESK_DOMAIN" + Fore.RESET)
        sys.exit(1)

    # Get key
    try:
        key = os.environ["FRESHDESK_API_KEY"]
    except KeyError:
        print(Fore.RED + "Please set the environment variable FRESHDESK_API_KEY" + Fore.RESET)
        sys.exit(1)

    freshdesk = API(domain, key)

    # Add a temporary title and leave it in draft mode.
    new_article = _empty_article(folder_id)

    # verify that the folder/category exists
    try:
        freshdesk.folders.get_folder(folder_id, category_id)
    except HTTPError:
        print(Fore.RED + "Verify that folder:{} and category:{} both exist".format(folder_id, category_id))
        sys.exit(1)

    # try to make the article shell
    try:
        # verify that the folder/category exists
        freshdesk.folders.get_folder(folder_id, category_id)
        article = freshdesk.articles.create_article(folder_id, category_id, article=new_article)
    except HTTPError:
        print(Fore.RED + "Unable to create article in folder:{} and category:{}".format(folder_id, category_id))
        sys.exit(1)

    # Report success.
    print('Successfully created the article.')

    # Create the article shell locally.
    article_id = article['id']
    create_shell(str(category_id), str(folder_id), str(article_id))


def create_shell(category_id, folder_id, article_id):
    # creates the article in posts/category_id/folder_id
    path = "posts/" + category_id + "/" + folder_id + "/" + article_id
    article = path + "/index.html"
    title = path + "/title.html"

    # The ID must be eleven numbers.
    if len(article_id) == 11 and article_id.isdigit() and not os.path.isfile(article):
        # Makes the folder for the article and pictures to be placed in.
        os.makedirs(path)
        # Create the article and title shell.
        open(article, 'a').close()
        open(title, 'a').close()
        # Provides the user with the location of the html file that was created.
        print "The article is located at " + article
        print "Enter the article's title at " + title
    elif os.path.isfile(article):
        print (Fore.RED + "Error: This article ID already exists: " + article_id + Fore.RESET)
        sys.exit(1)
    else:
        print (Fore.RED + "Error: This article ID is invalid: " + article_id + Fore.RESET)
        sys.exit(1)


def _empty_article(folder_id):
    if not folder_id:
        raise ValueError
    return {
            "title": "Temporary Title",
            "status": 1,
            "art_type": 1,
            "description": "Temporary Content",
            "folder_id": folder_id
          }

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python %s <category_id> <folder_id>' % sys.argv[0])
    else:
        main(sys.argv[1], sys.argv[2])
