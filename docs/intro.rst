Introduction
==============

This library is a simple wrapper around
`Ipernity's API <http://www.ipernity.com/help/api/about.html>`_.
It was inspired by Wayne's
`Ipernity API <https://github.com/oneyoung/python-ipernity-api>`_ and
Sybren A. Stüvel's `Flickr API <https://stuvel.eu/software/flickrapi/>`_.


Installation
-------------

The source is available at `Github <https://github.com/rcw-2/python-ipernity>`_.


Limits
-------

* Authorization is limited to desktop authenticaton.
* The only supported data format is JSON (which is parsed into Python objects).
* PyIpernity has no object-oriented representation of Ipernity object like
  documents, albums etc.
* Management of credentials (tokens) is left to the user.

