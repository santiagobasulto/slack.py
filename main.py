import click
from api import HighLevelSlackClient as SlackClient


def yes_no(option, capitalized=True):
    answer = 'Yes' if option else 'No'
    return answer.lower() if not capitalized else answer


def default_options(**kwargs):
    return {k: v for k, v in kwargs.items() if v}


@click.group()
@click.option('-a', '--token', required=True, envvar='SLACK_TOKEN')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def slack(ctx, token, debug):
    ctx.obj['DEBUG'] = debug
    ctx.obj['TOKEN'] = token
    ctx.obj['client'] = SlackClient(token)


HEADER = ("|{id:^15}|{name:^30}|{archived:^12}|{general:^12}|"
          "{private:^12}|{members:^12}")


@slack.command()
@click.option('-r', '--exclude-archived', is_flag=True, default=False)
@click.option('-s', '--starts-with', type=str)
@click.option('-c', '--contains', type=str)
@click.option('--delete', is_flag=True, default=False)
@click.option('--archive', is_flag=True, default=False)
@click.option('--dry-run', is_flag=True, default=False)
@click.pass_context
def list_channels(ctx, exclude_archived, starts_with,
                  contains, delete, archive, dry_run):
    if all([delete, archive]):
        ctx.fail("You can't set both --delete and --archive.")
    if delete:
        click.confirm(
            'Are you sure you want to delete these channels?', abort=True)
    if archive:
        click.confirm(
            'Are you sure you want to archive these channels?', abort=True)

    client = ctx.obj['client']
    channels = client.channels(**default_options(
        exclude_archived=exclude_archived,
        starts_with=starts_with,
        contains=contains,
        exclude_members=True
    ))

    click.echo(HEADER.format(
        id='Channel ID', name='Channel Name', archived='Is Archived',
        general="Is General", private="Is Private", members="Nº Members"))

    for channel in channels:
        click.echo(HEADER.format(
            id=channel.id, name=channel.name,
            archived=yes_no(channel.is_archived),
            general=yes_no(channel.is_general),
            private=yes_no(channel.is_private),
            members=channel.num_members))


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
