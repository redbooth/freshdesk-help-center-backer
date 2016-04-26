"""
Python script to deploy article to Freshdesk.
"""

import os
import sys
import glob


from colorama import init
from colorama import Fore

from scripts import renderer
from scripts import cloudfront_images
from scripts import compare_repos

from scripts import file_constants
from API.freshdesk import API

init()


def main(article_id, freshdesk, cloudfront_url):

    # Check if the article_id is valid
    try:
        post_path = glob.glob("posts/*/*/{}".format(article_id))[0]
    except:
        print (Fore.RED + "The article_id you entered is invalid." + Fore.RESET)
        sys.exit(1)

    title = open(post_path + "/title.html").readline()
    if not title:
        print (Fore.RED + "Add a title to " + post_path + " before deploying the article." + Fore.RESET)
        sys.exit(1)

    # Prepare files for being pushed to Freshdesk.
    renderer.render_freshdesk_deployment(cloudfront_url, freshdesk.domain, article_id)

    # Push the images to CloudFront.
    cloudfront_images.push_to_cloudfront(article_id)

    # Delete extra images on CloudFront.
    cloudfront_images.delete_from_cloudfront(article_id)

    if not compare_repos.compare_article_contents(article_id, freshdesk):
        return

    # Packages the data in a dictionary matching the expected JSON.
    path = post_path.replace("posts/", "site/", 1) + "/index.html"
    folder_id = post_path.split("/")[2]
    category_id = post_path.split("/")[1]

    # update the article
    update_article = _article_json(title, open(path, mode='rb').read())
    response = freshdesk.articles.update_article(article_id, folder_id, category_id, article=update_article)

    # Check if article is in Draft mode.
    check_draft = (response['status'] == 1)
    if check_draft:
        print (Fore.YELLOW + "Article " + article_id + " is still in draft mode. Publish in Freshdesk and redeploy." + Fore.RESET)
        return

    print "Article " + article_id + " has been updated"


def _article_json(title, description):
    if not (title and description):
        raise ValueError
    return {
            "title": title,
            "description": description,
            "status": 2
          }

if __name__ == '__main__':
    # Get cloudfront url.
    try:
        cloudfront_url = os.environ["FRESHDESK_CLOUDFRONT_URL"]
    except KeyError:
        print(Fore.RED + "Please set the environment variable FRESHDESK_CLOUDFRONT_URL" + Fore.RESET)
        sys.exit(1)

    # Get freshdesk domain.
    try:
        domain = os.environ["FRESHDESK_DOMAIN"]
    except KeyError:
        print(Fore.RED + "Please set the environment variable FRESHDESK_DOMAIN" + Fore.RESET)
        sys.exit(1)

    # Get password.
    try:
        api_key = os.environ["FRESHDESK_API_KEY"]
    except KeyError:
        print(Fore.RED + "Please set the environment variable FRESHDESK_API_KEY" + Fore.RESET)
        sys.exit(1)

    # Check for articles that were posted directly on Freshdesk instead of locally.
    freshdesk = API(domain, api_key)

    compare_repos.compare_article_ids(freshdesk)

    if len(sys.argv) == 2:
        print (Fore.MAGENTA + "Processing Article 1/1" + Fore.RESET)
        main(sys.argv[1], freshdesk, cloudfront_url)
    else:
        articles = glob.glob("posts/*/*/*")
        i = 1
        for article in articles:
            article_id = article.split("/")[-1]
            print (Fore.MAGENTA + "Processing Article %s/%s %s" % (str(i), len(articles), article_id) + Fore.RESET)
            main(article_id, freshdesk, cloudfront_url)
            i += 1

    print "="*40
    print(Fore.GREEN + "SUCCESSFULLY FINISHED DEPLOYMENT" + Fore.RESET)
