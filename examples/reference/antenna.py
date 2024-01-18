# ==============================================================================
#                               ANTENNA GEOMETRY                               =
# ==============================================================================
# type: ignore
"""
   Computing radiation from known antenna parameters.
"""

import math
import typing
import numpy as np
import plotly.graph_objs as go

from PyNEC import *
from typing import overload, Union
from meshlib import mrmeshpy as mm
from meshlib import mrmeshnumpy as mn
from rats.utils.conversions import freq_to_wvln
from rats.utils.meshlogic import sph2xyz, trace_from_mesh


# ---------------------------- ANTENNA COMPONENTS ------------------------------
def create_wire(
    context: typing.Any,
    geo: typing.Any,
    tagID: int = 0,
    segcnt: int = 2,
    x1: float = 0.0,
    y1: float = 0.0,
    z1: float = 0.0,
    x2: float = 0.01,
    y2: float = 0.0,
    z2: float = 0.0,
    rad: float = 0.001,
    rdel: float = 1.0,
    rrad: float = 1.0,
) -> Union[float, int, typing.Any]:
    """
    Generates a string of segments to represent a straight wire. Units are in m.

    Args:
        tagID: Tag identification number assigned to all segments
        segcnt: Number of segments definin6 wire
        x1: Wire start position (X)
        y1: Wire start position (Y)
        z1: Wire start position (Z)
        x2: Wire end position (X)
        y2: Wire end position (Y)
        z2: Wire end position (Z)
        rad: Wire radius (`0` if tapered); `GC` card defines taper.
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
    # object = geo.wire(tagID, segcnt, x1, y1, z1, x2, y2, z2, rad, rdel, rrad)
    # return geo.wire(tagID, segcnt, x1, y1, z1, x2, y2, z2, rad, rdel, rrad)
    geodata = np.array(["cylinder", x1, y1, z1, x2, y2, z2])
    return (
        context,
        geodata,
        geo.wire(tagID, segcnt, x1, y1, z1, x2, y2, z2, rad, rdel, rrad),
    )


def create_arc(
    tagID: int = 0,
    segcnt: int = 36,
    rada: float = 0.5,
    ang1: float = 0.0,
    ang2: float = 180.0,
    rad: float = 0.001,
) -> Union[int, float, typing.Any]:
    """
    Generates a string of segments to represent a straight wire. Units are in m,
    and angles (`ang1`,`ang2`) are measured from the X-axis to the left-hand
    direction about the Y-axis in degrees.

    Args:
        tagID: Tag identification number assigned to all segments
        segcnt: Number of segments definint wire
        rada: Arc radius [m]; center is the origin; see notes.
        ang1: Angle of the 1st end of the arc
        ang2: Angle of the 2nd end of the arc
        rad: Wire radius

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
    return context, geo.arc(tagID, segcnt, rada, ang1, ang2, rad)


def create_helix(
    s: float = 1.0,
    hl: float = 3.0,
    a1: float = 1.0,
    b1: float = 1.0,
    a2: float = 1.0,
    b2: float = 1.0,
    rad: float = 0.001,
    tagid: int = 0,
    segcnt: int = 36,
) -> Union[float, int, typing.Any]:
    """
    Generates a helix or spiral of wire segments.

    Args:
        s: Spacing between helix turns
        hl: Total length of the helix
        a1: Helical radius (X) at z = 0
        b1: Helical radius (Y) at z = 0
        a2: Helical radius (X) at z = hl
        b2: Helical radius (Y) at z = hl
        rad: Radius of the wire
        seg_cnt: Number of segments comprising the helix
        tag_id: Tag number assigned to all segments of the helix

    Returns:
        object: <PyNEC geometry object>

    NOTES:
        * The segments generated by GA form a section of polygons inscribed within
    the arc
        * If an arc in a different position or orientation is desired, the segements
        may be moved within a GM card.
        * Use of GA to form a circle will not result in symmetry  being used in
        the calculation. It is a good way to form the beginning of the circle,
        to be completed by GR, however.
    """
    return context, geo.helix(s, hl, a1, b1, a2, b2, rad, tagid, segcnt)


def define_gain(
    context: typing.Any,
    grnd: int = -1,
    radwires: int = 0,
    nadc: float = 0,
    nagc: float = 0,
    grndrad: float = 0,
    wirerad: float = 0,
    wirejr: float = 0,
    dm1m2: float = 0,
) -> Union[int, float, typing.Any]:
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
    return context.gn_card(grnd, radwires, nadc, nagc, grndrad, wirerad, wirejr, dm1m2)


def define_excitation(
    context: typing.Any,
    extype: int = 0,
    tagTheta: int = 1,
    rnkPhi: int = 1,
    pntRa: int = 0,
    chkimp: int = 0,
    vltTheta: float = 0,
    ivltPhi: float = 0,
    impNu: float = 0,
    thetaCur: float = 0,
    phiCur: float = 0,
    curmPol: float = 0,
) -> Union[int, float, typing.Any]:
    """
    Specify the ground parameters of two mediums near the antenna.

    Args:
        extype: Excitation type
            0: Voltage source due to applied E-field
            1: Incident plane wave, linearly polarized
            2: Incident plane wave, right-hand ellip. polarized
            3: Incident plane wave, left-hand ellip. polarized
            4: Elementary current source
            5: Voltage source due to current-slope discontinuity

        tagTheta: Tag number of source segment | number of Theta angles
                0: Tag number of source segment using abs. seg. numbers
                1: Number of theta angles
                2: Number of theta angles
                3: Number of theta angles
                4: -
                5: Tag number of source segment

        rnkPhi: Rank or source segment number | number of Phi angles
                0: Rank or source segment number using abs. numbers
                1: Number phi angles desired for plane wave
                2: Number phi angles desired for plane wave
                3: Number phi angles desired for plane wave
                4: -
                5: Rank of segment number of the source

        pntRa: Print relative admittance maxtrix asymmetry
                0: Otherwise
                1: Print max. relative admittance matrix asymmetry
                    (if extype=0|5, network connections are printed)

        chkimp: Check if impedance is included
                0: Otherwise
                1: If extype=0|5, accounts for impedance (impNu)

        vltTheta: Voltages -or- Values of theta -or- current source
                if extype=0|5: Real part of the voltage
                if extype=1|2|3: First value of theta
                else: X-coordinate of the current source

        ivltPhi: Voltages -or- Values of phi -or- current source
                if extype=0|5: Imaginary part of the voltage
                if extype=1|2|3: First value of phi
                else: Y-coordinate of the current source

        impNu: Impedance -or- polarization -or- current source
                if extype=0|5: Normalization const. of impedance
                if extype=1|2|3: Polarization angle (eta) [deg.]
                if extype=4: Z-coordinate of the current source

        thetaCur: Theta angle step -or- current source angle
                if extype=0|5: Zero
                if extype=1|2|3: Theta angle stepping increment
                if extype=4: Angle of the current source w/ the XY plane

        phiCur: Phi angle step -or- current source projection angle
                if extype=0|5: Zero
                if extype=1|2|3: Phi angle stepping increment
                if extype=4: Projectionn angle of current src on XY plane

        curmPol: Polarization -or- curremtn moment
                if extype=0|5: Zero
                if extype=1|2|3: Minor/major axis ratio for ellip. pol.
                if extype=4: "Current moment" of the source [A/m]

    Returns:
        object: <PyNEC excitation object>
    """
    return context.ex_card(
        extype,
        tagTheta,
        rnkPhi,
        pntRa,
        chkimp,
        vltTheta,
        ivltPhi,
        impNu,
        thetaCur,
        phiCur,
        curmPol,
    )


def define_frequency(
    context: typing.Any,
    steptype: int = 0,
    numstep: int = 1,
    firstval: float = 2400,
    stepincr: float = 10,
) -> Union[int, float, typing.Any]:
    """
    Specify the source frequencies.

        Args:
            steptype: Type of frequency stepping
                0: Linear
                1: Multiplicative

            numstep: The number of frequency steps

            firstval: The first frequency value [MHz]

            stepincr: The frequency stepping increment

        Returns:
                object: <PyNEC frequency object>
    """
    return context.fr_card(steptype, numstep, firstval, stepincr)


def define_radiation(
    context: typing.Any,
    cmode: int = 0,
    numtheta: int = 360,
    numphi: int = 360,
    outform: int = 0,
    normfctr: int = 0,
    pwrdrct: int = 1,
    calcavggn: int = 0,
    thetastart: float = 5.0,
    phistart: float = 5.0,
    thetastep: float = 1.0,
    phistep: float = 1.0,
    dfo: float = 1000,
    gainnorm: float = 0.0,
) -> Union[int, float, typing.Any]:
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

        numtheta: Number of Z-values -or- number of theta values
            if cmode=1: Number of Z-values

        numphi: Number of phi values

        outform: Output format
            if cmode=1: Zero
            0: if cmode!=1, prints major/minor axis, total gain
            1: if cmode!=1, prints vertical, horizontal, total gain

        normfctr: Normalization factor
            if cmode=1: Zero
            0: if cmode!=1, no normalization gain
            1: if cmode!=1, major axis gain normalized
            2: if cmode!=1, minor axis gain normalized
            3: if cmode!=1, vertical axis gain normalized
            4: if cmode!=1, horizontal axig gain normalized
            5: if cmode!=1, total gain normalized

        pwrdrct: Power or directed gain for printing and normalization
            if cmode=1: Zero
            0: if cmode!=1, power gain
            1: if cmode!=1, directive gain

        calcavggn: Average power gain over region
            if cmode=1: Zero
            0: if cmode!=1, no averaging
            1: if cmode!=1, average gain computed
            2: if cmode!=1, avg. gain copmuted, suppress printing

        thetastart: Initial theta value -or- initial Z value
            if cmode=1: Initial Z value
            other: if cmode!=1, initial theta value

        phistart: Initial phi value

        thetastep: Increment for theta -or- increment for Z
            if cmode=1: Increment for Z
            other: if cmode!=1, increment for theta

        phistep: Phi increment

        dfo: Cyl. coord. rho -or- radial distance of field from origin
            if cmode=1: Cylindrical coordinate rho. (>1 wavelength)
            other: if cmode!=1, Radial dist. of field point from origin

        gainnorm: Gain normalization (if required)
            0: Gain is normalized to its maximum value

    Returns:
            object: <PyNEC radiation object>
    """
    return context.rp_card(
        cmode,
        numtheta,
        numphi,
        outform,
        normfctr,
        pwrdrct,
        calcavggn,
        thetastart,
        phistart,
        thetastep,
        phistep,
        dfo,
        gainnorm,
    )


def define_txLine(
    seg1: int = 1,
    aseg1: int = 1,
    seg2: int = 2,
    aseg2: int = 2,
    chimp: float = 0.1,
    txlen: float = 1.1,
    rshunt1: float = 0.5,
    ishunt1: float = 0.0,
    rshunt2: float = 0.5,
    ishunt2: float = 0.0,
) -> Union[int, float, typing.Any]:
    """
    Generate a transmission (Tx) line between any two points on the structure.

    Args:
        seg1: Segment tag number where 1st end of tx line is connected
            0: Segment identification uses absolute segment number

        aseg1: Abs. seg. number where 1st end of txline is conn

        seg2: Segment tag number where 2nd end of tx line is connected
            0: Segment identification uses absolute segment number

        aseg2: Abs. seg. number where 2nd end of tx line is connected

        chimp: Characteristic impedance of Tx line [Ohms]
            <0: Generates a tx line w/ 180 deg. phase reversal

        txlen: Length of the transmission line [m]

        rshunt1: Real part of the shunt admittance at 1st end [Mhos]

        ishunt1: Imag. part of the shunt admittance at 1st end [Mhos]

        rshunt2: Real part of the shunt admittance at 2nd end [Mhos]

        ishunt2: Imag. part of the shunt admittance at 2nd end [Mhos]

    Returns:
            object: <PyNEC transmission line object>
    """
    return context.tl_card(
        seg1, aseg1, seg2, aseg2, chimp, txlen, rshunt1, ishunt1, rshunt2, ishunt2
    )


def define_printcurr(
    pntctl: int = -2, segnums: int = 2, asnstart: int = 1, asnend: int = 2
) -> Union[int, typing.Any]:
    """
    Controls for printing the currents.

    Args:
        pntctl: Print control flag specifying format used in printing
            -2: Print all currents (default if PT card is omitted)
            -1: Suppress printing of all wire segment currents
            0: Only print currents specified by other arguments
            1: Same as 0; currents print w/ format for receivers
            2: Same as 1; Current for one segment will be normalized

        segnums: Number of segments containing currents to print
            2: Absolute segment numbers will be used.

        asnstart: Abs. seg. no. of first segment w/ currents to print

        asnend: Abs. seg. no., of last segment w/ currents to print

    Returns:
        object: <PyNEC printing object>
    """
    return context.pt_card(pntctl, segnums, asnstart, asnend)


def define_printchrg(
    pntctl: int = -2, segnums: int = 2, asnstart: int = 1, asnend: int = 2
) -> Union[int, typing.Any]:
    """
    Controls for printing the currents.

    Args:
        pntctl: Print control flag specifying format used in printing
            -2: Print all charge densities
            1: Suppress printing charge densities [default]
            0: Print charge densities on segments specified

        segnums: Number segments containing charge densities to print
            0: Absolute segment numbers will be used.

        asnstart: Abs. seg. no. of first segment w/ chrg dens to print
            asnstart=asnend=0: Print all charge densities

        asnend: Abs. seg. no., of last segment w/ chrg dens to print
            asnstart=asnend=0: Print all charge densities

    Returns:
        object: <PyNEC printing object>
    """
    return context.pq_card(pntctl, segnums, asnstart, asnend)


# ----------------------------- ANTENNA TEMPLATES ------------------------------
def dipole_antenna(
    context: typing.Any, geo: typing.Any, n: int = 1, dsn_frq: float = 400
) -> Union[int, float, typing.Any]:
    """
    Generates a 3-node dipole array with directors extending in the X-Y plane.

    Args:
        dsn_frq: The desired operation frequency of the antenna [MHz]
        n: The preferred integer multiple of half-wavelengths

    Returns:
        object: <PyNEC geometry object>
        x: X-position array of each point comprising the antenna
        y: Y-position array of each point comprising the antenna
        z: Z-position array of each point comprising the antenna

    Sample use:
        dsn_frq = 2000              # MHz
        n = 1
        context,gd,x,y,z = dipole_antenna(dsn_frq,n)
    """
    # Convert design frequency to length [m]
    wvl = freq_to_wvln(dsn_frq)
    l = n * wvl / 2

    # Left spoke
    x1, y1, z1 = 0, 0, -l / 2
    x2, y2, z2 = 0, 0, 0
    x3, y3, z3 = 0, 0, l / 2
    # Left spoke
    context, gd, _ = create_wire(
        context, geo, tagID=0, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
    )
    # Right spoke
    _, _, _ = create_wire(
        context, geo, tagID=1, x1=x2, y1=y2, z1=z2, x2=x3, y2=y3, z2=z3
    )

    return context, gd


def turnstile_antenna(
    context: typing.Any, geo: typing.Any, n: int = 1, dsn_frq: float = 400
) -> Union[int, float, typing.Any]:
    """
    Generates a turnstile array with directors extending in the X-Y plane.

    Args:
        dsn_frq: The desired operation frequency of the antenna [MHz]
        n: The preferred integer multiple of half-wavelengths

    Returns:
        object: <PyNEC geometry object>
        x: X-position array of each point comprising the antenna
        y: Y-position array of each point comprising the antenna
        z: Z-position array of each point comprising the antenna

    Sample use:
        dsn_frq = 2000              # MHz
        n = 1
        context,gd,x,y,z = turnstile_antenna(dsn_frq,n)
    """

    # Convert design frequency to length
    wvl = freq_to_wvln(dsn_frq)
    l = n * wvl / 2

    # Left spoke
    x1, y1, z1 = -l / 2, 0, 0
    x2, y2, z2 = 0, 0, 0
    x3, y3, z3 = 0, l / 2, 0
    x4, y4, z4 = l / 2, 0, 0
    x5, y5, z5 = 0, -l / 2, 0
    # Left spoke
    context, gd, _ = create_wire(
        context, geo, tagID=0, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
    )
    # Top spoke
    _, _, _ = create_wire(
        context, geo, tagID=1, x1=x2, y1=y2, z1=z2, x2=x3, y2=y3, z2=z3
    )
    # Right spoke
    _, _, _ = create_wire(
        context, geo, tagID=2, x1=x2, y1=y2, z1=z2, x2=x4, y2=y4, z2=z4
    )
    # Bottom spoke
    _, _, _ = create_wire(
        context, geo, tagID=3, x1=x2, y1=y2, z1=z2, x2=x5, y2=y5, z2=z5
    )
    return context, gd, x, y, z


def yagi_uda_2D(
    context: typing.Any,
    geo: typing.Any,
    num_sets: int,
    red_rat: float,
    dsn_frq: float = 400,
) -> Union[int, float, typing.Any]:
    """
    Generates flat Yagi-Uda array with directors extending only in the X-Y plane.

    Args:
        dsn_frq: The desired operation frequency of the antenna [MHz]
        num_sets: The number of sets of directors comprising the antenna
        red_rat: The reduction ratio between the first and final directors

    Returns:
        object: <PyNEC geometry object>
        x: X-position array of each point comprising the antenna
        y: Y-position array of each point comprising the antenna
        z: Z-position array of each point comprising the antenna

    Sample use:
        dsn_frq = 2000              # MHz
        num_sets = 15
        reduce_rat = 1.0
        context,gd,x,y,z = yagi_uda_1D(dsn_frq,num_sets=10,reduce_rat=0.1)
    """

    # Calculate spacing from design frequency
    wvl = freq_to_wvln(dsn_frq)

    # Determine resonant arm lengths
    arm_pitch = wvl / 4  # m
    arm_len = wvl / 4
    start_wid = arm_len
    end_wid = red_rat * start_wid

    # Iterate wires to create antenna
    for tag_ID in np.arange(num_sets):
        x_start = tag_ID * arm_pitch
        x_end = (tag_ID + 1) * arm_pitch

        # Left parasitic element
        tin = int(3 * tag_ID)
        y1, y2 = -(start_wid - tag_ID * ((start_wid - end_wid) / (num_sets - 1))), 0.0
        x1, x2 = x_start, x_start
        z1, z2 = 0.0, 0.0
        if tag_ID == 0:
            context, gd, _ = create_wire(
                context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
            )
        else:
            _, _, _ = create_wire(
                context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
            )

        # Right parasitic element
        tin = int(3 * tag_ID + 1)
        y1, y2 = start_wid - tag_ID * ((start_wid - end_wid) / (num_sets - 1)), 0.0
        x1, x2 = x_start, x_start
        z1, z2 = 0.0, 0.0
        _, _, _ = create_wire(
            context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
        )

        # Center extension
        if tag_ID < num_sets - 1:
            tin = int(3 * tag_ID + 2)
            y1, y2 = 0.0, 0.0
            x1, x2 = x_start, x_end
            z1, z2 = 0.0, 0.0
            _, _, _ = create_wire(
                context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
            )

    return context, gd


def yagi_uda_3D(
    context: typing.Any,
    geo: typing.Any,
    num_sets: int,
    red_rat: float,
    dsn_frq: float = 400,
) -> Union[int, float, typing.Any]:
    """
    Generates flat Yagi-Uda array with directors extending only in the X-Y plane.

    Args:
        dsn_frq: The desired operation frequency of the antenna [MHz]
        num_sets: The number of sets of directors comprising the antenna
        red_rat: The reduction ratio between the first and final directors

    Returns:
        object: <PyNEC geometry object>

    Sample use:
        dsn_frq = 2000              # MHz
        num_sets = 15
        reduce_rat = 1.0
        context,gd,x,y,z = yagi_uda_2D(dsn_frq,num_sets=10,reduce_rat=0.1)
    """

    # Convert desired frequency to wavelength
    wvl = freq_to_wvln(dsn_frq)

    # Determine resonant arm lengths
    arm_pitch = wvl / 4  # m
    arm_len = wvl / 4
    start_wid = arm_len
    end_wid = red_rat * start_wid
    wires = []

    # Iterate wires to create antenna
    for tag_ID in np.arange(num_sets):
        x_start = tag_ID * arm_pitch
        x_end = (tag_ID + 1) * arm_pitch

        # Left parasitic element
        tin = int(5 * tag_ID)
        y1, y2 = -(start_wid - tag_ID * ((start_wid - end_wid) / (num_sets - 1))), 0.0
        x1, x2 = x_start, x_start
        z1, z2 = 0.0, 0.0
        wires.append(
            {
                "start": np.array([x1, y1, z1]),
                "end": np.array([x2, y2, z2]),
                "tid": tag_ID,
            }
        )
        if tag_ID == 0:
            context, gd, _ = create_wire(
                context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
            )
        else:
            _, _, _ = create_wire(
                context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
            )

        # Right parasitic element
        tin = int(5 * tag_ID + 1)
        y1, y2 = start_wid - tag_ID * ((start_wid - end_wid) / (num_sets - 1)), 0.0
        x1, x2 = x_start, x_start
        z1, z2 = 0.0, 0.0
        wires.append(
            {
                "start": np.array([x1, y1, z1]),
                "end": np.array([x2, y2, z2]),
                "tid": tag_ID,
            }
        )
        _, _, _ = create_wire(
            context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
        )

        # Top parasitic element
        tin = int(5 * tag_ID + 2)
        y1, y2 = 0.0, 0.0
        x1, x2 = x_start, x_start
        z1, z2 = start_wid - tag_ID * ((start_wid - end_wid) / (num_sets - 1)), 0.0
        wires.append(
            {
                "start": np.array([x1, y1, z1]),
                "end": np.array([x2, y2, z2]),
                "tid": tag_ID,
            }
        )
        _, _, _ = create_wire(
            context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
        )

        # Bottom parasitic element
        tin = int(5 * tag_ID + 3)
        y1, y2 = 0.0, 0.0
        x1, x2 = x_start, x_start
        z1, z2 = -(start_wid - tag_ID * ((start_wid - end_wid) / (num_sets - 1))), 0.0
        wires.append(
            {
                "start": np.array([x1, y1, z1]),
                "end": np.array([x2, y2, z2]),
                "tid": tag_ID,
            }
        )
        _, _, _ = create_wire(
            context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
        )

        # Center extension
        if tag_ID < num_sets - 1:
            tin = int(5 * tag_ID + 4)
            y1, y2 = 0.0, 0.0
            x1, x2 = x_start, x_end
            z1, z2 = 0.0, 0.0
            wires.append(
                {
                    "start": np.array([x1, y1, z1]),
                    "end": np.array([x2, y2, z2]),
                    "tid": tag_ID,
                }
            )
            _, _, _ = create_wire(
                context, geo, tagID=tin, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
            )

    return context, gd, wires


def bowtie_antenna(
    context: typing.Any, geo: typing.Any, dsn_frq: float
) -> Union[int, float, typing.Any]:
    """
    Generates a bowtie array in the X-Y plane. The creation of each point is
    documented in the User Manual.

    Args:
        dsn_frq: The desired operation frequency of the antenna [MHz]

    Returns:
        object: <PyNEC geometry object>
        x: X-position array of each point comprising the antenna
        y: Y-position array of each point comprising the antenna
        z: Z-position array of each point comprising the antenna

    Sample use:
        dsn_frq = 2000              # MHz
        context,gd,x,y,z = bowtie_antenna(dsn_frq,n=1)
    """

    # Convert design frequency to wavelength; determine geometry parameters
    wvl = freq_to_wvln(dsn_frq)
    h = 0.25 * wvl  # meters
    w = 0.375 * wvl  # meters
    d = 0.02066 * wvl  # meters

    # Center, upper left (CUL) -> Left half, upper point (LUP)
    x1, y1, z1 = 0, -d / 2, 0
    x2, y2, z2 = 0, -w - d / 2, h / 2
    x3, y3, z3 = 0, -w - d / 2, -h / 2
    x4, y4, z4 = 0, -d / 2, 0
    x5, y5, z5 = 0, -d / 2, -3 * d / 2
    x6, y6, z6 = 0, 0, -3 * d / 2
    x7, y7, z7 = 0, 0, 0
    x8, y8, z8 = 0, w, h / 2
    x9, y9, z9 = 0, w, -h / 2
    x10, y10, z10 = 0, 0, 0
    context, gd, _ = create_wire(
        context, geo, tagID=0, x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2
    )
    # Left half, upper point (LUP) -> Left half, lower point (LLP)
    _, _, _ = create_wire(
        context, geo, tagID=1, x1=x2, y1=y2, z1=z2, x2=x3, y2=y3, z2=z3
    )
    # Left half, lower point (LLP) -> Center, upper left (CUL)
    _, _, _ = create_wire(
        context, geo, tagID=2, x1=x3, y1=y3, z1=z3, x2=x4, y2=y4, z2=z4
    )
    # Center, upper left (CUL) -> Center, lower left (CLL)
    _, _, _ = create_wire(
        context, geo, tagID=3, x1=x4, y1=y4, z1=z4, x2=x5, y2=y5, z2=z5
    )
    # Center, lower left (CLL) -> Center, lower right (CLR)
    _, _, _ = create_wire(
        context, geo, tagID=4, x1=x5, y1=y5, z1=z5, x2=x6, y2=y6, z2=z6
    )
    # Center, lower right (CLR) -> Center, upper right (CUR)
    _, _, _ = create_wire(
        context, geo, tagID=5, x1=x6, y1=y6, z1=z6, x2=x7, y2=y7, z2=z7
    )
    # Center, upper right (CUR) -> Right half, upper point (RUP)
    _, _, _ = create_wire(
        context, geo, tagID=6, x1=x7, y1=y7, z1=z7, x2=x8, y2=y8, z2=z8
    )
    # Right half, upper point (RUP) -> Right half, lower point (RLP)
    _, _, _ = create_wire(
        context, geo, tagID=7, x1=x8, y1=y8, z1=z8, x2=x9, y2=y9, z2=z9
    )
    # Right half, lower point (RLP) -> Center, upper right (CUR)
    _, _, _ = create_wire(
        context, geo, tagID=8, x1=x9, y1=y9, z1=z9, x2=x10, y2=y10, z2=z10
    )
    return context, gd


def helical_antenna(
    context: typing.Any,
    geo: typing.Any,
    n_turns: int,
    wire_rad: float,
    seg_cnt: int,
    tag_id: int,
    dsn_frq: float = 400,
) -> Union[int, float, typing.Any]:
    """
    Generates a single helical antenna extending along the Z-axis. Note: There
    are recognized issues with this function, see issue RATS-49 on the JIRA board.

    Args:
        dsn_frq: The desired operation frequency of the antenna [MHz]
        n_turns: The number of turns of the helix
        wire_rad: The radius of the wire [m]
        seg_cnt: The number of segments comprising the helix.
        tag_id: The tag ID to be given to each element of the helix.

    Returns:
        object: <PyNEC geometry object>

    Sample use:
        dsn_frq = 2000              # MHz
        context,gd,x,y,z = helical_antenna(dsn_frq)
    """
    # Convert desired frequency to meters
    wvl = freq_to_wvln(dsn_frq)

    # Determine optimal antenna parameters
    D = wvl / math.pi
    S = 0.225 * wvl
    a1 = b1 = a2 = b2 = D / 2
    HL = S * n_turns
    context, _ = create_helix(
        s=S,
        hl=HL,
        a1=a1,
        b1=b1,
        a2=a2,
        b2=b2,
        rad=wire_rad,
        tagid=tag_id,
        segcnt=seg_cnt,
    )
    return context


def get_radiation(
    ant_type: str,
    num_sets: int = 10,
    red_rat: float = 0.1,
    n_turns: int = 10,
    wire_rad: float = 0.1,
    seg_cnt: int = 3,
    dsn_frq: float = 400,
) -> Union[str, int, float, typing.Any]:
    """
    Calls PyNEC to compute radiation for a given antenna type.

    Args:
        ant_type: The antenna type to be used in computation.
        num_sets: The number of sets of directors comprising the antenna
        red_rat: The reduction ratio between the first and final directors
        n_turns: The number of turns of the helix
        wire_rad: The radius of the wire [m]
        seg_cnt: The number of segments comprising the helix.
        dsn_frq: The desired operation frequency of the antenna [MHz]

    Returns:
        gain_db: Antenna gain in deciBels
        gain_pw: Antenna gain in Watts
        THETA: Theta values used to calculate gain for the antenna
        PHI: Phi values used to calculate gain for the antenna

    Sample use:
        dsn_frq = 4
        gdb,gpw,THETA,PHI = get_radiation(ant_type='dipole',dsn_frq=4)
    """
    # Instantiate a NEC context
    context = nec_context()
    # Retrieev the associated geometry
    geo = context.get_geometry()
    wires = None
    # Define antenna for radiation
    if ant_type == "dipole":
        context, _ = dipole_antenna(context, geo, dsn_frq=dsn_frq)
    elif ant_type == "turnstile":
        context, _ = turnstile_antenna(context, geo, dsn_frq=dsn_frq)
    elif ant_type == "yagi2d":
        context, _ = yagi_uda_2D(
            context, geo, dsn_frq=dsn_frq, num_sets=num_sets, red_rat=red_rat
        )
    elif ant_type == "yagi3d":
        context, _, wires = yagi_uda_3D(
            context, geo, dsn_frq=dsn_frq, num_sets=num_sets, red_rat=red_rat
        )
    elif ant_type == "bowtie":
        context, _ = bowtie_antenna(context, geo, dsn_frq)
    elif ant_type == "helical":
        context, _ = helical_antenna(context, geo, dsn_frq)

    # Complete antenna geometry
    context.geometry_complete(0)
    # Define antenna gain
    define_gain(context)
    # Define antenna excitation
    define_excitation(context)
    # Define source frequencies
    define_frequency(context, firstval=dsn_frq)
    # Radiation pattern parameters
    define_radiation(context)
    rp = context.get_radiation_pattern(0)
    gain_db = rp.get_gain()
    gain_pw = 10.0 ** (gain_db / 10.0)
    # Clear context & geometry
    del context, geo
    # Create meshgrid from Theta / Phi angles
    thetas = np.deg2rad(rp.get_theta_angles())
    phis = np.deg2rad(rp.get_phi_angles())
    THETA, PHI = np.meshgrid(thetas, phis)
    return gain_db, gain_pw, THETA, PHI, wires