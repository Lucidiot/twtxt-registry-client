from typing import Optional, Callable, Any
import logging
import urllib.parse
import click
import requests

logger = logging.getLogger(__name__)


class RegistryClient(object):
    """
    The twtxt registry API client.
    """

    def __init__(self,
                 registry_url: str,
                 insecure: bool = False,
                 disclose_identity: Optional[bool] = None):
        """
        :param str registry_url: Base URL for the registry API.
        :param bool insecure: Disable SSL certificate checks
        :param disclose_identity:
           Enable or disable identity disclosure;
           this appends the User-Agent header with the twtxt local
           username and URL, deduced from the twtxt configuration
        :type disclose_identity: bool or None
        """
        self.registry_url = registry_url
        self.session = requests.Session()
        self.session.verify = not insecure

        from twtxt_registry_client import __version__
        if disclose_identity or disclose_identity is None:
            logger.debug('Looking up identity disclosure configuration')
            config = click.get_current_context().obj.conf
            disclose_identity = config.disclose_identity

        if disclose_identity:
            logger.debug('disclose_identity is enabled')
            user_agent = 'twtxt-registry/{} (+{}; @{})'.format(
                __version__,
                config.twturl,
                config.nick,
            )
        else:
            logger.debug(
                'Configuration not found or disclose_identity is disabled')
            user_agent = 'twtxt-registry/{}'.format(__version__)

        logger.debug('Using user agent {!r}'.format(user_agent))
        self.session.headers['User-Agent'] = user_agent

    def request(self,
                method: Callable,
                endpoint: str,
                *,
                format: str = 'plain',
                raise_exc: bool = True,
                **params: Any) -> requests.Response:
        """
        Perform an API request.

        :param Callable method: A ``requests`` request method.
        :param str endpoint:
           An endpoint path;
           will be appended to the registry URL and the format.
        :param str format:
           The response format, as defined in
           the twtxt registry API specification.
        :param bool raise_exc:
           Raise :exc:`requests.exceptions.HTTPError`
           for HTTP errors.
        :param \\**params: Query parameters to send in the request URL.
        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        :raises requests.HTTPError:
           When ``raise_exc`` is ``True`` and the response has
           an HTTP 4xx or 5xx status code.
        """
        # Ignore parameters with None values
        params = {k: v for k, v in params.items() if v}
        resp = method(
            '/'.join([self.registry_url, format, endpoint]),
            params=params,
        )
        logger.debug('{} request to {}'.format(resp.request.method, resp.url))
        logger.debug('HTTP {} {}'.format(resp.status_code, resp.reason))
        logger.debug('Response body: {!r}'.format(resp.text))
        if raise_exc:
            resp.raise_for_status()
        return resp

    def get(self, *args: Any, **kwargs: Any) -> requests.Response:
        """
        Perform a GET request.
        Passes all arguments to :meth:`RegistryClient.request`.

        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        """
        return self.request(self.session.get, *args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> requests.Response:
        """
        Perform a POST request.
        Passes all arguments to :meth:`RegistryClient.request`.

        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        """
        return self.request(self.session.post, *args, **kwargs)

    def register(self,
                 nickname: str,
                 url: str,
                 **kwargs: Any) -> requests.Response:
        """
        Register a new user.

        :param str nickname: Nickname of the user.
        :param str url: Profile URL of the user.
        :param \\**kwargs:
           Keyword arguments sent to :meth:`RegistryClient.request`.
        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        """
        return self.post('users', nickname=nickname, url=url, **kwargs)

    def list_users(self, *,
                   q: Optional[str] = None,
                   **kwargs: Any) -> requests.Response:
        """
        List registered users.

        :param q: Optional query to filter users.
        :type q: str or None
        :param \\**kwargs:
           Keyword arguments sent to :meth:`RegistryClient.request`.
        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        """
        return self.get('users', q=q, **kwargs)

    def list_tweets(self, *,
                    q: Optional[str] = None,
                    **kwargs: Any) -> requests.Response:
        """
        List tweets from registered users.

        :param q: Optional query to filter tweets.
        :type q: str or None
        :param \\**kwargs:
           Keyword arguments sent to :meth:`RegistryClient.request`.
        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        """
        return self.get('tweets', q=q, **kwargs)

    def list_mentions(self, url: str, **kwargs: Any) -> requests.Response:
        """
        List tweets mentioning a given user.

        :param str url: Profile URL of the user to list mentions of.
        :param \\**kwargs:
           Keyword arguments sent to :meth:`RegistryClient.request`.
        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        """
        return self.get('mentions', url=url, **kwargs)

    def list_tag_tweets(self, name: str, **kwargs: Any) -> requests.Response:
        """
        List tweets with a given tag.

        :param str name: Name of the tag to look for.
        :param \\**kwargs:
           Keyword arguments sent to :meth:`RegistryClient.request`.
        :returns: An HTTP response.
        :rtype: requests.Response
        :raises requests.RequestException:
           For any error occuring when performing the request.
        """
        return self.get('tags/{}'.format(urllib.parse.quote(name)), **kwargs)
