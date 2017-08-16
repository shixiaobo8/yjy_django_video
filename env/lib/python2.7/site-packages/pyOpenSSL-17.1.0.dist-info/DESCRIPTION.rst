========================================================
pyOpenSSL -- A Python wrapper around the OpenSSL library
========================================================

.. image:: https://readthedocs.org/projects/pyopenssl/badge/?version=stable
   :target: https://pyopenssl.readthedocs.io/
   :alt: Stable Docs

.. image:: https://travis-ci.org/pyca/pyopenssl.svg?branch=master
   :target: https://travis-ci.org/pyca/pyopenssl
   :alt: Build status

.. image:: https://codecov.io/github/pyca/pyopenssl/branch/master/graph/badge.svg
   :target: https://codecov.io/github/pyca/pyopenssl
   :alt: Test coverage


High-level wrapper around a subset of the OpenSSL library.  Includes

* ``SSL.Connection`` objects, wrapping the methods of Python's portable sockets
* Callbacks written in Python
* Extensive error-handling mechanism, mirroring OpenSSL's error codes

... and much more.

You can find more information in the documentation_.
Development takes place on GitHub_.


Discussion
==========

If you run into bugs, you can file them in our `issue tracker`_.

We maintain a cryptography-dev_ mailing list for both user and development discussions.

You can also join ``#cryptography-dev`` on Freenode to ask questions or get involved.


.. _documentation: https://pyopenssl.readthedocs.io/
.. _`issue tracker`: https://github.com/pyca/pyopenssl/issues
.. _cryptography-dev: https://mail.python.org/mailman/listinfo/cryptography-dev
.. _GitHub: https://github.com/pyca/pyopenssl


Release Information
===================

17.1.0 (2017-06-30)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Removed the deprecated ``OpenSSL.rand.egd()`` function.
  Applications should prefer ``os.urandom()`` for random number generation.
  `#630 <https://github.com/pyca/pyopenssl/pull/630>`_
- Removed the deprecated default ``digest`` argument to ``OpenSSL.crypto.CRL.export()``.
  Callers must now always pass an explicit ``digest``.
  `#652 <https://github.com/pyca/pyopenssl/pull/652>`_
- Fixed a bug with ``ASN1_TIME`` casting in ``X509.set_notBefore()``,
  ``X509.set_notAfter()``, ``Revoked.set_rev_date()``, ``Revoked.set_nextUpdate()``,
  and ``Revoked.set_lastUpdate()``. You must now pass times in the form
  ``YYYYMMDDhhmmssZ``. ``YYYYMMDDhhmmss+hhmm`` and ``YYYYMMDDhhmmss-hhmm``
  will no longer work. `#612 <https://github.com/pyca/pyopenssl/pull/612>`_


Deprecations:
^^^^^^^^^^^^^


- Deprecated the legacy "Type" aliases: ``ContextType``, ``ConnectionType``, ``PKeyType``, ``X509NameType``, ``X509ExtensionType``, ``X509ReqType``, ``X509Type``, ``X509StoreType``, ``CRLType``, ``PKCS7Type``, ``PKCS12Type``, ``NetscapeSPKIType``.
  The names without the "Type"-suffix should be used instead.


Changes:
^^^^^^^^

- Added ``OpenSSL.crypto.X509.from_cryptography()`` and ``OpenSSL.crypto.X509.to_cryptography()`` for converting X.509 certificate to and from pyca/cryptography objects.
  `#640 <https://github.com/pyca/pyopenssl/pull/640>`_
- Added ``OpenSSL.crypto.X509Req.from_cryptography()``, ``OpenSSL.crypto.X509Req.to_cryptography()``, ``OpenSSL.crypto.CRL.from_cryptography()``, and ``OpenSSL.crypto.CRL.to_cryptography()`` for converting X.509 CSRs and CRLs to and from pyca/cryptography objects.
  `#645 <https://github.com/pyca/pyopenssl/pull/645>`_
- Added ``OpenSSL.debug`` that allows to get an overview of used library versions (including linked OpenSSL) and other useful runtime information using ``python -m OpenSSL.debug``.
  `#620 <https://github.com/pyca/pyopenssl/pull/620>`_
- Added a fallback path to ``Context.set_default_verify_paths()`` to accommodate the upcoming release of ``cryptography`` ``manylinux1`` wheels.
  `#633 <https://github.com/pyca/pyopenssl/pull/633>`_

`Full changelog <https://pyopenssl.readthedocs.io/en/stable/changelog.html>`_.



