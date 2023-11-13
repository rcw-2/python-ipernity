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

The following snippet illustrates the authentication procedure for a
`Flask <https://flask.palletsprojects.com/>`_ app. The URL for
``callback`` must be given to Ipernity on creation of the API key.

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


Calling API methods
--------------------

There are two ways of calling Ipernity API methods:

#. The :meth:`~IpernityAPI.call` method.
#. The "method property" scheme.

The difference is best shown in an example:

.. code-block:: python

    # These two calls are equivalent
    user_info = iper.call('user.get', userid = 4711)
    user_info = iper.user.info(userid = 4711)

In both cases, the response (here: ``user_info``) is the complete parsed JSON
that the API call returns. See
`Ipernity API output formats <http://www.ipernity.com/help/api/output.formats.html>`_
for more information.


Iterating over search results
------------------------------

PyIpernity provides special methods to iterate smoothly over results that are
distributed as multiple "pages". These generators are:

:meth:`~ipernity.IpernityAPI.walk_albums`
    Iterates over a user's albums.

:meth:`~ipernity.IpernityAPI.walk_album_docs`
    Iterates over documents in an album.

:meth:`~ipernity.IpernityAPI.walk_doc_search`
    Iterates over the result of a document search.

:meth:`~ipernity.IpernityAPI.walk_docs`
    Iterates over a user's documents.

:meth:`~ipernity.IpernityAPI.walk_data`
    Generic method, called by the other ``walk_*`` methods.


