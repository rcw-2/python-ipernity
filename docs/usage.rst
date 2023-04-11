Usage
==============


Authentication and Authorization
----------------------------------

So far, only desktop authentication is supported. To get an access
token, do something like this:

.. code-block:: python

    from ipernity import IpernityAPI

    iper = IpernityAPI(my_key, my_secret)
    frob = iper.auth.getFrob()['auth']['frob']

    print('Starting web browser for authorization...')
    webbrowser.open_new(url)
    input('Press <Enter> after authorizing access in browser... ')

    # Store token in API object
    iper.auth.getToken(frob)
    print('Token retrieved, you can close the browser now.')

Once the access token is generated, it can be passed to `IpernityAPI`'s
constructor to create a pre-authorized object:

.. code-block:: python

    from ipernity import IpernityAPI

    iper = IpernityAPI(my_key, my_secret, my_token)


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



