Internals
=========

TADA's internals contain files necessary to establish the RF analysis library.


Repository layout
-----------------
The repository layout is standard for a service-driven plugin.

- ``README.md`` - Documentation for the TADA GitHub landing page.

- ``package.json``

- ``pyproject.toml`` - Project characterization / development data

- ``build/`` - Mac OS build files for TADA

- ``docs/`` - Sources for building documentation

- ``examples/`` - Sources to help demonstrate TADA's functionality

- ``src/`` - The source code for TADA

  - ``tada/`` - Where the TADA code is housed.

  - ``rats.egg-info``

- ``tests/`` - Contains unit tests for each module

  - ``analysis/`` - Unit tests for the Analysis scripts (ex. line of sight, etc.)

  - ``utils/`` - Unit tests for the utility codes (ex. conversions, etc.)