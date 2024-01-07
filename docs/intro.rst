Introduction
==============

This library is a simple wrapper around the
`Ipernity API <http://www.ipernity.com/help/api/about.html>`_.
It was inspired by Wayne's
`Ipernity API <https://github.com/oneyoung/python-ipernity-api>`_ and
Sybren A. Stüvel's `Flickr API <https://stuvel.eu/software/flickrapi/>`_.


Installation
-------------

Via Pip:

.. code-block:: shell-session

    $ pip install PyIpernity

The source is available at `Github <https://github.com/rcw-2/python-ipernity>`_.


Limits
-------

* OAuth is not supported.
* The only supported data format is JSON (which is parsed into Python objects).
* PyIpernity has no object-oriented representation of Ipernity objects like
  documents, albums etc.
* Management of credentials (login and tokens) is mostly left to the user.


