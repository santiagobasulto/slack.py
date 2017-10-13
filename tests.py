import pytest
import responses
from mock import MagicMock
from api import HighLevelSlackClient

TOKEN = 'XYZ'

CHANNELS_FIXTURE = {
    "ok": True,
    "channels": [
        {
          "id": "ID-CH-1",
          "name": "test-channel-1",
          "is_channel": True,
          "created": 1472598112,
          "creator": "U1TESTING",
          "is_archived": False,
          "is_general": False,
          "unlinked": 0,
          "name_normalized": "test-channel-1",
          "is_shared": False,
          "is_org_shared": False,
          "is_member": False,
          "is_private": False,
          "is_mpim": False,
          "members": [
            "U1TESTING",
            "U2TESTING",
            "U3TESTING",
          ],
          "topic": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "purpose": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "previous_names": [],
          "num_members": 3
        },
        {
          "id": "ID-CH-2",
          "name": "test-channel-2",
          "is_channel": True,
          "created": 1472598112,
          "creator": "U2TESTING",
          "is_archived": True,
          "is_general": False,
          "unlinked": 0,
          "name_normalized": "test-channel-2",
          "is_shared": False,
          "is_org_shared": False,
          "is_member": False,
          "is_private": False,
          "is_mpim": False,
          "members": [
            "U1TESTING",
            "U2TESTING"
          ],
          "topic": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "purpose": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "previous_names": [],
          "num_members": 2
        },
        {
          "id": "ID-CH-3",
          "name": "a-different-channel-1",
          "is_channel": True,
          "created": 1472598112,
          "creator": "U1TESTING",
          "is_archived": False,
          "is_general": False,
          "unlinked": 0,
          "name_normalized": "test-channel-1",
          "is_shared": False,
          "is_org_shared": False,
          "is_member": False,
          "is_private": False,
          "is_mpim": False,
          "members": [
            "U1TESTING",
            "U2TESTING",
            "U3TESTING",
          ],
          "topic": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "purpose": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "previous_names": [],
          "num_members": 3
        },
        {
          "id": "ID-CH-4",
          "name": "a-different-channel-2",
          "is_channel": True,
          "created": 1472598112,
          "creator": "U2TESTING",
          "is_archived": True,
          "is_general": False,
          "unlinked": 0,
          "name_normalized": "test-channel-2",
          "is_shared": False,
          "is_org_shared": False,
          "is_member": False,
          "is_private": False,
          "is_mpim": False,
          "members": [
            "U1TESTING",
            "U2TESTING"
          ],
          "topic": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "purpose": {
            "value": "",
            "creator": "",
            "last_set": 0
          },
          "previous_names": [],
          "num_members": 2
        },
    ]
}

NOT_ARCHIVED_CHANNEL_FIXTURES = {
    'ok': True,
    'channels': [
        CHANNELS_FIXTURE['channels'][0],
        CHANNELS_FIXTURE['channels'][2],
      ]
}


@pytest.fixture
def get_mocked_client():
    def wrapped(data_fixture):
        client = HighLevelSlackClient(TOKEN)
        client._client.api_call = MagicMock(
            return_value=data_fixture)
        return client

    return wrapped


@responses.activate
def test_list_channels_without_filters(get_mocked_client):
    mocked_client = get_mocked_client(CHANNELS_FIXTURE)
    channels = [c for c in mocked_client.channels()]

    mocked_client._client.api_call.assert_called_once_with('channels.list')

    assert len(channels) == 4

    c1, c2, c3, c4 = channels

    assert c1.name == 'test-channel-1'
    assert c1.id == 'ID-CH-1'

    assert c2.name == 'test-channel-2'
    assert c2.id == 'ID-CH-2'

    assert c3.name == 'a-different-channel-1'
    assert c3.id == 'ID-CH-3'

    assert c4.name == 'a-different-channel-2'
    assert c4.id == 'ID-CH-4'


@responses.activate
def test_list_channels_slack_api_parameters(get_mocked_client):
    """Parameter that are not filters should be forwarded to the Slack API.
    """
    mocked_client = get_mocked_client(CHANNELS_FIXTURE)
    channels = [c for c in mocked_client.channels(exclude_members=True)]

    mocked_client._client.api_call.assert_called_once_with(
        'channels.list', exclude_members=True)

    assert len(channels) == 4


@responses.activate
def test_list_channels_exclude_archived(get_mocked_client):
    mocked_client = get_mocked_client(NOT_ARCHIVED_CHANNEL_FIXTURES)
    channels = [c for c in mocked_client.channels(exclude_archived=True)]

    mocked_client._client.api_call.assert_called_once_with(
        'channels.list', exclude_archived=True)

    assert len(channels) == 2

    c1, c2 = channels

    assert c1.name == 'test-channel-1'
    assert c1.id == 'ID-CH-1'
    assert not c1.is_archived

    assert c2.name == 'a-different-channel-1'
    assert c2.id == 'ID-CH-3'
    assert not c2.is_archived


@responses.activate
def test_list_channels_only_archived(get_mocked_client):

    mocked_client = get_mocked_client(CHANNELS_FIXTURE)
    channels = [c for c in mocked_client.channels(only_archived=True)]

    mocked_client._client.api_call.assert_called_once_with('channels.list')

    assert len(channels) == 2

    c1, c2 = channels

    assert c1.name == 'test-channel-2'
    assert c1.id == 'ID-CH-2'

    assert c2.name == 'a-different-channel-2'
    assert c2.id == 'ID-CH-4'


@responses.activate
def test_list_channels_is_archived_is_false(get_mocked_client):
    mocked_client = get_mocked_client(CHANNELS_FIXTURE)
    channels = [c for c in mocked_client.channels(is_archived=False)]

    mocked_client._client.api_call.assert_called_once_with('channels.list')

    assert len(channels) == 2

    c1, c2 = channels

    assert c1.name == 'test-channel-1'
    assert c1.id == 'ID-CH-1'

    assert c2.name == 'a-different-channel-1'
    assert c2.id == 'ID-CH-3'


@responses.activate
def test_list_channels_is_archived_is_true(get_mocked_client):
    mocked_client = get_mocked_client(CHANNELS_FIXTURE)
    channels = [c for c in mocked_client.channels(is_archived=True)]

    mocked_client._client.api_call.assert_called_once_with('channels.list')

    assert len(channels) == 2

    c1, c2 = channels

    assert c1.name == 'test-channel-2'
    assert c1.id == 'ID-CH-2'

    assert c2.name == 'a-different-channel-2'
    assert c2.id == 'ID-CH-4'


@responses.activate
def test_list_channels_start_with(get_mocked_client):
    mocked_client = get_mocked_client(CHANNELS_FIXTURE)
    channels = [c for c in mocked_client.channels(starts_with='test-')]

    mocked_client._client.api_call.assert_called_once_with('channels.list')

    assert len(channels) == 2

    c1, c2 = channels

    assert c1.name == 'test-channel-1'
    assert c1.id == 'ID-CH-1'

    assert c2.name == 'test-channel-2'
    assert c2.id == 'ID-CH-2'


@responses.activate
def test_list_channels_start_with_and_is_archived(get_mocked_client):
    mocked_client = get_mocked_client(CHANNELS_FIXTURE)
    channels = [c for c in mocked_client.channels(
        starts_with='test-', is_archived=False)]

    mocked_client._client.api_call.assert_called_once_with('channels.list')

    assert len(channels) == 1

    c1 = channels[0]

    assert c1.name == 'test-channel-1'
    assert c1.id == 'ID-CH-1'
