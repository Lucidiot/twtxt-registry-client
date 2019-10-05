from abc import ABCMeta, abstractmethod
from datetime import datetime, timezone
from objtools.registry import ClassRegistry
from twtxt.mentions import format_mentions
from twtxt.parser import parse_iso8601
import click
import json
import logging
import humanize
import requests
import textwrap

logger = logging.getLogger(__name__)


class FormatterRegistry(ClassRegistry):
    """
    The class that holds registered formatters; allows registering a formatter
    automatically by merely importing it.

    You should not have to use this class directly; use the already
    instanciated :data:`registry` in this module instead.
    """

    def check_value(self, value: type) -> None:
        """
        Ensure that a new formatter class subclasses :class:`Formatter`.

        :param Callable value: A formatter subclass.
        :raises AssertionError:
           When the formatter subclass does not subclass :class:`Formatter`.
        """
        assert issubclass(value, Formatter), 'Can only register formatters'


registry = FormatterRegistry()
"""
The formatter registry: an enhanced ``dict`` which holds links between
formatter names (used in the ``--format`` command-line argument) and formatter
classes.
"""


class FormatterMetaclass(registry.metaclass, ABCMeta):  # type: ignore
    """
    The metaclass which allows auto-registration of each formatter.
    In most cases, you should not have to use this class directly;
    use the :class:`Formatter` abstract class instead.
    Registration of classes that do not subclass :class:`Formatter` will fail.
    """


class Formatter(metaclass=FormatterMetaclass, register=False):
    """
    Abstract base class for output formatters.

    When creating a new subclass, you may specify some parameters to pass to
    the auto-registration system::

       class MyFormatter(key='something'):
           pass

       class MyInvisibleFormatter(register=False):
           pass

    In the above example, ``MyFormatter`` can be used in the command line
    client using ``twtxt-registry -f something``, and MyInvisibleFormatter
    will not be visible directly (which is useful for abstract classes).

    ``register`` defaults to ``True``, and ``key`` defaults to the class name.
    """
    # TODO: Add link to objtools docs here once they are published

    @abstractmethod
    def format_response(self, resp: requests.Response) -> str:
        """
        Generic output for an HTTP response: generally, this would include
        the HTTP status code and the response body. This is used to output
        HTTP errors or basic requests which do not have a very meaningful
        response body, like the registration API.

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the formatter's output.
        :rtype: str
        """

    @abstractmethod
    def format_tweets(self, resp: requests.Response) -> str:
        """
        Output tweets from a successful HTTP response. The tweets can be
        obtained from ``resp.text`` and parsing of the response text is left
        to the formatter.

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the formatter's output.
        :rtype: str
        """

    @abstractmethod
    def format_users(self, resp: requests.Response) -> str:
        """
        Output users from a successful HTTP response. The users can be obtained
        from ``resp.text`` and parsing of the response text is left to the
        formatter.

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the formatter's output.
        :rtype: str
        """


class RawFormatter(Formatter, key='raw'):
    """
    A very basic formatter which always outputs the response's body directly.

    Use ``-f raw`` or ``--format raw`` in the CLI to select it.
    """

    def format_response(self, resp: requests.Response) -> str:
        return resp.text

    def format_tweets(self, resp: requests.Response) -> str:
        return resp.text

    def format_users(self, resp: requests.Response) -> str:
        return resp.text


class JSONFormatter(Formatter, key='json'):
    """
    A formatter which always returns valid JSON documents.

    Use ``-f json`` or ``--format json`` in the CLI to select it.
    """

    def format_response(self, resp: requests.Response) -> str:
        """
        Outputs a simple JSON payload for any HTTP response, including its
        HTTP status code, its URL and its body.
        Sample output with a 404 error::

           {
               "status_code": 404,
               "url": "http://somewhere/api/not/found",
               "body": "Page Not Found!"
           }

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the JSON output.
        :rtype: str
        """
        return json.dumps({
            'status_code': resp.status_code,
            'url': resp.url,
            'body': resp.text,
        })

    def format_tweets(self, resp: requests.Response) -> str:
        """
        Outputs a list of JSON objects for an HTTP response holding tweets,
        with the users' nickname and URL, the tweet's timestamp, and its
        content. Sample output::

           [
               {
                   "nick": "lucidiot",
                   "url": "https://tilde.town/~lucidiot/twtxt.txt",
                   "timestamp": "2019-02-31T13:37:42.123456Z",
                   "message": "Hello, world!"
               }
           ]

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the JSON output.
        :rtype: str
        """
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

    def format_users(self, resp: requests.Response) -> str:
        """
        Outputs a list of JSON objects for an HTTP response holding users,
        with their nickname, URL, and last update timestamp. Sample output::

           [
               {
                   "nick": "lucidiot",
                   "url": "https://tilde.town/~lucidiot/twtxt.txt",
                   "timestamp": "2019-02-31T13:37:42.123456Z"
               }
           ]

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the JSON output.
        :rtype: str
        """
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
    """
    A formatter with pretty-printing for beautiful command line output.

    This is the default formatter; Use ``-f pretty`` or ``--format pretty``
    in the CLI to explicitly select it.
    """

    status_colors = {
        1: 'white',
        2: 'green',
        3: 'cyan',
        4: 'red',
        5: 'magenta',
    }

    def format_response(self, resp: requests.Response) -> str:
        """
        Outputs an HTTP response in a syntax similar to a true HTTP response,
        with its status code, reason and body:

           HTTP **404 Not Found**

           Page Not Found!

        The HTTP status code may be coloured if the terminal supports it:
        white for 1xx, green for 2xx, cyan for 3xx, red for 4xx and magenta
        for 5xx.

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the human-readable output.
        :rtype: str
        """
        return 'HTTP {code} {name}\n\n{body}'.format(
            code=click.style(
                str(resp.status_code),
                fg=self.status_colors.get(resp.status_code // 100),
                bold=True,
            ),
            name=click.style(resp.reason, bold=True),
            body=resp.text,
        )

    def format_tweets(self, resp: requests.Response) -> str:
        """
        Outputs an HTTP response as a list of tweets, in a format similar to
        the output of the original ``twtxt`` CLI.

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the human-readable output.
        :rtype: str
        """
        if not resp.ok:
            return self.format_response(resp)

        # Try to determine the configured character limit and time display
        logger.debug(
            'Trying to load pretty printing options from twtxt configuration')
        conf = click.get_current_context().obj.conf
        abs_time = conf.get('use_abs_time', False)
        limit = conf.get('character_limit')
        logger.debug(
            'Using {} time'.format('absolute' if abs_time else 'relative'))
        logger.debug('Character limit: {!r}'.format(limit))

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

    def format_users(self, resp: requests.Response) -> str:
        """
        Outputs an HTTP response as a list of users, in a format similar to
        the output of the original ``twtxt`` CLI.

        :param resp:
           A requests ``Response`` instance from an API request to a registry.
        :type resp: requests.Response
        :returns: A string holding the human-readable output.
        :rtype: str
        """
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
