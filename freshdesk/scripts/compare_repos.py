"""
Python script to check if any articles were created on Freshdesk instead of locally
or if any articles were deleted from Freshdesk but not deleted locally.
"""
import glob
from colorama import init
from colorama import Fore
init()


def compare_article_ids(freshdesk, freshdesk_articles=None):
    freshdesk_ids = []

    if not freshdesk_articles:
        freshdesk_articles = freshdesk.articles.get_all_articles()

    for article in freshdesk_articles:
        freshdesk_ids.append(str(article['id']))

    local_ids = glob.glob("posts/*/*/*")
    local_ids = map(_extract_article_id, local_ids)

    local_ids.sort()
    freshdesk_ids.sort()

    for ids in freshdesk_ids:
        if str(ids) not in set(local_ids):
            print(Fore.RED + "WARNING: Article number %s was created directly in Freshdesk and is not tracked by Git." %str(ids) + Fore.RESET)
    for ids in local_ids:
        if str(ids) not in set(freshdesk_ids):
            print(Fore.RED + "WARNING: Article number %s was deleted in Freshdesk but not deleted in Git." %str(ids) + Fore.RESET)


def _extract_article_id(path):
    return path.split('/')[3]


def _extract_article_folder_id(path):
    return path.split('/')[2]


def _extract_article_category_id(path):
    return path.split('/')[1]


def compare_article_contents(article_id, freshdesk):
    local_path = glob.glob("posts/*/*/{}".format(str(article_id)))[0]
    category_id = _extract_article_category_id(local_path)
    folder_id = _extract_article_folder_id(local_path)

    article = freshdesk.articles.get_article(article_id, folder_id, category_id)

    # If the title has changed, deploy the article.
    title = article['title']
    if title != open(local_path + "/title.html").readline():
        return True

    # Read local body into a string to compare with freshdesk body
    rendered_path = "site/{}/{}/{}/index.html".format(str(category_id), str(folder_id), str(article_id))
    with open(rendered_path, "r") as myfile:
        local_body = myfile.read()

    # If the bodies are not the same, deploy the article
    if local_body != article['description']:
        return True
    return False


def line_count(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
