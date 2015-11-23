import datetime

from freezegun import freeze_time

from caravan.commands.list import Command


def run_and_get_mock(mocker, args):
    orig_args = ['PROG', '-d', 'DOMAIN']
    args = orig_args + args
    mocker.patch('sys.argv', args)

    run_swf = mocker.patch('caravan.commands.list.run_swf_command')
    run_swf.return_value = {'executionInfos': []}

    with freeze_time("2000-01-10"):
        Command.main()

    return run_swf


def test_minimal(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=[])

    start_time_filter = {
        'oldestDate': datetime.datetime(2000, 1, 9),
        'latestDate': datetime.datetime(2000, 1, 10),
        }

    run_swf.assert_called_once_with(
        'list_open_workflow_executions',
        domain='DOMAIN',
        startTimeFilter=start_time_filter,
        typeFilter=None,
        tagFilter=None,
        executionFilter=None,
        )

    out, _ = capsys.readouterr()
    assert 'No results.' in out


def test_type_filter(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['-n', 'NAME', '-v', 'VERSION'])
    expected = {'name': 'NAME', 'version': 'VERSION'}
    assert run_swf.call_args[1]['typeFilter'] == expected


def test_tag_filter(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--tag', 'TAG'])
    expected = {'tag': 'TAG'}
    assert run_swf.call_args[1]['tagFilter'] == expected


def test_id_filter(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--id', 'ID'])
    expected = {'workflowId': 'ID'}
    assert run_swf.call_args[1]['executionFilter'] == expected


# TODO: test formatter
