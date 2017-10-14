import time
import click

from .utils import yes_no

DEFAULT_SLEEP_IN_MILLISECONDS = 10000


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
