=======
Caravan
=======

**Light python framework for AWS SWF**

Project
=======

- `Code on Github <https://github.com/pior/caravan>`_
- `PyPi <https://pypi.python.org/pypi/caravan>`_
- Doc: ``TODO``
- Tests: ``TODO``

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
- Activity task worker
- Commands to start/signal an arbitrary workflow execution
- Command to list workflow execution
- Command to register a domain

Usage
=====

Setup a SWF for the example::

    $ caravan-domain-register -n CaravanExample --retention-days 1

List execution for last 24h::

    $ caravan-list -d CaravanExample

List execution for year 2015::



Timer example
-------------
    $ caravan-list -d CaravanExample --oldest 2015-01-01

Run the decider::

    $ caravan-decider -d CaravanExample -m caravan.examples.timer.workflow -t default

Start an execution::

    $ caravan-start -d CaravanExample -n TimerExample -v 0.1 -i 1


Similar projects
================

Python:

- Simpleflow: https://github.com/botify-labs/simpleflow
- Flowy: https://github.com/severb/flowy
- Garcon: https://github.com/xethorn/garcon

Ruby:

- AWS Flow: https://github.com/aws/aws-flow-ruby

Development
===========

Clone and install development dependencies::

    $ git clone git@github.com:pior/caravan.git
    $ cd caravan
    $ pip install -e .[dev]

Run tests:

``TODO``

License
=======

MIT licensed. See the bundled
`LICENSE <https://github.com/pior/caravan/blob/master/LICENSE>`_
file for more details
