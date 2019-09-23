from abc import ABCMeta, abstractmethod
from objtools.registry import ClassRegistry
import json


class FormatterRegistry(ClassRegistry):

    def check_value(self, value):
        assert issubclass(value, Formatter), 'Can only register formatters'


registry = FormatterRegistry()


class FormatterMetaclass(registry.metaclass, ABCMeta):
    pass


class Formatter(metaclass=FormatterMetaclass, register=False):

    @abstractmethod
    def format_response(self, resp):
        pass

    @abstractmethod
    def format_tweets(self, resp):
        pass

    @abstractmethod
    def format_users(self, resp):
        pass


class RawFormatter(Formatter, key='raw'):

    def format_response(self, resp):
        return resp.text

    def format_tweets(self, resp):
        return resp.text

    def format_users(self, resp):
        return resp.text


class JSONFormatter(Formatter, key='json'):

    def format_response(self, resp):
        return json.dumps({
            'status_code': resp.status_code,
            'url': resp.url,
            'body': resp.text,
        })

    def format_tweets(self, resp):
        if not resp.ok:
            return self.format_response(resp)
        output = []
        for tweet in resp.text.splitlines():
            nick, url, timestamp, message = tweet.split('\t', maxsplit=3)
            output.append({
                'nick': nick,
                'url': url,
                'timestamp': timestamp,
                'message': message,
            })
        return json.dumps(output)

    def format_users(self, resp):
        if not resp.ok:
            return self.format_response(resp)
        output = []
        for user in resp.text.splitlines():
            nick, url, timestamp = user.split('\t', maxsplit=2)
            output.append({
                'nick': nick,
                'url': url,
                'timestamp': timestamp,
            })
        return json.dumps(output)
