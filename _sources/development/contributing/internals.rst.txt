Internals
=========

TADA's internals contain files necessary to establish the RF analysis library.


Repository layout
-----------------
The repository layout is standard for a service-driven plugin.

- ``README.md`` - Documentation for the TADA GitHub landing page.

- ``package.json`` - TADA package dependencies and changelog specification

- ``pyproject.toml`` - Project characterization / development data

- ``build/`` - Mac OS build files for TADA

- ``docs/`` - Sources for building documentation

- ``examples/`` - Sources to help demonstrate TADA's functionality

- ``src/`` - The source code for TADA

  - ``tada/`` - Where the TADA code is housed.

- ``tests/`` - Contains unit tests for each module

  - ``hw_tests/`` - Unit tests for hardware operation and connectivity (ex. RTL SDR dongles, etc.)
  
  - ``sw_tests/`` - Unit tests for software scripts (ex. analysis, data cleaning, etc.)

  - ``utils/`` - Unit tests for the utility codes (ex. conversions, etc.)