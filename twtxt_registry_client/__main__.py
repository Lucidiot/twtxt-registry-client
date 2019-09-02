#!/usr/bin/env python3
from urllib.parse import urlsplit, urlunsplit
import click
from twtxt.config import Config
from twtxt_registry_client import RegistryClient


@click.group(name='twtxt-registry')
@click.argument('registry_url', required=True)
@click.version_option()
@click.option('-k', '--insecure', is_flag=True)
@click.pass_context
def cli(ctx, registry_url, insecure):
    scheme, netloc, path, query, fragment = urlsplit(registry_url)
    if not scheme:
        scheme = 'https'
    if not netloc and path:
        netloc, _, path = path.partition('/')
    registry_url = urlunsplit((scheme, netloc, path, query, fragment))
    ctx.obj = RegistryClient(registry_url, insecure=insecure)


@cli.command()
@click.option(
    '-n', '--nickname',
    help='Nickname to register with. '
         'Defaults to the configured twtxt nickname, if available.',
)
@click.option(
    '-u', '--url',
    help='URL to the twtxt file to register with. '
         'Defaults to the configured twtxt URL, if available.',
)
@click.pass_context
def register(ctx, nickname, url):
    if not nickname or not url:
        try:
            config = Config.discover()
        except ValueError as e:
            raise click.UsageError(
                'Nickname or URL were omitted from the command-line, but they'
                'could not be deduced from the twtxt config: {!s}'.format(e),
                ctx=ctx,
            )
        nickname = nickname or config.nick
        url = url or config.twturl

    click.echo(ctx.obj.register(nickname, url).text)


@cli.command()
@click.option('-q', '--query')
@click.pass_context
def users(ctx, query):
    click.echo(ctx.obj.list_users(q=query).text)


@cli.command()
@click.option('-q', '--query')
@click.pass_context
def tweets(ctx, query):
    click.echo(ctx.obj.list_tweets(q=query).text)


@cli.command()
@click.argument('name_or_url', required=False)
@click.pass_context
def mentions(ctx, name_or_url):
    if name_or_url:
        scheme = urlsplit(name_or_url).scheme
        if not scheme:  # it could be a nick
            try:
                config = Config.discover()
            except ValueError:
                pass
            else:
                source = config.get_source_by_nick(name_or_url)
                if source:
                    url = source.url
        url = url or name_or_url  # Fallback
    else:
        try:
            config = Config.discover()
        except ValueError as e:
            raise click.UsageError(
                'URL was omitted from the command-line, but it could not '
                'be deduced from the twtxt config: {!s}'.format(e),
                ctx=ctx,
            )
        url = config.twturl

    click.echo(ctx.obj.list_mentions(url).text)


@cli.command()
@click.argument('name', required=True)
@click.pass_context
def tag(ctx, name):
    click.echo(ctx.obj.list_tag_tweets(name).text)


if __name__ == '__main__':
    cli()
