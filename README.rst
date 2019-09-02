twtxt-registry-client
=====================

A simple API client for servers implementing `twtxt`_'s `registry`_ API.

.. _twtxt: https://github.com/buckket/twtxt
.. _registry: https://twtxt.readthedocs.io/en/stable/user/registry.html

To-do
-----

* Error handling
* Read user info from twtxt's config to set defaults on user registration
* Read user info from twtxt following list to guess the URL in mentions :
  ``twtxt-registry registry.twtxt.org mentions johndoe``
* Command-line help
* Sphinx documentation
  * Doc8 linting
  * GitLab Pages
* Enhanced outputs and porcelain mode, just like with `twtxt`_
* Verbose output and logging
