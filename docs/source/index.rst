.. RATS documentation master file, created by
   sphinx-quickstart on Mon Nov  6 15:19:08 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the RATS documentation!
==================================

**RATS** (Radiation And Trajectory Simulator) is a Python library aimed at
creating a digital twin of the RF (radio frequency) environment of space-, air-,
land-, and sea-based assets. Based on a simple and intuitive API, RATS enables
high-fidelity signal loss predictions between two or more antennas.

.. warning::

   This project is under active development


Installation
------------
.. note::

   If running on a Mac, first ensure you have developer tools installed by running
   ``xcode-select --install``

RATS is available on JFrog for Slingshot usage in the ``slingshotaerospace.jfrog.io/artifactory/api/pypi/science-pypi/simple``
repository.  See `here <https://slingshotaero.atlassian.net/wiki/spaces/IT/pages/1866924079/JFrog+programmatic+access>`_
for information on how to obtain credentials.  Once you have credentials, simply
update your `pip configuration <https://pip.pypa.io/en/stable/topics/configuration/>`_ to include
the science repository as an ``extra-index-url``.

Once you've configured JFrog, you must first pre-install setuptools, wheel, and numpy to ensure the
RATS dependencies build properly. Then simply install RATS like any other package.

.. code::

   python -m pip install --upgrade pip setuptools wheel numpy
   python -m pip install rats



.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Development

   development/contributing/workflow
   development/contributing/internals
   development/changelog


.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: API Reference

   modules/analysis
   modules/cad
   modules/data
   modules/physics
   modules/simulation
   modules/utils




Indices and tables
==================

* :ref:`genindex`
* :ref:`search`