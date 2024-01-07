Usage
==============


Authentication and Authorization
----------------------------------

So far, only desktop and web authentication are supported.


Desktop Authentication
~~~~~~~~~~~~~~~~~~~~~~~~

To get an access token, do something like this:

.. code-block:: python

    from ipernity import IpernityAPI

    iper = IpernityAPI(my_key, my_secret)
    frob = iper.auth.getFrob()['auth']['frob']
    url = iper.auth.auth_url({'doc': 'write'}, frob)

    print('Starting web browser for authorization...')
    webbrowser.open_new(url)
    input('Press <Enter> after authorizing access in browser... ')

    # Get access token and store it in API object
    iper.auth.getToken(frob)
    print('Token retrieved, you can close the browser now.')

Once the access token is generated, it can be passed to `IpernityAPI`'s
constructor to create a pre-authorized object:

.. code-block:: python

    from ipernity import IpernityAPI
    iper = IpernityAPI(my_key, my_secret, my_token)

.. seealso::
    * `Ipernity Documentation <http://www.ipernity.com/help/api/auth.soft.html>`_


Web Authentication (Flask)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following snippet illustrates the authentication procedure using an example
`Flask <https://flask.palletsprojects.com/>`_ application. For a description
of the process, see the
`Ipernity Documentation <http://www.ipernity.com/help/api/auth.web.html>`.
The URL for ``callback`` must be given to Ipernity on creation of the
API key.

.. code-block:: python

    from flask import Flask, redirect, session
    from ipernity import IpernityAPI

    app = Flask()

    # Application should redirect here when authorization is required
    @app.route('/login')
    def login():
        iper = IpernityAPI(my_key, my_secret, auth='web')
        return redirect(iper.auth.auth_url({'doc': 'write'}))
    
    # Ipernity will redirect here on successful authorization
    @app.route('/callback')
    def callback():
        frob = request.params['frob']
        iper = IpernityAPI(my_key, my_secret, auth='web')
        token = iper.auth.getToken(frob)['auth']
        session['token'] = token

.. seealso::
    * `Ipernity Documentation <http://www.ipernity.com/help/api/auth.web.html>`_


.. _calling-api-methods:

Calling API methods
--------------------

There are two ways of calling Ipernity API methods:

#. The :meth:`~ipernity.api.IpernityAPI.call` method.
#. The "method property" scheme.

The difference is best shown in an example:

.. code-block:: python

    ip = IpernityAPI(key, secret)

    # These two calls are equivalent
    user_info = ip.call('user.get', userid = 4711)
    user_info = ip.user.get(userid = 4711)

.. note::
    *   All parameters should be passed as keyword arguments.
    *   The response (here: ``user_info``) is the complete parsed JSON that the
        API call returns. See
        `Ipernity API output formats <http://www.ipernity.com/help/api/output.formats.html>`_
        for more information.
    *   The ``api_key`` parameter is specified in the constructor of
        :class:`IpernityAPI` and should not be specified in API calls.
    *   Requests are automatically signed by PyIpernity.


Iterating over search results
------------------------------

PyIpernity provides special methods to iterate smoothly over results that are
distributed as multiple "pages". These generators are:

:meth:`~ipernity.api.IpernityAPI.walk_albums`
    Iterates over a user's albums.

:meth:`~ipernity.api.IpernityAPI.walk_album_docs`
    Iterates over documents in an album.

:meth:`~ipernity.api.IpernityAPI.walk_doc_search`
    Iterates over the result of a document search.

:meth:`~ipernity.api.IpernityAPI.walk_docs`
    Iterates over a user's documents.

:meth:`~ipernity.api.IpernityAPI.walk_data`
    Generic method, called by the other ``walk_*`` methods.


Interactive mode
-----------------

.. versionadded:: 0.3.0

PyIpernity provides an interactive mode for testing. To get information about
the command line options, type

.. code-block:: shell-session

    $ python -m ipernity -h

at the shell prompt. If application key and secret are specified in environment
variables or a configuration file, you can just start interactive mode with

.. code-block:: shell-session

    $ python -m ipernity


Specifying key, secret and token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are three ways to specify the authentication information
(in order of precedence):

#. Command line arguments:
    
    .. code-block:: shell-session
        
        $ python -m ipernity -k <api-key> -s <api-secret> -t <api-token>

#. Configuration file (default :file:`$HOME/.ipernity.ini`):
    
    .. code-block:: ini

        [ipernity]
        api key = <api-key>
        api secret = <api-secret>
        api token = <api-token>

#. Environment variables:
    
    .. code-block:: shell-session

        IPERNITY_API_KEY=<api-key>
        IPERNITY_API_SECRET=<api-secret>
        IPERNITY_API_TOKEN=<api-token>

Specifying the token is optional. Some API methods can be called without a
token, and you can get a token with the ``login`` command.

