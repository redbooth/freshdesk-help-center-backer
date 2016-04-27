import requests
from requests.exceptions import HTTPError


class API(object):
    def __init__(self, domain, api_key):
        """Creates a wrapper to perform API actions.
        Arguments:
          domain:    the Freshdesk domain (not custom). e.g. company.freshdesk.com
          api_key:   the API key
        """

        self._api_prefix = 'https://{}/'.format(domain.rstrip('/'))
        self._session = requests.Session()
        self._session.auth = (api_key, 'unused_with_api_key')
        self._session.headers = {'Content-Type': 'application/json'}

        self.domain = domain

        self.articles = ArticleAPI(self)
        self.folders = FolderAPI(self)
        self.categories = CategoryAPI(self)

    def get(self, url, params={}):
        response = self._session.get(self._api_prefix + url, params=params)
        response.raise_for_status()
        _handle_403_errors(response)
        return response.json()

    def post(self, url, data=None, json=None, params={}):
        response = self._session.post(self._api_prefix + url, data=data, json=json, params=params)
        response.raise_for_status()
        _handle_403_errors(response)
        return response.json()

    def put(self, url, data=None, json=None, params={}):
        response = self._session.put(self._api_prefix + url, data=data, json=json, params=params)
        response.raise_for_status()
        _handle_403_errors(response)
        return response.json()

    def delete(self, url, params={}):
        response = self._session.delete(self._api_prefix + url, params=params)
        response.raise_for_status()
        _handle_403_errors(response)
        return response.json()


class ArticleAPI(object):

    def __init__(self, api):
        self._api = api

    def get_article(self, article_id, folder_id, category_id):
        url = "solution/categories/{}/folders/{}/articles/{}.json".format(category_id, folder_id, article_id)
        return self._api.get(url)['article']

    def create_article(self, folder_id, category_id, article={}, tags=[]):
        payload_folder_id = article['folder_id']
        if not payload_folder_id == folder_id:
            raise ValueError
        url = "solution/categories/{}/folders/{}/articles.json".format(category_id, folder_id)
        data = {"solution_article": article}
        if len(tags) > 0:
            data["tags"] = {"name": ", ".join(tags)}
        return self._api.post(url, json=data)['article']

    def update_article(self, article_id, folder_id, category_id, article={}, tags=[]):
        url = "solution/categories/{}/folders/{}/articles/{}.json".format(category_id, folder_id, article_id)
        data = {"solution_article": article}
        if len(tags) > 0:
            data["tags"] = {"name": ", ".join(tags)}
        return self._api.put(url, json=data)['article']

    def get_all_folder_category_articles(self, folder_id, category_id):
        url = "/solution/categories/{}/folders/{}.json".format(category_id, folder_id)
        return self._api.get(url)

    def get_all_articles(self):
        articles = []
        _get_all_articles(articles, self._api)
        return articles


class FolderAPI(object):

    def __init__(self, api):
        self._api = api

    def get_folder(self, folder_id, category_id):
        url = "/solution/categories/{}/folders/{}.json".format(category_id, folder_id)
        return self._api.get(url)['folder']


class CategoryAPI(object):

    def __init__(self, api):
        self._api = api

    def get_category(self, category_id):
        url = "/solution/categories/{}.json".format(category_id)
        return self._api.get(url)['category']

    def get_categories(self):
        url = "/solution/categories.json"
        return self._api.get(url)


def _get_all_articles(articles, api):
    categories = CategoryAPI(api).get_categories()
    for category in categories:
        category_id = category['category']['id']
        folders = category['category']['folders']
        for folder in folders:
            folder_id = folder['id']
            remote_articles = ArticleAPI(api).get_all_folder_category_articles(folder_id, category_id)['folder']['articles']
            for article in remote_articles:
                article['parent_id'] = category_id
            articles.extend(remote_articles)


def _handle_403_errors(response):
    if 'Retry-After' in response.headers:
        raise HTTPError('403 Forbidden: API rate-limit has been reached until {}.' \
                'See http://freshdesk.com/api#ratelimit'.format(response.headers['Retry-After']))
    j = response.json()
    if 'require_login' in j:
        raise HTTPError('403 Forbidden: API key is incorrect for this domain')