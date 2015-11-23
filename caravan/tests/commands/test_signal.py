from caravan.commands.signal import Command


def test_minimal(mocker, capsys):
    run_swf = mocker.patch('caravan.commands.signal.run_swf_command')
    mocker.patch('sys.argv', ['PROG', '-d', 'DOMAIN', '-i', 'ID', '-s', 'SIG'])

    Command.main()

    out, _ = capsys.readouterr()
    assert 'Signal sent.' in out

    run_swf.assert_called_once_with(
        'signal_workflow_execution',
        domain='DOMAIN',
        input=None,
        runId=None,
        signalName='SIG',
        workflowId='ID',
        )
