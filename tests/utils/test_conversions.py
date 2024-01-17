import unittest
import numpy as np

from rats.physics.constants import EQ_RADIUS_M
from rats.utils.conversions import freq_to_wvln, wvln_to_freq, db_to_decimal
from rats.utils.coordinates import lla_to_ecef, ecef_to_lla


class TestConversionMethods(unittest.TestCase):
    # Test frequency to wavelength (float)
    def test_freq_to_wvln(self):
        freq = 31.4  # [MHz]
        wvln = freq_to_wvln(freq)
        self.assertAlmostEqual(wvln, 9.54753051)

    # Test frequency to wavelength (array)
    def test_freq_to_wvln(self):
        freq = np.array([1.57, 31.4, 20.23])  # [MHz]
        wvln = freq_to_wvln(freq)
        corr = np.array([190.95061019, 9.54753051, 14.819202076])
        np.testing.assert_array_almost_equal(wvln, corr)

    # Test wavelength to frequency (float)
    def test_wvln_to_freq(self):
        wvln = 95.426903172  # [m]
        freq = wvln_to_freq(wvln)
        self.assertAlmostEqual(freq, 3.14159265)

    # Test wavelength to frequency (array)
    def test_wvln_to_freq(self):
        wvln = np.array([76.54, 87.65, 98.76])  # [m]
        freq = wvln_to_freq(wvln)
        corr = np.array([3.9168076561, 3.4203360867, 3.0355655934])
        np.testing.assert_array_almost_equal(freq, corr)

    # Test decibels to signal loss
    def test_db_to_decimal(self):
        db = -3.0  # [dB]
        dm = db_to_decimal(db)
        self.assertAlmostEqual(dm, -0.4988, places=3)


class TestConversionMethodsLLA(unittest.TestCase):
    """
    Expected values are taken from orekit results for the same conversion

    Reference code::

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                 Constants.WGS84_EARTH_FLATTENING,
                                 itrf)
        lat = np.deg2rad(33.0)
        lon = np.deg2rad(84.0)
        gp = GeodeticPoint(float(lat), float(lon), 6378137.0)
        coord = TopocentricFrame(earth, gp, "station")
        print(coord.getPVCoordinates(AbsoluteDate.J2000_EPOCH, itrf))
    """

    def test_lla_to_ecef_1d(self):
        lla = np.array([np.deg2rad(33), np.deg2rad(-84), EQ_RADIUS_M])
        arr = lla_to_ecef(lla)
        result = np.isclose(
            arr,
            np.array([1118834.0545646108, -1.0644994958923265e7, 6927741.022051536]),
        )
        assert result.all()

    def test_lla_to_ecef_2d(self):
        lla = np.array(
            [
                [np.deg2rad(33), np.deg2rad(-84), EQ_RADIUS_M],
                [np.deg2rad(33), np.deg2rad(84), EQ_RADIUS_M],
            ]
        )
        arr = lla_to_ecef(lla)
        result = np.isclose(
            arr,
            np.array(
                [
                    [1118834.0545646108, -1.0644994958923265e7, 6927741.022051536],
                    [1118834.0545646108, 1.0644994958923267e7, 6927741.022051543],
                ]
            ),
        )
        assert result.all()


class TestConversionMethodsECEF(unittest.TestCase):
    """
    Expected values are taken from orekit results for the same conversion

    Reference code::

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                 Constants.WGS84_EARTH_FLATTENING,
                                 itrf)
        lat = np.deg2rad(33.0)
        lon = np.deg2rad(84.0)
        gp = GeodeticPoint(float(lat), float(lon), 6378137.0)
        coord = TopocentricFrame(earth, gp, "station")
        print(coord.getPVCoordinates(AbsoluteDate.J2000_EPOCH, itrf))
    """

    def test_ecef_to_lla_1d(self):
        ecef = np.array([1118834.0545646108, -1.0644994958923265e7, 6927741.022051536])
        arr = ecef_to_lla(ecef, deg=True)
        result = np.isclose(
            arr.T,
            np.array([33, -84, EQ_RADIUS_M]),
        )
        assert result.all()

    def test_ecef_to_lla_2d(self):
        ecef = np.array(
            [
                [1118834.0545646108, -1.0644994958923265e7, 6927741.022051536],
                [1118834.0545646108, 1.0644994958923267e7, 6927741.022051543],
            ]
        )
        arr = ecef_to_lla(ecef)
        result = np.isclose(
            arr.T,
            np.array(
                [
                    [np.deg2rad(33), np.deg2rad(-84), EQ_RADIUS_M],
                    [np.deg2rad(33), np.deg2rad(84), EQ_RADIUS_M],
                ]
            ),
        )
        assert result.all()
