import sys
import argparse

import botocore.exceptions

from caravan.commands import get_swf_connection, is_response_success


def main():
    parser = argparse.ArgumentParser(description='Signal a workflow execution')
    parser.add_argument('-d', '--domain', required=True)
    parser.add_argument('-i', '--id', required=True)
    parser.add_argument('--run-id')
    parser.add_argument('-s', '--signal', required=True)
    parser.add_argument('--input', help='Raw input data for this signal')
    args = parser.parse_args()

    connection = get_swf_connection()

    callargs = {}
    if args.input:
        callargs['input'] = args.input
    if args.run_id:
        callargs['runId'] = args.run_id

    try:
        response = connection.signal_workflow_execution(
            domain=args.domain,
            workflowId=args.id,
            signalName=args.signal,
            **callargs
            )
    except botocore.exceptions.ClientError as err:
        sys.exit(err)
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        if is_response_success(response):
            print 'Signal successfully sent'
        else:
            print 'Response: %s' % response
