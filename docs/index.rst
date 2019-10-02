twtxt-registry-client
=====================

:ref:`genindex` - :ref:`modindex` - :ref:`search`

.. image:: https://img.shields.io/pypi/v/twtxt-registry-client.svg
   :target: https://pypi.org/project/twtxt-registry-client

.. image:: https://img.shields.io/pypi/l/twtxt-registry-client.svg
   :target: https://pypi.org/project/twtxt-registry-client

.. image:: https://img.shields.io/pypi/format/twtxt-registry-client.svg
   :target: https://pypi.org/project/twtxt-registry-client

.. image:: https://img.shields.io/pypi/pyversions/twtxt-registry-client.svg
   :target: https://pypi.org/project/twtxt-registry-client

.. image:: https://img.shields.io/pypi/status/twtxt-registry-client.svg
   :target: https://pypi.org/project/twtxt-registry-client

.. image:: https://gitlab.com/Lucidiot/twtxt-registry-client/badges/master/pipeline.svg
   :target: https://gitlab.com/Lucidiot/twtxt-registry-client/pipelines

.. image:: https://requires.io/github/Lucidiot/twtxt-registry-client/requirements.svg?branch=master
   :target: https://requires.io/github/Lucidiot/twtxt-registry-client/requirements/?branch=master

.. image:: https://img.shields.io/github/last-commit/Lucidiot/twtxt-registry-client.svg
   :target: https://gitlab.com/Lucidiot/twtxt-registry-client/commits

.. image:: https://img.shields.io/badge/badge%20count-9-brightgreen.svg
   :target: https://gitlab.com/Lucidiot/twtxt-registry-client

A Python CLI for the twtxt `registry API`_.

Installation
------------

This package has a very standard Python setup::

   pip install twtxt_registry_client

That's it, nothing more.

Usage
-----

Base arguments
^^^^^^^^^^^^^^

.. code::

   $ twtxt-registry
     [--version]
     [--help]
     [-k|-insecure]
     [-f [raw|json|pretty]]
     REGISTRY_URL
     COMMAND
     [subcommand args]

``--version``
   Output the CLI's version number and exit.
``--help``
   Output the main help text and exit.
``-k`` / ``--insecure``
   Disable SSL certificate checks; first added for the `twtxt demo registry`_
   as it is appears to be unmaintained and has an expired certificate.
``-f`` / ``--format`` with one of ``raw``, ``json`` or ``pretty``
   Use a specific :class:`Formatter <twtxt_registry_client.output.Formatter>`
   class to output the HTTP responses.
``REGISTRY_URL``
   Base URL to a twtxt registry's API.

   .. note::

      The recommended base path for registry APIs is at ``http://host/api``,
      but the `registry API`_ specification does not enforce it. Therefore,
      on most registries, you will need to append ``/api`` to the hostname.

``COMMAND [subcommand args]``
   A client subcommand; see the subcommand-specific sections below.

Registration
^^^^^^^^^^^^

.. code::

   $ twtxt-registry
     [...base arguments...]
     register
     [--help]
     [-n|--nickname [NICK]]
     [-u|--url [URL]]

``--help``
   Output the subcommand help text and exit.
``-n [NICK]`` / ``--nickname [NICK]``
   Set a custom nickname. If omitted, the CLI will try to read it from the
   ``twtxt`` client's standard configuration; this may not work with other
   twtxt implementations.
``-u [URL]`` / ``--url [URL]``
   Set a custom public URL. If omitted, the CLI will try to read it from the
   ``twtxt`` client's standard configuration; this may not work with other
   twtxt implementations.

This subcommand outputs the HTTP response directly, see
:meth:`Formatter.format_response()
<twtxt_registry_client.output.Formatter.format_response>`.

List users
^^^^^^^^^^

.. code::

   $ twtxt-registry
     [...base arguments...]
     users
     [--help]
     [-q|--query [TEXT]]

``--help``
   Output the subcommand help text and exit.
``-q [TEXT]`` / ``--query [TEXT]``
   Optionally filter users by a query.

This subcommand outputs the users list, see :meth:`Formatter.format_users()
<twtxt_registry_client.output.Formatter.format_users>`.
If the registry returns an HTTP 4xx or 5xx error code, the response is printed
directly. See :meth:`Formatter.format_response()
<twtxt_registry_client.output.Formatter.format_response>`.

List tweets
^^^^^^^^^^^

.. code::

   $ twtxt-registry
     [...base arguments...]
     tweets
     [--help]
     [-q|--query [TEXT]]

``--help``
   Output the subcommand help text and exit.
``-q [TEXT]`` / ``--query [TEXT]``
   Optionally filter tweets by a query.

This subcommand outputs the tweets list, see :meth:`Formatter.format_tweets()
<twtxt_registry_client.output.Formatter.format_tweets>`.
If the registry returns an HTTP 4xx or 5xx error code, the response is printed
directly. See :meth:`Formatter.format_response()
<twtxt_registry_client.output.Formatter.format_response>`.

List tweets by mention
^^^^^^^^^^^^^^^^^^^^^^

.. code::

   $ twtxt-registry
     [...base arguments...]
     mentions
     [--help]
     [NAME_OR_URL]

``--help``
   Output the subcommand help text and exit.
``NAME_OR_URL``
   Name or URL of a user to list mentions to.

   If a name is specified, the CLI will try to deduce its URL from the
   ``twtxt`` client's configuration. If nothing is specified, the CLI will
   use the configured public URL to default to the local user.
   This may not work on other twtxt implementations.

This subcommand outputs the tweets list, see :meth:`Formatter.format_tweets()
<twtxt_registry_client.output.Formatter.format_tweets>`.
If the registry returns an HTTP 4xx or 5xx error code, the response is printed
directly. See :meth:`Formatter.format_response()
<twtxt_registry_client.output.Formatter.format_response>`.

List tweets by tag
^^^^^^^^^^^^^^^^^^

.. code::

   $ twtxt-registry
     [...base arguments...]
     tag
     [--help]
     NAME

``--help``
   Output the subcommand help text and exit.
``NAME``
   Tag to list tweets for.

This subcommand outputs the tweets list, see :meth:`Formatter.format_tweets()
<twtxt_registry_client.output.Formatter.format_tweets>`.
If the registry returns an HTTP 4xx or 5xx error code, the response is printed
directly. See :meth:`Formatter.format_response()
<twtxt_registry_client.output.Formatter.format_response>`.

Learn more
----------

.. toctree::
   client
   output
   contributing

.. _registry API: https://twtxt.readthedocs.io/en/stable/user/registry.html
.. _twtxt demo registry: https://registry.twtxt.org
