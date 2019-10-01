from abc import ABCMeta, abstractmethod
from datetime import datetime, timezone
from objtools.registry import ClassRegistry
from twtxt.mentions import format_mentions
from twtxt.parser import parse_iso8601
import click
import json
import humanize
import textwrap


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


class PrettyFormatter(Formatter, key='pretty'):

    status_colors = {
        1: 'white',
        2: 'green',
        3: 'cyan',
        4: 'red',
        5: 'magenta',
    }

    def format_response(self, resp):
        return 'HTTP {code} {name}\n\n{body}'.format(
            code=click.style(
                str(resp.status_code),
                fg=self.status_colors.get(resp.status_code // 100),
                bold=True,
            ),
            name=click.style(resp.reason, bold=True),
            body=resp.text,
        )

    def format_tweets(self, resp):
        if not resp.ok:
            return self.format_response(resp)

        # Try to determine the configured character limit and time display
        conf = click.get_current_context().obj.conf
        abs_time = conf.get('use_abs_time', False)
        limit = conf.get('character_limit')
        # Prevent AttributeErrors when using twtxt.helper.format_mentions
        conf.setdefault('twturl', None)
        conf.setdefault('following', [])

        output = []
        for tweet in resp.text.splitlines():
            # Mostly taken from twtxt.helper.style_tweet
            nick, url, timestamp, message = tweet.split('\t', maxsplit=3)
            if limit:
                styled = format_mentions(message)
                len_styling = len(styled) - len(click.unstyle(styled))
                message = textwrap.shorten(styled, limit + len_styling)
            else:
                message = format_mentions(message)

            dt = parse_iso8601(timestamp)
            if abs_time:
                timestamp = dt.strftime('%c')
                tense = None
            else:
                now = datetime.now(timezone.utc)
                timestamp = humanize.naturaldelta(now - dt)
                tense = 'from now' if dt > now else 'ago'

            output.append(
                '➤ {nick} @ {url} ({timestamp} {tense}):\n{message}'.format(
                    nick=click.style(nick, bold=True),
                    url=url,
                    timestamp=timestamp,
                    tense=tense,
                    message=message,
                )
            )

        return '\n\n'.join(output)

    def format_users(self, resp):
        if not resp.ok:
            return self.format_response(resp)
        output = []
        for user in resp.text.splitlines():
            nick, url, timestamp = user.split('\t', maxsplit=2)
            dt = parse_iso8601(timestamp)
            output.append(
                '➤ {nick} @ {url} (last updated on {timestamp})'.format(
                    nick=click.style(nick, bold=True),
                    url=url,
                    timestamp=dt.strftime('%c'),
                )
            )
        return '\n'.join(output)
