# ============================= Physical Constants =============================

#  WGS-84 equatorial radius of Earth, [m]
"""
Constant definitions

.. data:: EQ_RADIUS_M

    WGS-84 equatorial radius of the Earth [m]

.. data:: EARTH_FLATTENING

    WGS-84 Earth inverse flattening

.. data:: POLAR_RADIUS_M

    WGS-84 polar radius of the Earth [m]
    
.. data:: EARTH_ECCEN

    Prime eccentricity of the Earth (squared)
    
.. data:: PRIME_ECCEN

    Second ellipsoidal eccentricity of the Earth (squared)
    
.. data:: SPEED_OF_LIGHT

    Speed of light in a vacuum [m/s]
    
.. data:: E_SQUARED

    E^2 value of the Earth's oblong spheroid
"""
EQ_RADIUS_M = 6378137.0

# WGS-84 Earth inverse flattening
EARTH_FLATTENING = 1.0 / 298.257223563

# WGS-84 polar radius of earth [m] (6356752.314)
POLAR_RADIUS_M = EQ_RADIUS_M - EARTH_FLATTENING * EQ_RADIUS_M

# Prime eccentricity of earth, squared
EARTH_ECCEN = 0.00669438

# Second ellipsoisal eccentricity of earth, squared
PRIME_ECCEN = 0.00673950

# Speed of light [m/s]
SPEED_OF_LIGHT = 299792458

# E-squared value of the Earth's oblong spheroid
E_SQUARED = 6.69437999014e-3
