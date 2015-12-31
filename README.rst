=======
Caravan
=======

**Light python framework for AWS SWF**

About this Project
==================

Caravan is being used at `Ludia <https://github.com/ludia>`_ for projects
like marketing campaign system and on-demand distributed processing
systems (thanks to hundreds of Lambda functions).

Feedbacks, ideas and contributions are highly welcomed. (Just open a
`Github issue <https://github.com/pior/caravan/issues>`_).

- `Code on Github <https://github.com/pior/caravan>`_
- `PyPi <https://pypi.python.org/pypi/caravan>`_
- `Tests <https://travis-ci.org/pior/caravan>`_ |travis| |coveralls|
- Doc: ``TODO``

.. |travis| image:: https://travis-ci.org/pior/caravan.svg?branch=master
    :target: https://travis-ci.org/pior/caravan

.. |coveralls| image:: https://coveralls.io/repos/pior/caravan/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/pior/caravan?branch=master

Focus of this project
=====================

Similar projects exists (like Simpleflow which seems mature).
Here is where Caravan differs from existing projects:

- Support of AWS Lambda tasks
- Boto3
- KISS
- Bring your own workflow framework (standard implementations as contribs)
- No coupling between Decider code and Activity code
- Paster compatible config file

Features
========

- Decider worker
- Activity task worker ``TODO``
- Commands to start/signal/terminate an arbitrary workflow execution
- Command to list open workflow execution
- Command to register a domain / list domains

Configuration
=============

Caravan uses Boto3 to connect to AWS. See
`Boto 3 configuration guide <http://boto3.readthedocs.org/en/latest/guide/configuration.html>`_
for the complete documentation.

.. warning::
    On AWS EC2, the metadata provider only provides the credentials, the
    must be provided by configuration.

Environment Variables
---------------------

``AWS_ACCESS_KEY_ID``
    The access key for your AWS account.

``AWS_SECRET_ACCESS_KEY``
    The secret key for your AWS account.

``AWS_DEFAULT_REGION``
    The default region to use, e.g. `us-east-1`.

``AWS_PROFILE``
    The default credential and configuration profile to use, if any.

Configuration Files
-------------------

The credentials file is located at ``~/.aws/credentials``::

    [default]
    # The access key for your AWS account
    aws_access_key_id=<YOUR ACCESS KEY ID>

    # The secret key for your AWS account
    aws_secret_access_key=<YOUR SECRET KEY>

The settings file is located at ``~/.aws/config``::

    [default]
    # The default region when making requests
    region=<REGION NAME>

It also supports profiles::

    [profile dev-profile]
    # The default region when using the dev-profile account
    region=<REGION NAME>

Demo
====

Setup a SWF domain to run this example::

    $ caravan-domain-register -n CaravanDemo --retention-days 1

Write a workflow type (see full demo_)

.. code:: python

    from caravan import Workflow


    class Demo(Workflow):

        """Noop workflow using the bare caravan API."""

        name = 'Demo'
        version = '0.1'
        default_execution_start_to_close_timeout = '600'
        default_task_start_to_close_timeout = '10'

        def run(self):
            self.task.print_events()
            self.task.add_decision('CompleteWorkflowExecution')

.. _demo: https://github.com/pior/caravan/blob/master/caravan/examples/demo.py

Run the decider with the Demo workflow::

    $ caravan-decider -d CaravanDemo -m caravan.examples.demo -t default --verbose

Start an execution of the Demo workflow::

    $ caravan-start -d CaravanDemo -n Demo -v 0.1 -i 1

    (The Demo workflow will wait for 5 minutes)

List the executions::

    $ caravan-list -d CaravanDemo
    $ caravan-list -d CaravanDemo --oldest 2015-01-01

Send a signal to an execution::

    $ caravan-signal -d CaravanDemo -i 1 -s PRINT --input 'Hello World!'
    $ caravan-signal -d CaravanDemo -i 1 -s PRINT --input 'Lorem ipsum'
    $ caravan-signal -d CaravanDemo -i 1 -s STOP

Terminate an execution::

    $ caravan-terminate -d CaravanDemo -i 1

Similar projects
================

Python:

- Simpleflow: https://github.com/botify-labs/simpleflow
- Flowy: https://github.com/severb/flowy
- Garcon: https://github.com/xethorn/garcon

Ruby:

- AWS Flow: https://github.com/aws/aws-flow-ruby

References
==========

- `AWS Developer Guide for SWF <http://docs.aws.amazon.com/amazonswf/latest/developerguide/>`_
- `AWS API reference for SWF <http://docs.aws.amazon.com/amazonswf/latest/apireference/>`_

Development
===========

Possibly use `virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_
to manage your virtualenvs.

    $ mkvirtualenv caravan

    or

    $ virtualenv caravan

Clone and install development dependencies::

    (caravan)$ git clone git@github.com:pior/caravan.git
    (caravan)$ cd caravan
    (caravan)$ pip install -e .[dev]

Run tests::

    (caravan)$ nosetests

Release
=======

The release process use zest.releaser::

    $ fullrelease

License
=======

MIT licensed. See the bundled
`LICENSE <https://github.com/pior/caravan/blob/master/LICENSE>`_
file for more details
