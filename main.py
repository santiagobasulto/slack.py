import click

from slack_cli import HighLevelSlackClient as SlackClient
from slack_cli.utils import default_options
from slack_cli.cmd import (
    DEFAULT_SLEEP_IN_MILLISECONDS, ListChannels, DeleteChannels,
    ArchiveChannels)


@click.group()
@click.option('-a', '--token', required=True, envvar='SLACK_API_TOKEN')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def slack(ctx, token, debug):
    ctx.obj['DEBUG'] = debug
    ctx.obj['TOKEN'] = token
    ctx.obj['client'] = SlackClient(token)


@slack.command()
@click.pass_context
def auth_test(ctx):
    def __msg(label, value, fg='blue', bold=True):
        msg = click.style("{:<10}: ".format(label), fg=fg, bold=bold)
        msg += click.style(value, reset=True)
        return msg

    client = ctx.obj['client']

    resp = client.auth_test(fail=False)
    if resp['ok']:
        click.secho('... OK ...', fg='green', )
        click.echo(
            __msg('Team', "{:} - ({:})".format(resp['team'], resp['team_id'])))
        click.echo(__msg('URL', resp['url']))
        click.echo(
            __msg('User', "{:} - ({:})".format(resp['user'], resp['user_id'])))
    else:
        msg = click.style('FAILED', fg='red', bold=True)
        msg += click.style(' -- {}'.format(resp['error']), reset=True)
        click.secho(msg)


@slack.command()
@click.option('-i', '--id', type=str)
@click.option('-r', '--exclude-archived', is_flag=True, default=False)
@click.option('-s', '--starts-with', type=str)
@click.option('-c', '--contains', type=str)
@click.option('-n', '--name', type=str)
@click.option('--delete', is_flag=True, default=False)
@click.option('--archive', is_flag=True, default=False)
@click.option('--dry-run', is_flag=True, default=False)
@click.option(
    '--sleep', type=int, default=DEFAULT_SLEEP_IN_MILLISECONDS,
    help='Sleep time for Slack Rate API - in Milliseconds')
@click.pass_context
def channels(ctx, id, exclude_archived, starts_with,
             contains, name, delete, archive, dry_run, sleep):
    subcommand = 'list'
    subcommand_classes = {
        'list': ListChannels,
        'delete': DeleteChannels,
        'archive': ArchiveChannels
    }

    if all([delete, archive]):
        ctx.fail("You can't set both --delete and --archive.")

    if delete:
        click.confirm(
            'Are you sure you want to delete these channels?', abort=True)
        subcommand = 'delete'
    if archive:
        click.confirm(
            'Are you sure you want to archive these channels?', abort=True)
        subcommand = 'archive'

    client = ctx.obj['client']
    channels = client.channels(**default_options(
        id=id,
        name=name,
        exclude_archived=exclude_archived,
        starts_with=starts_with,
        contains=contains,
        exclude_members=True
    ))

    SubcommandClass = subcommand_classes[subcommand]
    cmd = SubcommandClass(
        client, channels, dry_run=dry_run, sleep=sleep)
    cmd.execute()


def main():
    slack(obj={})


if __name__ == '__main__':
    main()
