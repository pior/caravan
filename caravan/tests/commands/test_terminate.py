from caravan.commands.terminate import Command


def run_and_get_mock(mocker, args):
    orig_args = ['PROG', '-d', 'DOMAIN', '-i', 'ID']
    args = orig_args + args
    mocker.patch('sys.argv', args)

    run_swf = mocker.patch('caravan.commands.terminate.run_swf_command')

    Command.main()

    return run_swf


def test_minimal(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=[])

    run_swf.assert_called_once_with(
        'terminate_workflow_execution',
        domain='DOMAIN',
        workflowId='ID',
        runId=None,
        reason=None,
        details=None,
        childPolicy=None,
        )

    out, _ = capsys.readouterr()
    assert 'Execution terminated.' in out


def test_runid(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--run-id', 'RUNID'])
    assert run_swf.call_args[1]['runId'] == 'RUNID'


def test_reason(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--reason', 'REASON'])
    assert run_swf.call_args[1]['reason'] == 'REASON'


def test_details(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--details', 'DETAILS'])
    assert run_swf.call_args[1]['details'] == 'DETAILS'


def test_child_policy(mocker, capsys):
    test_policy = Command.CHILD_POLICIES[0]
    run_swf = run_and_get_mock(mocker, args=['--child-policy', test_policy])
    assert run_swf.call_args[1]['childPolicy'] == test_policy
