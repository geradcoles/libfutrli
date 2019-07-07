libfutrli
=========

A Python 3 library and cli-tool for interacting with with Futrli web suite
for business forecasting and reporting.

The impetus for this library was to add support for automating the uploading of
non-financial data to an organization in Futrli. As far as is known by the
author, Futrli does not have an official public-facing API, so this code uses
the framework provided by the interactive Futrli website to authenticate
and upload data.

Financial Data Upload Example
-----------------------------

First, we need to get a ``FutrliClient``::

    import libfutrli
    client = libfutrli.FutrliClient(
        email='some-email@nowhere.com', password='some-password')

If you don't want to supply credentials directly in code, you can use the
configuration system:

    configuration = get_configuration()
    client = libfutrli.FutrliClient(**configuration)

Then, we need to manually authenticate the client::

    client.authenticate()

Now before we can upload financial data, we need to identify our organization
ID, which can be obtained with the ``get_org_list()`` method, as follows::

    for org in client.get_org_list():
        print("{}: {}".format(org['id'], org['name']))

This approach dumps a list of organization IDs and the user-facing name,
so you can find your organization ID pretty quickly. In most cases, you can
probably shortcut to directly retrieving the ``id`` field from the first
organization returned. Alternatively, see the cli-interface method below.

Finally let's upload the CSV file to Futrli. Assuming we have a file called
'sample_data.csv' in the local directory::

    client.upload_financial_data('sample_data.csv', 'ORG_ID')

Command-Line Interface (CLI)
----------------------------

The command-line interface is probably most useful for scripted uploads and
ad-hoc workflows. Here's an example of uploading non-financial data::

    futrli nfd upload ./data/operating_hours.csv

Note that no email, password or organization ID are
provided to the command above. That's because they may optionally be placed in
a JSON configuration file at ``~/.futrli``. All of these configuration items
may optionally be provided to the command, itself (a different configuration
file path can be specified with the ``--config`` switch).

Before you can run any non-financial data uploads, you need to get your
organisation id (UK spelling), which can be done as follows:

    futrli org list

See ``futrli --help`` for a detailed list of options.