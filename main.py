import click
import time
from api import HighLevelSlackClient as SlackClient

DEFAULT_SLEEP_IN_MILLISECONDS = 10000


def yes_no(option, capitalized=True):
    answer = 'Yes' if option else 'No'
    return answer.lower() if not capitalized else answer


def default_options(**kwargs):
    return {k: v for k, v in kwargs.items() if v}


@click.group()
@click.option('-a', '--token', required=True, envvar='SLACK_API_TOKEN')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def slack(ctx, token, debug):
    ctx.obj['DEBUG'] = debug
    ctx.obj['TOKEN'] = token
    ctx.obj['client'] = SlackClient(token)


class ChannelSubCommand(object):
    def __init__(self, client, channels, **kwargs):
        self.client = client
        self.channels = channels
        self.extras = kwargs

    def echo(self, *args, **kwargs):
        return click.echo(*args, **kwargs)


class ListChannels(ChannelSubCommand):
    LINE_TEMPLATE = ("|{id:^15}|{name:^30}|{archived:^12}|{general:^12}|"
                     "{private:^12}|{members:^12}")

    def execute(self):
        header = self.LINE_TEMPLATE.format(
            id='Channel ID', name='Channel Name', archived='Is Archived',
            general="Is General", private="Is Private", members="Nº Members")
        self.echo(header)
        report = {
            'private': 0,
            'total': 0,
            'archived': 0
        }
        for channel in self.channels:
            report['total'] += 1
            if channel.is_archived:
                report['archived'] += 1
            if channel.is_private:
                report['private'] += 1

            self.echo(self.LINE_TEMPLATE.format(
                id=channel.id, name=channel.name,
                archived=yes_no(channel.is_archived),
                general=yes_no(channel.is_general),
                private=yes_no(channel.is_private),
                members=channel.num_members))

        self.echo('\n' + '=' * len(header))
        msg = click.style(str(report['total']), reset=True)
        msg += click.style(' total channels', fg='green', bold=True)
        msg += click.style('. %s' % report['archived'], reset=True)
        msg += click.style(' Archived', fg='blue', bold=True)
        msg += click.style('. %s' % report['private'], reset=True)
        msg += click.style(' Private', fg='red', bold=True)
        msg += click.style('.', reset=True)
        self.echo(msg)


class ActionChannelSubcommand(ChannelSubCommand):
    SLACK_API_METHOD = None
    TITLE_MESSAGE = None

    def __perform_action(self, channel, dry_run=False):
        if dry_run:
            return {'ok': True}

        resp = self.client._client.api_call(
            self.SLACK_API_METHOD, channel=channel.id)
        return resp

    def _report(self, success, failed):
        msg = click.style(str(len(success)), fg='green', bold=True)

        msg += click.style(' ok, ', reset=True)
        msg += click.style(str(len(failed)), fg='red', bold=True)
        msg += click.style(' failed.', reset=True)

        self.echo('\n' + msg)

    def execute(self):
        self.echo("==== {} ====".format(self.TITLE_MESSAGE))

        report = {
            'success': [],
            'failed': []
        }
        success, failed = report['success'], report['failed']

        def _log_report(channel, resp):
            msg = click.style('ok', fg='green')
            report_list = success
            if not resp['ok']:
                msg = click.style('failed', fg='red')
                report_list = failed

            click.echo('\t {}{}'.format(
                msg, click.style('...', reset=True)))

            report_list.append(channel)
        sleep_in_seconds = self.extras.get(
            'sleep', DEFAULT_SLEEP_IN_MILLISECONDS) / 1000.0

        for idx, channel in enumerate(self.channels):
            if idx != 0 and sleep_in_seconds > 0:
                time.sleep(sleep_in_seconds)

            self.echo("{id:<15} - {name:<30}".format(
                id=channel.id,
                name=channel.name))

            resp = self.__perform_action(
                channel, dry_run=self.extras.get('dry_run'))
            _log_report(channel, resp)

        self._report(success, failed)


class DeleteChannels(ActionChannelSubcommand):
    SLACK_API_METHOD = 'channels.delete'
    TITLE_MESSAGE = 'Deleting Channels'


class ArchiveChannels(ActionChannelSubcommand):
    SLACK_API_METHOD = 'channels.archive'
    TITLE_MESSAGE = 'Archiving Channels'


@slack.command()
@click.option('-r', '--exclude-archived', is_flag=True, default=False)
@click.option('-s', '--starts-with', type=str)
@click.option('-c', '--contains', type=str)
@click.option('--delete', is_flag=True, default=False)
@click.option('--archive', is_flag=True, default=False)
@click.option('--dry-run', is_flag=True, default=False)
@click.option(
    '--sleep', type=int, default=DEFAULT_SLEEP_IN_MILLISECONDS,
    help='Sleep time for Slack Rate API - in Milliseconds')
@click.pass_context
def list_channels(ctx, exclude_archived, starts_with,
                  contains, delete, archive, dry_run, sleep):
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
        exclude_archived=exclude_archived,
        starts_with=starts_with,
        contains=contains,
        exclude_members=True
    ))

    SubcommandClass = subcommand_classes[subcommand]
    cmd = SubcommandClass(
        client, channels, dry_run=dry_run, sleep=sleep)
    cmd.execute()


@slack.command()
@click.pass_context
def channel_info(ctx):
    click.echo('Info!')


@slack.command()
@click.pass_context
def channel_archive(ctx):
    client = ctx.obj['client']
    click.echo('Archive!')
    print()


@slack.command()
@click.pass_context
def channel_delete(ctx):
    click.echo('Channel Delete')


if __name__ == '__main__':
    slack(obj={})
