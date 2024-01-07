v0.3.0 (2024-01-07)
--------------------
*   Allow custom authentication handlers.
*   Interactive mode (``python -m ipernity``).
*   New attributes ``api_key`` and ``api_secret``.

v0.2.0 (2023-12-28)
--------------------
*   Exceptions for specific errors.
*   ``IpernityAPI.call()`` raises ``APIRequestError`` instead of ``HTTPError``
    if HTTP request fails.
*   Removed obsolete ``_replace_file`` method.

v0.1.5 (2023-12-09)
--------------------
*   New attribute ``permissions`` and method ``has_permissions``.

v0.1.4 (2023-11-25)
--------------------
*   Fixed ``walk_data`` for ``group.getList`` and empty results.

v0.1.3 (2023-11-13)
--------------------
*   Web authentication added.
*   ``user_info`` returns ``None`` when user data is not present
    and cannot be fetched.
*   Storing of token by ``AuthHandler.getToken`` is optional.

v0.1.2 (2023-11-11)
--------------------
*   First public release.
