from __future__ import annotations

import abc
import inspect
import uuid
from enum import Enum
from PyNEC import *
from typing import Optional, List, ClassVar

import numpy as np
from pydantic import BaseModel, Field, ConfigDict

from rats import Simulated
from rats.data import PolymorphicBaseModel
from rats.utils.conversions import freq_to_wvln


class AntennaGeometry(str, Enum):
    """This class represents an arbitrary antenna geometry.
    :param str: A string specifying the geometry of the antenna. Current options
    include dipole ("DIPOLE"), Yagi-Uda ("YAGI_UDA"), and turnstile ("TURNSTILE")
    geometries.

    :type data: string
    """

    DIPOLE = "DIPOLE"
    YAGI_UDA = "YAGI_UDA"
    TURNSTILE = "TURNSTILE"


class AntennaAction(str, Enum):
    """
    This class represents an arbitrary antenna geometry.
    :param str: A string specifying the geometry of the antenna. Current options
    include dipole ("DIPOLE"), Yagi-Uda ("YAGI_UDA"), and turnstile ("TURNSTILE")
    geometries.

    :type data: string
    """

    TRANSMIT = "TRANSMIT"
    RECEIVE = "RECEIVE"


class Antenna(PolymorphicBaseModel, Simulated, abc.ABC, polymorphic=True):
    """This class represents a fully defined RATS antenna object. The object is
    characterized by a `name` field describing the antenna, a `geometry` field
    defining the geometry of the antenna (`AntennaGeometry`), and a `frequency`
    field defining the operation frequency of the antenna.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = Field(
        str(uuid.uuid4()),
        description="A descriptive name for the antenna",
        alias="name",
    )
    frequency: float = Field(
        400.0,
        description="The operation frequency of the antenna [MHz]",
        alias="frequency",
    )
    type: ClassVar[str]
    relative_location: np.ndarray = Field(
        np.array([0.0, 0.0, 0.0]),
        description="3D vector with coordinates of the antenna relative to the asset body. Defaults to the origin.",
    )
    actions: List[AntennaAction] = Field(
        [AntennaAction.RECEIVE],
        description="List of available capabilities for this antenna",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._wvl = freq_to_wvln(self.frequency)
        self._context = nec_context()
        self._geo = self._context.get_geometry()
        self._initialize()
        self._context.geometry_complete(0)
        # Define antenna gain
        self.define_gain()
        # Define antenna excitation
        self.define_excitation()
        # Define source frequencies
        self.define_frequency(first_val=self.frequency)
        # Radiation pattern parameters
        self.define_radiation()
        self._radiation_pattern = self._context.get_radiation_pattern(0)

    @property
    @abc.abstractmethod
    def source_index(self) -> int:
        pass

    @property
    def gain_db(self):
        return self._radiation_pattern.get_gain()

    @property
    def gain_pw(self):
        return 10.0 ** (self.gain_db / 10.0)

    @property
    def thetas(self):
        return np.deg2rad(self._radiation_pattern.get_theta_angles())

    @property
    def phis(self):
        return np.deg2rad(self._radiation_pattern.get_phi_angles())

    @property
    @abc.abstractmethod
    def diameter(self):
        pass

    def create_wire(
        self,
        *,
        tag_id: int = 0,
        segments: int = 5,
        wire_start: np.ndarray,
        wire_end: np.ndarray,
        radius: float = 0.001,
        rdel: float = 1.0,
        rrad: float = 1.0,
    ):
        """
        Generates a string of segments to represent a straight wire. Units are in m.

        Args:
            tag_id: Tag identification number assigned to all segments
            segments: Number of segments defining wire
            wire_start (np.ndarray): x,y,z coordinates of wire start position [m]
            wire_end (np.ndarray): x,y,z coordinates of wire end position [m]
            radius: Wire radius (`0` if tapered); `GC` card defines taper.
            rdel: Current segment length : previous segment length ratio
            rrad: Adjacent segment radii ratio

        Returns:
            object: <PyNEC geometry object>

        NOTES:
        * The tag number is for later use when a segment must be identified, such as
        when connecting a voltage source or lumped load to the segment. Any number
        except zero can be used as a tag. When identifying a segment by its tag, the
        tag number and the number of the segment in the set of segments having that
        tag are given. Thus, the tag of a segment does not need to be unique. If no
        need is anticipated to refer back to any segments on a wire by tag, the tag
        field may be left blank. This results in a tag of zero which cannot be
        referenced as a valid tag.

        - If two wires are electrically connected at their ends, the identical
        coordinates should be used for the connected ends to ensure that the wires
        are treated as connected for current interpolation. If wires intersect away
        from their ends, the point of intersection must occur at segment ends within
        each wire for interpolation to occur. Generally, wires should intersect only
        at their ends unless the location of segment ends is accurately known.

        * The only significance of differentiating end one from end two of a wire is
        that the positive reference direction for current will be in the direction
        from end one to end two on each segment making up the wire.

        - As a rule of thumb, segment lengths should be less than 0.1 wavelength at
        the desired frequency. Somewhat longer segments may be used on long wires
        with no abrupt changes, while shorter segments, 0.05 wavelength or less, may
        be required in modeling critical regions of an antenna.

        * If input is in units other than meters, then the units must be scaled to
        meters through the use of a Scale Structure Dimensions (GS) card.
        """
        coords = np.concatenate((wire_start, wire_end), axis=None)
        return (self._geo.wire(tag_id, segments, *coords, radius, rdel, rrad),)
        # self._geo.wire(1, 36, 0, 0, 0, -0.042, 0.008, 0.017, 0.001, 1.0, 1.0)

    def create_arc(
        self,
        tag_id: int = 0,
        segments: int = 36,
        rada: float = 0.5,
        ang1: float = 0.0,
        ang2: float = 180.0,
        radius: float = 0.001,
    ):
        """
        Generates a string of segments to represent a straight wire. Units are in m,
        and angles (`ang1`,`ang2`) are measured from the X-axis to the left-hand
        direction about the Y-axis in degrees.

        Args:
            tag_id: Tag identification number assigned to all segments
            segments: Number of segments definint wire
            rada: Arc radius [m]; center is the origin; see notes.
            ang1: Angle of the 1st end of the arc
            ang2: Angle of the 2nd end of the arc
            radius: Wire radius

        Returns:
            object: <PyNEC geometry object>

        NOTES:
            * The segments generated by GA form a section of polygons inscribed within
            the arc
            * If an arc in a different position or orientation is desired, the segements
            may be moved within a GM card.
            * Use of GA to form a circle will not result in symmetry  being used in the
            calculation. It is a good way to form the beginning of the circle, to be
            completed by GR, however.
        """
        return self._geo.arc(tag_id, segments, rada, ang1, ang2, radius)

    def define_gain(
        self,
        grnd: int = -1,
        radwires: int = 0,
        nadc: float = 0,
        nagc: float = 0,
        grndrad: float = 0,
        wirerad: float = 0,
        wirejr: float = 0,
        dm1m2: float = 0,
    ):
        """
        Specify the ground parameters of two mediums near the antenna.

        Args:
            grnd: Ground type
                -1: Nullify previous ground parameters
                0: Finite ground; uses reflection coefficient approx.
                1: Perfectly conducting ground
                2: Finite ground; uses Sommerfeld/Norton method

            radwires: Number of radial wires in ground screen approx.
                0: No ground screen

            nadc: Relative dielectric constant near the antenna
                0: Perfect ground

            nagc: Ground conductivity near the antenna
                0: Perfect ground
                < 0: Complex dielectric constant; see documentation

            grndrad: Ground radius
                0: Infinite ground plane
                > 0: Radius of ground screen [m]
                < 0: Relative dielectric constant of medium 2

            wirerad: Radius of wires used in ground screen
                0: Infinite ground plane
                > 0: Radius of wires used in ground screen
                < 0: Conductivity of medium 2 [mho/m]

            wirejr: Wire join radius
                0: Infinite ground plane
                > 0: Dist. from origin to join between mediums 1 and 2. Either the
                    radius of the circle where the media join or distance from X-axis
                    to where the media join in a line parallel to the Y-axis. Circular
                    versus linear specification is done using RP card.

            dm1m2: Relative distances of surfaces of mediums 1 and 2
                0: Infinite ground plane if wire radius > 0.
                other: Positive or zero dist. by which med 2 is below med 1

        Returns:
                object: <PyNEC gain object>
        """
        self._context.gn_card(
            grnd, radwires, nadc, nagc, grndrad, wirerad, wirejr, dm1m2
        )

    def define_excitation(
        self,
        ex_type: int = 0,
        tag_theta: int = 0,
        rnk_phi: Optional[int] = None,
        pnt_ra: int = 0,
        chk_imp: int = 0,
        vlt_theta: float = 0,
        ivlt_phi: float = 0,
        imp_nu: float = 0,
        theta_cur: float = 0,
        phi_cur: float = 0,
        curm_pol: float = 0,
    ):
        """
        Specify the ground parameters of two mediums near the antenna.

        Args:
            ex_type: Excitation type
                0: Voltage source due to applied E-field
                1: Incident plane wave, linearly polarized
                2: Incident plane wave, right-hand ellip. polarized
                3: Incident plane wave, left-hand ellip. polarized
                4: Elementary current source
                5: Voltage source due to current-slope discontinuity

            tag_theta: Tag number of source segment | number of Theta angles
                    0: Tag number of source segment using abs. seg. numbers
                    1: Number of theta angles
                    2: Number of theta angles
                    3: Number of theta angles
                    4: -
                    5: Tag number of source segment

            rnk_phi: Rank or source segment number | number of Phi angles
                    0: Rank or source segment number using abs. numbers
                    1: Number phi angles desired for plane wave
                    2: Number phi angles desired for plane wave
                    3: Number phi angles desired for plane wave
                    4: -
                    5: Rank of segment number of the source

            pnt_ra: Print relative admittance maxtrix asymmetry
                    0: Otherwise
                    1: Print max. relative admittance matrix asymmetry
                        (if extype=0|5, network connections are printed)

            chk_imp: Check if impedance is included
                    0: Otherwise
                    1: If extype=0|5, accounts for impedance (impNu)

            vlt_theta: Voltages -or- Values of theta -or- current source
                    if extype=0|5: Real part of the voltage
                    if extype=1|2|3: First value of theta
                    else: X-coordinate of the current source

            ivlt_phi: Voltages -or- Values of phi -or- current source
                    if extype=0|5: Imaginary part of the voltage
                    if extype=1|2|3: First value of phi
                    else: Y-coordinate of the current source

            imp_nu: Impedance -or- polarization -or- current source
                    if extype=0|5: Normalization const. of impedance
                    if extype=1|2|3: Polarization angle (eta) [deg.]
                    if extype=4: Z-coordinate of the current source

            theta_cur: Theta angle step -or- current source angle
                    if extype=0|5: Zero
                    if extype=1|2|3: Theta angle stepping increment
                    if extype=4: Angle of the current source w/ the XY plane

            phi_cur: Phi angle step -or- current source projection angle
                    if extype=0|5: Zero
                    if extype=1|2|3: Phi angle stepping increment
                    if extype=4: Projectionn angle of current src on XY plane

            curm_pol: Polarization -or- curremtn moment
                    if extype=0|5: Zero
                    if extype=1|2|3: Minor/major axis ratio for ellip. pol.
                    if extype=4: "Current moment" of the source [A/m]

        Returns:
            object: <PyNEC excitation object>
        """
        if rnk_phi is None:
            rnk_phi = self.source_index

        self._context.ex_card(
            ex_type,
            tag_theta,
            rnk_phi,
            pnt_ra,
            chk_imp,
            vlt_theta,
            ivlt_phi,
            imp_nu,
            theta_cur,
            phi_cur,
            curm_pol,
        )

    def define_frequency(
        self,
        step_type: int = 0,
        num_step: int = 2,
        first_val: float = 2400,
        step_incr: float = 100e6,
    ):
        """
        Specify the source frequencies.

            Args:
                step_type: Type of frequency stepping
                    0: Linear
                    1: Multiplicative

                num_step: The number of frequency steps

                first_val: The first frequency value [MHz]

                step_incr: The frequency stepping increment

            Returns:
                    object: <PyNEC frequency object>
        """
        self._context.fr_card(step_type, num_step, first_val, step_incr)

    def define_radiation(
        self,
        cmode: int = 0,
        theta_start: float = 0.0,
        theta_step: float = 1.0,
        num_theta: int = 361,
        phi_start: float = 0.0,
        phi_step: float = 1.0,
        num_phi: int = 361,
        out_form: int = 0,  # X
        norm_fctr: int = 0,  # N
        pwr_drct: int = 0,  # D
        calc_avg_gn: int = 0,  # A
        dfo: float = 100.0,
        gain_norm: float = 0.0,
    ):
        """
        Specify the radiation pattern parameters.

        Args:
            cmode: Calculation mode of the radiated field
                0: Normal mode, computes space-wave fields.
                1: Space-wave + surface wave propagating along ground
                2: Linear cliff with antenna above upper level
                3: Circular cliff centered at coordinate system origin
                4: Radial wire ground screen centered at origin
                5: Linear cliff + radial wire ground screen
                6: Circular cliff + radial wire ground screen

            num_theta: Number of Z-values -or- number of theta values
                if cmode=1: Number of Z-values

            num_phi: Number of phi values

            out_form: Output format
                if cmode=1: Zero
                0: if cmode!=1, prints major/minor axis, total gain
                1: if cmode!=1, prints vertical, horizontal, total gain

            norm_fctr: Normalization factor
                if cmode=1: Zero
                0: if cmode!=1, no normalization gain
                1: if cmode!=1, major axis gain normalized
                2: if cmode!=1, minor axis gain normalized
                3: if cmode!=1, vertical axis gain normalized
                4: if cmode!=1, horizontal axig gain normalized
                5: if cmode!=1, total gain normalized

            pwr_drct: Power or directed gain for printing and normalization
                if cmode=1: Zero
                0: if cmode!=1, power gain
                1: if cmode!=1, directive gain

            calc_avg_gn: Average power gain over region
                if cmode=1: Zero
                0: if cmode!=1, no averaging
                1: if cmode!=1, average gain computed
                2: if cmode!=1, avg. gain copmuted, suppress printing

            theta_start: Initial theta value -or- initial Z value
                if cmode=1: Initial Z value
                other: if cmode!=1, initial theta value

            phi_start: Initial phi value

            theta_step: Increment for theta -or- increment for Z
                if cmode=1: Increment for Z
                other: if cmode!=1, increment for theta

            phi_step: Phi increment

            dfo: Cyl. coord. rho -or- radial distance of field from origin
                if cmode=1: Cylindrical coordinate rho. (>1 wavelength)
                other: if cmode!=1, Radial dist. of field point from origin

            gain_norm: Gain normalization (if required)
                0: Gain is normalized to its maximum value

        Returns:
                object: <PyNEC radiation object>
        """
        self._context.rp_card(
            cmode,
            num_theta,
            num_phi,
            out_form,
            norm_fctr,
            pwr_drct,
            calc_avg_gn,
            theta_start,
            phi_start,
            theta_step,
            phi_step,
            dfo,
            gain_norm,
        )

    @abc.abstractmethod
    def _initialize(self):
        pass
