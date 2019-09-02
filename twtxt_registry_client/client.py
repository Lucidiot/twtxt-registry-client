import urllib
import requests


class RegistryClient(object):

    def __init__(self, registry_url):
        self.registry_url = registry_url

    def request(self, method, endpoint, *, format='plain', **params):
        resp = method(
            '/'.join([self.registry_url, format, endpoint]),
            # Ignore parameters with None values
            params={k: v for k, v in params.items() if v},
        )
        resp.raise_for_status()
        return resp

    def get(self, *args, **kwargs):
        return self.request(requests.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request(requests.post, *args, **kwargs)

    def register(self, nickname, url, *, format='plain'):
        return self.post(
            'users',
            format=format,
            nickname=nickname,
            url=url,
        )

    def list_users(self, *, q=None, format='plain'):
        return self.get(
            'users',
            q=q,
            format=format,
        )

    def list_tweets(self, *, q=None, format='plain'):
        return self.get(
            'tweets',
            q=q,
            format=format,
        )

    def list_mentions(self, url, *, format='plain'):
        return self.get(
            'mentions',
            url=url,
            format=format,
        )

    def list_tag_tweets(self, name, *, format='plain'):
        return self.get(
            'tags/{}'.format(urllib.quote(name)),
            format=format,
        )
