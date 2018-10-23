import json
from functools import partial
from slackclient import SlackClient


class HighLevelSlackAPIException(Exception):
    pass


class FailedRequestException(HighLevelSlackAPIException):
    pass


class Channel(object):
    def __init__(self, resp_data):
        self._resp_data = resp_data
        for key, value in resp_data.items():
            setattr(self, key, value)

    def __str__(self):
        return "%s (%s)" % (self.name, self.id)

    def __repr__(self):
        return "Channel(name=%s, id=%s)" % (self.name, self.id)


def filtered(fn):
    def wrapped(self, *args, **kwargs):
        self.filters = {}

        if self.FILTERS:
            for k, v in kwargs.items():
                if k in self.FILTERS:
                    self.filters[k] = partial(self.FILTERS[k], v)
            for k in self.filters:
                del kwargs[k]

        return fn(self, *args, **kwargs)

    return wrapped


class Filter(object):
    pass


class HighLevelSlackClient(object):
    # A `filter` is a callable that receives:
    # p: The parameter passed by the user
    # c: The channel (raw json)
    # and must return True if the channel passes the filter
    # or `False` to drop it. Similar to `builtins.filter`

    FILTERS = {
        'id': lambda p, c: c['id'] == p,
        'name': lambda p, c: c['name'] == p,
        'only_archived': lambda p, c: c['is_archived'],
        'is_archived': lambda p, c: c['is_archived'] is p,
        'starts_with': lambda p, c: c['name'].startswith(p)
    }

    def __init__(self, *args, **kwargs):
        self._client = SlackClient(*args, **kwargs)

    def __request(self, method, **kwargs):
        fail = kwargs.setdefault('fail', True)
        del kwargs['fail']

        resp = self._client.api_call(method, **kwargs)

        if not resp['ok'] and fail:
            raise FailedRequestException('`{}` request failed'.format(method))

        return resp

    def auth_test(self, **kwargs):
        resp = self.__request('auth.test', **kwargs)
        return resp

    @filtered
    def channels(self, **kwargs):
        resp = self.__request('channels.list', **kwargs)

        for channel in resp['channels']:
            for filter in self.filters.values():
                if not filter(channel):
                    break
            else:
                yield Channel(channel)
