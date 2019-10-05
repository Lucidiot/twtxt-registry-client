#!/usr/bin/env python3
from urllib.parse import urlsplit, urlunsplit
from objtools.collections import Namespace
from requests.exceptions import HTTPError
from typing import Optional
from twtxt.config import Config
from twtxt_registry_client import RegistryClient, output
import click
import logging

logger = logging.getLogger(__name__)


@click.group(name='twtxt-registry')
@click.argument('registry_url', required=True)
@click.version_option('-V', '--version')
@click.option(
    '-k', '--insecure',
    is_flag=True,
    help='Disable SSL certificate checks.',
)
@click.option(
    '-f', '--format',
    type=click.Choice(output.registry.keys()),
    default='pretty',
    help='Change the output format.',
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Output logs to stderr for debugging purposes.',
)
@click.pass_context
def cli(ctx: click.Context,
        registry_url: str,
        insecure: bool,
        format: str,
        verbose: bool) -> None:
    """
    Command-line client for the twtxt registry API.

    Takes a mandatory registry URL argument, as the base API URL
    (ex. https://registry.twtxt.org/api)
    """
    if verbose:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s/%(name)s] %(message)s',
            level=logging.DEBUG,
        )

    ctx.obj = Namespace()

    try:
        ctx.obj.conf = Config.discover()
    except ValueError as e:
        logger.debug('Could not load the twtxt configuration: {!s}'.format(e))
        ctx.obj.conf = Namespace()

    scheme, netloc, path, query, fragment = urlsplit(registry_url)
    if not scheme:
        scheme = 'https'
    if not netloc and path:
        netloc, _, path = path.partition('/')
    registry_url = urlunsplit((scheme, netloc, path, query, fragment))

    logger.debug('Using registry URL {}'.format(registry_url))
    if insecure:
        logger.debug('SSL certificate checks are disabled')
    ctx.obj.client = RegistryClient(registry_url, insecure=insecure)

    ctx.obj.formatter = output.registry[format]()
    logger.debug('Using formatter {!r}'.format(ctx.obj.formatter))


@cli.command()
@click.option(
    '-n', '--nickname',
    help='Nickname to register with. '
         'Defaults to the configured twtxt nickname, if available.',
    metavar='[NICK]',
)
@click.option(
    '-u', '--url',
    help='URL to the twtxt file to register with. '
         'Defaults to the configured twtxt URL, if available.',
    metavar='[URL]',
)
@click.pass_context
def register(ctx: click.Context,
             nickname: Optional[str],
             url: Optional[str]) -> None:
    """
    Register a user on a registry.
    """
    if not nickname or not url:
        logger.debug(
            'Nickname or URL were omitted; trying to deduce from '
            'the twtxt configuration'
        )
        if not ctx.obj.conf:
            raise click.UsageError(
                'Nickname or URL were omitted from the command-line, but they '
                'could not be deduced from the twtxt config.',
                ctx=ctx,
            )
        nickname = nickname or ctx.obj.conf.nick
        url = url or ctx.obj.conf.twturl
        logger.debug('Using nick {!r} and URL {!r}'.format(nickname, url))

    click.echo(ctx.obj.formatter.format_response(
        ctx.obj.client.register(nickname, url, raise_exc=False)
    ))


@cli.command()
@click.option(
    '-q', '--query',
    help='An optional search query to filter users.',
)
@click.pass_context
def users(ctx: click.Context, query: Optional[str]) -> None:
    """
    List and search users on a registry.
    """
    try:
        click.echo(ctx.obj.formatter.format_users(
            ctx.obj.client.list_users(q=query)
        ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


@cli.command()
@click.option(
    '-q', '--query',
    help='An optional search query to filter tweets.',
)
@click.pass_context
def tweets(ctx: click.Context, query: Optional[str]) -> None:
    """
    List and search tweets on a registry.
    """
    try:
        click.echo(ctx.obj.formatter.format_tweets(
            ctx.obj.client.list_tweets(q=query)
        ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


@cli.command()
@click.argument('name_or_url', required=False)
@click.pass_context
def mentions(ctx: click.Context, name_or_url: Optional[str]) -> None:
    """
    List mentions to someone on a registry.

    Without arguments, will try to use twtxt's configured URL to list your own
    mentions.
    """
    if name_or_url:
        logger.debug('Parsing the name/URL argument')
        scheme = urlsplit(name_or_url).scheme
        if ctx.obj.conf and not scheme:  # it could be a nick
            logger.debug(
                'Argument could be a nickname; '
                'trying to deduce from the twtxt configuration'
            )
            source = ctx.obj.conf.get_source_by_nick(name_or_url)
            if source:
                logger.debug('Found source {!r} with URL {!r}'.format(
                    source.nick, source.url))
                url = source.url
            else:
                logger.debug(
                    'No source found from twtxt configuration; '
                    'assuming argument is a URL'
                )
        url = url or name_or_url  # Fallback
    else:
        logger.debug(
            'URL was omitted; trying to deduce from the twtxt configuration')
        if not ctx.obj.conf:
            raise click.UsageError(
                'URL was omitted from the command-line, but it could not '
                'be deduced from the twtxt config.',
                ctx=ctx,
            )
        url = ctx.obj.conf.twturl

    logger.debug('Using URL {}'.format(url))

    try:
        click.echo(ctx.obj.formatter.format_tweets(
            ctx.obj.client.list_mentions(url)
        ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


@cli.command()
@click.argument('name', required=True)
@click.pass_context
def tag(ctx: click.Context, name: str) -> None:
    """
    Search for tweets containing a tag.

    Requires a tag name as a positional argument.
    """
    try:
        click.echo(ctx.obj.formatter.format_tweets(
            ctx.obj.client.list_tag_tweets(name)
        ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


if __name__ == '__main__':
    cli()
