from caravan.commands.start import Command


def run_and_get_mock(mocker, args):
    orig_args = ['PROG', '-d', 'DOMAIN', '-n', 'NAME', '-v', 'VERSION',
                 '-i', 'ID']
    args = orig_args + args
    mocker.patch('sys.argv', args)

    run_swf = mocker.patch('caravan.commands.start.run_swf_command')
    run_swf.return_value = {'runId': 'RUNID'}

    Command.main()

    return run_swf


def test_minimal(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=[])

    run_swf.assert_called_once_with(
        'start_workflow_execution',
        domain='DOMAIN',
        workflowId='ID',
        workflowType={'name': 'NAME', 'version': 'VERSION'},
        input=None,
        taskList=None,
        tagList=None,
        executionStartToCloseTimeout=None,
        taskStartToCloseTimeout=None,
        childPolicy=None,
        lambdaRole=None,
        )

    out, _ = capsys.readouterr()
    assert 'Execution started.' in out
    assert 'RunId: RUNID' in out


def test_task_list(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['-t', 'TASKLISTNAME'])
    assert run_swf.call_args[1]['taskList'] == {'name': 'TASKLISTNAME'}


def test_tag_list_1(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--tag', 'TAG1'])
    assert run_swf.call_args[1]['tagList'] == ['TAG1']


def test_tag_list_2(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--tag', 'TAG1 TAG2'])
    assert run_swf.call_args[1]['tagList'] == ['TAG1', 'TAG2']


def test_input(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--input', 'INPUT'])
    assert run_swf.call_args[1]['input'] == 'INPUT'


def test_execution_timeout(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--execution-timeout', '60'])
    assert run_swf.call_args[1]['executionStartToCloseTimeout'] == '60'


def test_task_timeout(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--task-timeout', '60'])
    assert run_swf.call_args[1]['taskStartToCloseTimeout'] == '60'


def test_child_policy(mocker, capsys):
    test_policy = Command.CHILD_POLICIES[0]
    run_swf = run_and_get_mock(mocker, args=['--child-policy', test_policy])
    assert run_swf.call_args[1]['childPolicy'] == test_policy


def test_lambda_role(mocker, capsys):
    run_swf = run_and_get_mock(mocker, args=['--lambda-role', 'ROLE'])
    assert run_swf.call_args[1]['lambdaRole'] == 'ROLE'
