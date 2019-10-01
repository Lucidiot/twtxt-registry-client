#!/usr/bin/env python3
from urllib.parse import urlsplit, urlunsplit
from objtools.collections import Namespace
from requests.exceptions import HTTPError
from twtxt.config import Config
from twtxt_registry_client import RegistryClient, output
import click


@click.group(name='twtxt-registry')
@click.argument('registry_url', required=True)
@click.version_option('-V', '--version')
@click.option('-k', '--insecure', is_flag=True)
@click.option('-f', '--format',
              type=click.Choice(output.registry.keys()),
              default='raw')
@click.pass_context
def cli(ctx, registry_url, insecure, format):
    ctx.obj = Namespace()

    scheme, netloc, path, query, fragment = urlsplit(registry_url)
    if not scheme:
        scheme = 'https'
    if not netloc and path:
        netloc, _, path = path.partition('/')
    registry_url = urlunsplit((scheme, netloc, path, query, fragment))
    ctx.obj.client = RegistryClient(registry_url, insecure=insecure)

    ctx.obj.formatter = output.registry[format]()


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

    click.echo(ctx.obj.formatter.format_response(
        ctx.obj.client.register(nickname, url, raise_exc=False)
    ))


@cli.command()
@click.option('-q', '--query')
@click.pass_context
def users(ctx, query):
    try:
    click.echo(ctx.obj.formatter.format_users(
        ctx.obj.client.list_users(q=query)
    ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


@cli.command()
@click.option('-q', '--query')
@click.pass_context
def tweets(ctx, query):
    try:
    click.echo(ctx.obj.formatter.format_tweets(
        ctx.obj.client.list_tweets(q=query)
    ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


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

    try:
    click.echo(ctx.obj.formatter.format_tweets(
        ctx.obj.client.list_mentions(url)
    ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


@cli.command()
@click.argument('name', required=True)
@click.pass_context
def tag(ctx, name):
    try:
    click.echo(ctx.obj.formatter.format_tweets(
        ctx.obj.client.list_tag_tweets(name)
    ))
    except HTTPError as e:
        click.echo(ctx.obj.formatter.format_response(e.response))


if __name__ == '__main__':
    cli()
