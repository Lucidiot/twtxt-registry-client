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

    def request(self, method, endpoint,
                *, format='plain', raise_exc=True, **params):
        resp = method(
            '/'.join([self.registry_url, format, endpoint]),
            # Ignore parameters with None values
            params={k: v for k, v in params.items() if v},
        )
        if raise_exc:
            resp.raise_for_status()
        return resp

    def get(self, *args, **kwargs):
        return self.request(self.session.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request(self.session.post, *args, **kwargs)

    def register(self, nickname, url, **kwargs):
        return self.post('users', nickname=nickname, url=url, **kwargs)

    def list_users(self, *, q=None, **kwargs):
        return self.get('users', q=q, **kwargs)

    def list_tweets(self, *, q=None, **kwargs):
        return self.get('tweets', q=q, **kwargs)

    def list_mentions(self, url, **kwargs):
        return self.get('mentions', url=url, **kwargs)

    def list_tag_tweets(self, name, **kwargs):
        return self.get('tags/{}'.format(urllib.parse.quote(name)), **kwargs)
