py-futrli
=========

A library for interacting with with Futrli web suite for business forecasting and reporting.

The impetus for this library was to add support for automating the uploading of
non-financial data to an organization in Futrli. As far as is known by the author, Futrli
does not have an official public-facing API, so this code uses the same framework used
by the interactive Futrli website to authenticate and upload data.

Financial Data Upload Example
-----------------------------

First, we need to get a ``FutrliClient``::

    import futrli
    client = futrli.FutrliClient(
        email='some-email@nowhere.com', password='some-password')

Then, we need to manually authenticate the client::

    client.authenticate()

Now before we can upload financial data, we need to identify our organization
ID, which can be obtained with the ``get_org_list()`` method, as follows::

    for org in client.get_org_list():
        print("{}: {}".format(org['id'], org['name']))

This approach dumps a list of organization IDs and the user-facing name,
so you can find your organization ID pretty quickly. In most cases, you can
probably shortcut to directly retrieving the ``id`` field from the first
organization returned.

Finally let's upload the CSV file to Futrli. Assuming we have a file called
'sample_data.csv' in the local directory::

    client.upload_financial_data('sample_data.csv', 'ORG_ID')

