#!/usr/bin/env python3
from urllib.parse import urlsplit, urlunsplit
import click
from twtxt_registry_client import RegistryClient


@click.group(name='twtxt-registry')
@click.argument('registry_url', required=True)
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
@click.argument('nickname', required=True)
@click.argument('url', required=True)
@click.pass_context
def register(ctx, nickname, url):
    # TODO: Use twtxt's config to guess the user's info
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
@click.argument('url', required=True)
@click.pass_context
def mentions(ctx, url):
    # TODO: Allow names instead of URLs for known users
    # TODO: Use twtxt's config to default to the user's name
    click.echo(ctx.obj.list_mentions(url).text)


@cli.command()
@click.argument('name', required=True)
@click.pass_context
def tag(ctx, name):
    click.echo(ctx.obj.list_tag_tweets(name).text)


if __name__ == '__main__':
    cli()
