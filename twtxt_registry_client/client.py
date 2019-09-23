import urllib
import requests
from twtxt.config import Config


class RegistryClient(object):

    def __init__(self, registry_url, insecure=False, disclose_identity=None):
        self.registry_url = registry_url
        self.session = requests.Session()
        self.session.verify = not insecure

        from twtxt_registry_client import __version__
        if disclose_identity or disclose_identity is None:
            try:
                config = Config.discover()
            except ValueError:
                disclose_identity = False
            else:
                disclose_identity = config.disclose_identity

        if disclose_identity:
            user_agent = 'twtxt-registry/{} (+{}; @{})'.format(
                __version__,
                config.twturl,
                config.nick,
            )
        else:
            user_agent = 'twtxt-registry/{}'.format(__version__)
        self.session.headers['User-Agent'] = user_agent

    def request(self, method, endpoint, *, format='plain', **params):
        resp = method(
            '/'.join([self.registry_url, format, endpoint]),
            # Ignore parameters with None values
            params={k: v for k, v in params.items() if v},
        )
        resp.raise_for_status()
        return resp

    def get(self, *args, **kwargs):
        return self.request(self.session.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request(self.session.post, *args, **kwargs)

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
            'tags/{}'.format(urllib.parse.quote(name)),
            format=format,
        )
