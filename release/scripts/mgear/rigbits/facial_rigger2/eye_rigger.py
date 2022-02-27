import json
import traceback
from six import string_types

import mgear
import pymel.core as pm
from mgear.core import meshNavigation, curve, applyop, node, primitive, icon
from mgear.core import transform, utils, attribute, skin, string
from pymel.core import datatypes

from mgear import rigbits

# TODO: change deformers_group to static_rig_parent
# for the moment we keep this for backwards compativility with
# old configuration files
##########################################################
# Eye rig constructor
##########################################################


def rig(
    eyeMesh=None,
    edgeLoop="",
    blinkH=20,
    namePrefix="eye",
    offset=0.05,
    rigidLoops=2,
    falloffLoops=4,
    headJnt=None,
    doSkin=True,
    parent_node=None,
    ctlName="ctl",
    sideRange=False,
    customCorner=False,
    intCorner=None,
    extCorner=None,
    ctlSet=None,
    defSet=None,
    upperVTrack=0.02,
    upperHTrack=0.01,
    lowerVTrack=0.02,
    lowerHTrack=0.01,
    aim_controller="",
    deformers_group="",
    everyNVertex=1,
):
    """Create eyelid and eye rig

    Args:
        eyeMesh (TYPE): Description
        edgeLoop (TYPE): Description
        blinkH (TYPE): Description
        namePrefix (TYPE): Description
        offset (TYPE): Description
        rigidLoops (TYPE): Description
        falloffLoops (TYPE): Description
        headJnt (TYPE): Description
        doSkin (TYPE): Description
        parent_node (None, optional): Description
        ctlName (str, optional): Description
        sideRange (bool, optional): Description
        customCorner (bool, optional): Description
        intCorner (None, optional): Description
        extCorner (None, optional): Description
        ctlSet (None, optional): Description
        defSet (None, optional): Description
        upperVTrack (None, optional): Description
        upperHTrack (None, optional): Description
        lowerVTrack (None, optional): Description
        lowerHTrack (None, optional): Description
        aim_controller (None, optional): Description
        deformers_group (None, optional): Description
        everyNVertex (int, optional): Will create a joint every N vertex

    No Longer Returned:
        TYPE: Description
    """

    ##########################################
    # INITIAL SETUP
    ##########################################
    up_axis = pm.upAxis(q=True, axis=True)
    # print(up_axis)
    if up_axis == "z":
        z_up = True
        # print("Z_up!!!")
    else:
        z_up = False
        # print("Y_up!!!")

    # getters
    edgeLoopList = get_edge_loop(edgeLoop)
    eyeMesh = get_eye_mesh(eyeMesh)

    # checkers
    if not edgeLoopList or not eyeMesh:
        return
    if doSkin:
        if not headJnt:
            pm.displayWarning(
                "Please set the Head Jnt or unCheck "
                "Compute Topological Autoskin"
            )
            return

    # Convert data
    blinkH = blinkH / 100.0

    # Initial Data
    bboxCenter = meshNavigation.bboxCenter(eyeMesh)

    extr_v = meshNavigation.getExtremeVertexFromLoop(
        edgeLoopList, sideRange, z_up
    )
    upPos = extr_v[0]
    lowPos = extr_v[1]
    inPos = extr_v[2]
    outPos = extr_v[3]
    edgeList = extr_v[4]
    vertexList = extr_v[5]

    # Detect the side L or R from the x value
    if inPos.getPosition(space="world")[0] < 0.0:
        side = "R"
        inPos = extr_v[3]
        outPos = extr_v[2]
        normalPos = outPos
        npw = normalPos.getPosition(space="world")
        normalVec = npw - bboxCenter
    else:
        side = "L"
        normalPos = outPos
        npw = normalPos.getPosition(space="world")
        normalVec = bboxCenter - npw

    # Manual Vertex corners
    if customCorner:
        if intCorner:
            try:
                if side == "R":
                    inPos = pm.PyNode(extCorner)
                else:
                    inPos = pm.PyNode(intCorner)
            except pm.MayaNodeError:
                pm.displayWarning("%s can not be found" % intCorner)
                return
        else:
            pm.displayWarning("Please set the internal eyelid corner")
            return

        if extCorner:
            try:
                normalPos = pm.PyNode(extCorner)
                npw = normalPos.getPosition(space="world")
                if side == "R":
                    outPos = pm.PyNode(intCorner)
                    normalVec = npw - bboxCenter
                else:
                    outPos = pm.PyNode(extCorner)
                    normalVec = bboxCenter - npw
            except pm.MayaNodeError:
                pm.displayWarning("%s can not be found" % extCorner)
                return
        else:
            pm.displayWarning("Please set the external eyelid corner")
            return

    # Check if we have prefix:
    if namePrefix:
        namePrefix = string.removeInvalidCharacter(namePrefix)
    else:
        pm.displayWarning("Prefix is needed")
        return

    def setName(name, ind=None):
        namesList = [namePrefix, side, name]
        if ind is not None:
            namesList[1] = side + str(ind)
        name = "_".join(namesList)
        return name

    if pm.ls(setName("root")):
        pm.displayWarning(
            "The object %s already exist in the scene. Please "
            "choose another name prefix" % setName("root")
        )
        return

    ##########################################
    # CREATE OBJECTS
    ##########################################

    # Eye root
    eye_root = primitive.addTransform(None, setName("root"))
    eyeCrv_root = primitive.addTransform(eye_root, setName("crvs"))

    # Eyelid Main crvs
    try:
        upEyelid_edge = meshNavigation.edgeRangeInLoopFromMid(
            edgeList, upPos, inPos, outPos
        )
        up_crv = curve.createCurveFromOrderedEdges(
            upEyelid_edge, inPos, setName("upperEyelid"), parent=eyeCrv_root
        )
        upCtl_crv = curve.createCurveFromOrderedEdges(
            upEyelid_edge, inPos, setName("upCtl_crv"), parent=eyeCrv_root
        )
        pm.rebuildCurve(upCtl_crv, s=2, rt=0, rpo=True, ch=False)

        lowEyelid_edge = meshNavigation.edgeRangeInLoopFromMid(
            edgeList, lowPos, inPos, outPos
        )
        low_crv = curve.createCurveFromOrderedEdges(
            lowEyelid_edge, inPos, setName("lowerEyelid"), parent=eyeCrv_root
        )
        lowCtl_crv = curve.createCurveFromOrderedEdges(
            lowEyelid_edge, inPos, setName("lowCtl_crv"), parent=eyeCrv_root
        )

        pm.rebuildCurve(lowCtl_crv, s=2, rt=0, rpo=True, ch=False)

    except UnboundLocalError:
        if customCorner:
            pm.displayWarning(
                "This error is maybe caused because the custom "
                "Corner vertex is not part of the edge loop"
            )
        pm.displayError(traceback.format_exc())
        return

    # blendshape  curves. All crv have 30 point to allow blendshape connect
    upDriver_crv = curve.createCurveFromCurve(
        up_crv, setName("upDriver_crv"), nbPoints=30, parent=eyeCrv_root
    )
    upDriver_crv.attr("lineWidth").set(5)
    lowDriver_crv = curve.createCurveFromCurve(
        low_crv, setName("lowDriver_crv"), nbPoints=30, parent=eyeCrv_root
    )
    lowDriver_crv.attr("lineWidth").set(5)

    upRest_target_crv = curve.createCurveFromCurve(
        up_crv, setName("upRest_target_crv"), nbPoints=30, parent=eyeCrv_root
    )
    lowRest_target_crv = curve.createCurveFromCurve(
        low_crv, setName("lowRest_target_crv"), nbPoints=30, parent=eyeCrv_root
    )
    upProfile_target_crv = curve.createCurveFromCurve(
        up_crv,
        setName("upProfile_target_crv"),
        nbPoints=30,
        parent=eyeCrv_root,
    )
    lowProfile_target_crv = curve.createCurveFromCurve(
        low_crv,
        setName("lowProfile_target_crv"),
        nbPoints=30,
        parent=eyeCrv_root,
    )

    # mid driver
    midUpDriver_crv = curve.createCurveFromCurve(
        up_crv, setName("midUpDriver_crv"), nbPoints=30, parent=eyeCrv_root
    )
    midLowDriver_crv = curve.createCurveFromCurve(
        low_crv, setName("midLowDriver_crv"), nbPoints=30, parent=eyeCrv_root
    )

    # curve that define the close point of the eyelid
    closeTarget_crv = curve.createCurveFromCurve(
        up_crv, setName("closeTarget_crv"), nbPoints=30, parent=eyeCrv_root
    )

    eyeCrv_root.attr("visibility").set(False)

    # localBBOX
    localBBox = eyeMesh.getBoundingBox(invisible=True, space="world")
    wRadius = abs((localBBox[0][0] - localBBox[1][0]))
    dRadius = abs((localBBox[0][1] - localBBox[1][1]) / 1.7)

    # Groups
    if not ctlSet:
        ctlSet = "rig_controllers_grp"
    try:
        ctlSet = pm.PyNode(ctlSet)
    except pm.MayaNodeError:
        pm.sets(n=ctlSet, em=True)
        ctlSet = pm.PyNode(ctlSet)
    if not defSet:
        defSet = "rig_deformers_grp"
    try:
        defset = pm.PyNode(defSet)
    except pm.MayaNodeError:
        pm.sets(n=defSet, em=True)
        defset = pm.PyNode(defSet)

    # Calculate center looking at
    averagePosition = (
        upPos.getPosition(space="world")
        + lowPos.getPosition(space="world")
        + inPos.getPosition(space="world")
        + outPos.getPosition(space="world")
    ) / 4
    if side == "R":
        negate = False
        offset = offset
        # over_offset = dRadius
    else:
        negate = False
        # over_offset = dRadius

    # if side == "R" and sideRange or side == "R" and customCorner:
    #     axis = "z-x"
    #     # axis = "zx"
    # else:
    #     axis = "z-x"
    if z_up:
        axis = "zx"
    else:
        axis = "z-x"
    # print(axis)
    t = transform.getTransformLookingAt(
        bboxCenter, averagePosition, normalVec, axis=axis, negate=negate
    )

    over_npo = primitive.addTransform(
        eye_root, setName("center_lookatRoot"), t
    )

    center_lookat = primitive.addTransform(
        over_npo, setName("center_lookat"), t
    )

    # Tracking
    # Eye aim control
    t_arrow = transform.getTransformLookingAt(
        bboxCenter,
        averagePosition,
        upPos.getPosition(space="world"),
        axis="zy",
        negate=False,
    )

    radius = abs((localBBox[0][0] - localBBox[1][0]) / 1.7)

    arrow_ctl = None
    arrow_npo = None
    if aim_controller:
        arrow_ctl = pm.PyNode(aim_controller)
    else:
        arrow_npo = primitive.addTransform(
            eye_root, setName("aim_npo"), t_arrow
        )
        arrow_ctl = icon.create(
            arrow_npo,
            setName("aim_%s" % ctlName),
            t_arrow,
            icon="arrow",
            w=1,
            po=datatypes.Vector(0, 0, radius),
            color=4,
        )
    if len(ctlName.split("_")) == 2 and ctlName.split("_")[-1] == "ghost":
        pass
    else:
        pm.sets(ctlSet, add=arrow_ctl)
    attribute.setKeyableAttributes(arrow_ctl, params=["rx", "ry", "rz"])
    attribute.addAttribute(arrow_ctl, "isCtl", "bool", keyable=False)

    # tracking custom trigger
    if side == "R":
        tt = t_arrow
    else:
        tt = t
    aimTrigger_root = primitive.addTransform(
        center_lookat, setName("aimTrigger_root"), tt
    )
    # For some unknown reason the right side gets scewed rotation values
    mgear.core.transform.resetTransform(aimTrigger_root)
    aimTrigger_lvl = primitive.addTransform(
        aimTrigger_root, setName("aimTrigger_lvl"), tt
    )
    # For some unknown reason the right side gets scewed rotation values
    mgear.core.transform.resetTransform(aimTrigger_lvl)
    aimTrigger_lvl.attr("tz").set(1.0)
    aimTrigger_ref = primitive.addTransform(
        aimTrigger_lvl, setName("aimTrigger_ref"), tt
    )
    # For some unknown reason the right side gets scewed rotation values
    mgear.core.transform.resetTransform(aimTrigger_ref)
    aimTrigger_ref.attr("tz").set(0.0)
    # connect  trigger with arrow_ctl
    pm.parentConstraint(arrow_ctl, aimTrigger_ref, mo=True)

    # Blink driver controls
    if z_up:
        trigger_axis = "tz"
        # ro_up = [1.57079633, 1.57079633, -1.57079633]
        ro_up = [0, 1.57079633 * 2, 1.57079633]
        ro_low = [0, 0, 1.57079633]
        # ro_low = [1.57079633, 1.57079633, 1.57079633 * 3]
        po = [offset * -1, 0, 0]
        low_pos = 2  # Z
    else:
        trigger_axis = "ty"
        ro_up = (1.57079633, 1.57079633, 0)
        ro_low = [1.57079633, 1.57079633, 1.57079633 * 2]
        po = [0, 0, offset]
        low_pos = 1  # Y

    # upper ctl
    p = upRest_target_crv.getCVs(space="world")[15]
    ut = transform.setMatrixPosition(datatypes.Matrix(), p)
    npo = primitive.addTransform(over_npo, setName("upBlink_npo"), ut)

    up_ctl = icon.create(
        npo,
        setName("upBlink_ctl"),
        ut,
        icon="arrow",
        w=2.5,
        d=2.5,
        ro=datatypes.Vector(ro_up[0], ro_up[1], ro_up[2]),
        po=datatypes.Vector(po[0], po[1], po[2]),
        color=4,
    )
    attribute.setKeyableAttributes(up_ctl, [trigger_axis])
    pm.sets(ctlSet, add=up_ctl)

    # use translation of the object to drive the blink
    blink_driver = primitive.addTransform(up_ctl, setName("blink_drv"), ut)

    # lowe ctl
    p_low = lowRest_target_crv.getCVs(space="world")[15]
    p[low_pos] = p_low[low_pos]
    lt = transform.setMatrixPosition(ut, p)
    npo = primitive.addTransform(over_npo, setName("upBlink_npo"), lt)

    low_ctl = icon.create(
        npo,
        setName("lowBlink_ctl"),
        lt,
        icon="arrow",
        w=1.5,
        d=1.5,
        ro=datatypes.Vector(ro_low[0], ro_low[1], ro_low[2]),
        po=datatypes.Vector(po[0], po[1], po[2]),
        color=4,
    )
    attribute.setKeyableAttributes(low_ctl, [trigger_axis])
    pm.sets(ctlSet, add=low_ctl)

    # Controls lists
    upControls = []
    trackLvl = []
    track_corner_lvl = []
    corner_ctl = []
    ghost_ctl = []

    # upper eyelid controls
    upperCtlNames = ["inCorner", "upInMid", "f", "upOutMid", "outCorner"]
    cvs = upCtl_crv.getCVs(space="world")
    if side == "R" and not sideRange:
        # if side == "R":
        cvs = [cv for cv in reversed(cvs)]
    for i, cv in enumerate(cvs):
        if utils.is_odd(i):
            color = 14
            wd = 0.3
            icon_shape = "circle"
            params = ["tx", "ty", "tz"]
        else:
            color = 4
            wd = 0.6
            icon_shape = "circle"
            params = [
                "tx",
                "ty",
                "tz",
                "ro",
                "rx",
                "ry",
                "rz",
                "sx",
                "sy",
                "sz",
            ]

        t = transform.setMatrixPosition(t, cvs[i])
        npo = primitive.addTransform(
            center_lookat, setName("%s_npo" % upperCtlNames[i]), t
        )
        npoBase = npo
        # track for corners and mid point level
        if i in [0, 2, 4]:
            # we add an extra level to input the tracking ofset values
            npo = primitive.addTransform(
                npo, setName("%s_trk" % upperCtlNames[i]), t
            )
            if i == 2:
                trackLvl.append(npo)
            else:
                track_corner_lvl.append(npo)

        if i in [1, 2, 3]:
            ctl = primitive.addTransform(
                npo, setName("%s_loc" % upperCtlNames[i]), t
            )
            # ghost controls
            if i == 2:
                gt = ut
            else:
                gt = t
            npo_g = primitive.addTransform(
                up_ctl, setName("%sCtl_npo" % upperCtlNames[i]), gt
            )
            ctl_g = icon.create(
                npo_g,
                setName("%s_%s" % (upperCtlNames[i], ctlName)),
                gt,
                icon=icon_shape,
                w=wd,
                d=wd,
                ro=datatypes.Vector(1.57079633, 0, 0),
                po=datatypes.Vector(0, 0, offset),
                color=color,
            )
            # define the ctl_param to recive the ctl configuration
            ctl_param = ctl_g
            ghost_ctl.append(ctl_g)
            # connect local SRT
            rigbits.connectLocalTransform([ctl_g, ctl])
        else:
            ctl = icon.create(
                npo,
                setName("%s_%s" % (upperCtlNames[i], ctlName)),
                t,
                icon=icon_shape,
                w=wd,
                d=wd,
                ro=datatypes.Vector(1.57079633, 0, 0),
                po=datatypes.Vector(0, 0, offset),
                color=color,
            )
            # define the ctl_param to recive the ctl configuration
            ctl_param = ctl
        attribute.addAttribute(ctl_param, "isCtl", "bool", keyable=False)
        attribute.add_mirror_config_channels(ctl_param)
        node.add_controller_tag(ctl_param, over_npo)
        if len(ctlName.split("_")) == 2 and ctlName.split("_")[-1] == "ghost":
            pass
        else:
            pm.sets(ctlSet, add=ctl_param)
        attribute.setKeyableAttributes(ctl_param, params)
        upControls.append(ctl)
        # add corner ctls to corner ctl list for tracking
        if i in [0, 4]:
            corner_ctl.append(ctl)
        if side == "R":
            npoBase.attr("ry").set(180)
            npoBase.attr("sz").set(-1)
    # adding parent constraints to odd controls
    for i, ctl in enumerate(upControls):
        if utils.is_odd(i):
            cns_node = pm.parentConstraint(
                upControls[i - 1], upControls[i + 1], ctl.getParent(), mo=True
            )
            # Make the constraint "noFlip"
            cns_node.interpType.set(0)

    # adding parent constraint ghost controls
    cns_node = pm.parentConstraint(
        ghost_ctl[1], upControls[0], ghost_ctl[0].getParent(), mo=True
    )
    cns_node.interpType.set(0)
    cns_node = pm.parentConstraint(
        ghost_ctl[1], upControls[-1], ghost_ctl[2].getParent(), mo=True
    )
    cns_node.interpType.set(0)

    # lower eyelid controls
    lowControls = [upControls[0]]
    lowerCtlNames = [
        "inCorner",
        "lowInMid",
        "lowMid",
        "lowOutMid",
        "outCorner",
    ]

    cvs = lowCtl_crv.getCVs(space="world")
    if side == "R" and not sideRange:
        cvs = [cv for cv in reversed(cvs)]
    for i, cv in enumerate(cvs):
        # we skip the first and last point since is already in the uper eyelid
        if i in [0, 4]:
            continue
        if utils.is_odd(i):
            color = 14
            wd = 0.3
            icon_shape = "circle"
            params = ["tx", "ty", "tz"]
        else:
            color = 4
            wd = 0.6
            icon_shape = "circle"
            params = [
                "tx",
                "ty",
                "tz",
                "ro",
                "rx",
                "ry",
                "rz",
                "sx",
                "sy",
                "sz",
            ]

        t = transform.setMatrixPosition(t, cvs[i])
        npo = primitive.addTransform(
            center_lookat, setName("%s_npo" % lowerCtlNames[i]), t
        )
        npoBase = npo
        if i in [1, 2, 3]:
            if i == 2:
                # we add an extra level to input the tracking ofset values
                npo = primitive.addTransform(
                    npo, setName("%s_trk" % lowerCtlNames[i]), t
                )
                trackLvl.append(npo)
            ctl = primitive.addTransform(
                npo, setName("%s_loc" % lowerCtlNames[i]), t
            )
            # ghost controls
            if i == 2:
                gt = lt
            else:
                gt = t
            # ghost controls
            npo_g = primitive.addTransform(
                low_ctl, setName("%sCtl_npo" % lowerCtlNames[i]), gt
            )
            ctl_g = icon.create(
                npo_g,
                setName("%s_%s" % (lowerCtlNames[i], ctlName)),
                gt,
                icon=icon_shape,
                w=wd,
                d=wd,
                ro=datatypes.Vector(1.57079633, 0, 0),
                po=datatypes.Vector(0, 0, offset),
                color=color,
            )
            # define the ctl_param to recive the ctl configuration
            ctl_param = ctl_g
            ghost_ctl.append(ctl_g)
            # connect local SRT
            rigbits.connectLocalTransform([ctl_g, ctl])
        else:
            ctl = icon.create(
                npo,
                setName("%s_%s" % (lowerCtlNames[i], ctlName)),
                t,
                icon=icon_shape,
                w=wd,
                d=wd,
                ro=datatypes.Vector(1.57079633, 0, 0),
                po=datatypes.Vector(0, 0, offset),
                color=color,
            )
            # define the ctl_param to recive the ctl configuration
            ctl_param = ctl
        attribute.addAttribute(ctl_param, "isCtl", "bool", keyable=False)
        attribute.add_mirror_config_channels(ctl_param)

        lowControls.append(ctl)
        if len(ctlName.split("_")) == 2 and ctlName.split("_")[-1] == "ghost":
            pass
        else:
            pm.sets(ctlSet, add=ctl_param)
        attribute.setKeyableAttributes(ctl_param, params)
        # mirror behaviout on R side controls
        if side == "R":
            npoBase.attr("ry").set(180)
            npoBase.attr("sz").set(-1)
    for lctl in reversed(lowControls[1:]):
        node.add_controller_tag(lctl, over_npo)
    lowControls.append(upControls[-1])

    # adding parent constraints to odd controls
    for i, ctl in enumerate(lowControls):
        if utils.is_odd(i):
            cns_node = pm.parentConstraint(
                lowControls[i - 1],
                lowControls[i + 1],
                ctl.getParent(),
                mo=True,
            )
            # Make the constraint "noFlip"
            cns_node.interpType.set(0)

    # adding parent constraint ghost controls
    cns_node = pm.parentConstraint(
        ghost_ctl[4], upControls[0], ghost_ctl[3].getParent(), mo=True
    )
    cns_node.interpType.set(0)
    cns_node = pm.parentConstraint(
        ghost_ctl[4], upControls[-1], ghost_ctl[5].getParent(), mo=True
    )
    cns_node.interpType.set(0)

    ##########################################
    # OPERATORS
    ##########################################
    # Connecting control crvs with controls
    applyop.gear_curvecns_op(upCtl_crv, upControls)
    applyop.gear_curvecns_op(lowCtl_crv, lowControls)

    # adding wires
    w1 = pm.wire(up_crv, w=upDriver_crv)[0]
    w2 = pm.wire(low_crv, w=lowDriver_crv)[0]

    w3 = pm.wire(upProfile_target_crv, w=upCtl_crv)[0]
    w4 = pm.wire(lowProfile_target_crv, w=lowCtl_crv)[0]

    if z_up:
        trigger_axis = "tz"
    else:
        trigger_axis = "ty"

    # connect blink driver
    pm.pointConstraint(low_ctl, blink_driver, mo=False)
    rest_val = blink_driver.attr(trigger_axis).get()

    up_div_node = node.createDivNode(up_ctl.attr(trigger_axis), rest_val)
    low_div_node = node.createDivNode(
        low_ctl.attr(trigger_axis), rest_val * -1
    )

    # contact driver
    minus_node = node.createPlusMinusAverage1D(
        [rest_val, blink_driver.attr(trigger_axis)], operation=2
    )
    contact_div_node = node.createDivNode(minus_node.output1D, rest_val)

    # wire tension
    for w in [w1, w2, w3, w4]:
        w.dropoffDistance[0].set(100)

    # TODO: what is the best solution?
    # trigger using proximity
    # remap_node = pm.createNode("remapValue")
    # contact_div_node.outputX >> remap_node.inputValue
    # remap_node.value[0].value_Interp.set(2)
    # remap_node.inputMin.set(0.995)
    # reverse_node = node.createReverseNode(remap_node.outColorR)
    # for w in [w1, w2]:
    #     reverse_node.outputX >> w.scale[0]

    # trigger at starting movement for up and low
    # up
    remap_node = pm.createNode("remapValue")
    up_ctl.attr(trigger_axis) >> remap_node.inputValue
    remap_node.value[0].value_Interp.set(2)
    remap_node.inputMax.set(rest_val / 8)
    reverse_node = node.createReverseNode(remap_node.outColorR)
    reverse_node.outputX >> w1.scale[0]
    # low
    remap_node = pm.createNode("remapValue")
    low_ctl.attr(trigger_axis) >> remap_node.inputValue
    remap_node.value[0].value_Interp.set(2)
    remap_node.inputMin.set((rest_val / 8) * -1)
    remap_node.outColorR >> w2.scale[0]

    # mid position drivers blendshapes
    bs_midUpDrive = pm.blendShape(
        lowRest_target_crv,
        upProfile_target_crv,
        midUpDriver_crv,
        n="midUpDriver_blendShape",
    )

    bs_midLowDrive = pm.blendShape(
        upRest_target_crv,
        lowProfile_target_crv,
        midLowDriver_crv,
        n="midlowDriver_blendShape",
    )

    bs_closeTarget = pm.blendShape(
        midUpDriver_crv,
        midLowDriver_crv,
        closeTarget_crv,
        n="closeTarget_blendShape",
    )

    pm.connectAttr(
        up_div_node.outputX,
        bs_midUpDrive[0].attr(lowRest_target_crv.name()),
    )

    pm.connectAttr(
        low_div_node.outputX,
        bs_midLowDrive[0].attr(upRest_target_crv.name()),
    )

    pm.setAttr(bs_closeTarget[0].attr(midUpDriver_crv.name()), 0.5)
    pm.setAttr(bs_closeTarget[0].attr(midLowDriver_crv.name()), 0.5)

    # Main crv drivers
    bs_upBlink = pm.blendShape(
        lowRest_target_crv,
        closeTarget_crv,
        upProfile_target_crv,
        upDriver_crv,
        n="upBlink_blendShape",
    )
    bs_lowBlink = pm.blendShape(
        upRest_target_crv,
        closeTarget_crv,
        lowProfile_target_crv,
        lowDriver_crv,
        n="lowBlink_blendShape",
    )

    # blink contact connections
    cond_node_up = node.createConditionNode(
        contact_div_node.outputX, 1, 3, 0, up_div_node.outputX
    )
    pm.connectAttr(
        cond_node_up.outColorR,
        bs_upBlink[0].attr(lowRest_target_crv.name()),
    )

    cond_node_low = node.createConditionNode(
        contact_div_node.outputX, 1, 3, 0, low_div_node.outputX
    )
    pm.connectAttr(
        cond_node_low.outColorR,
        bs_lowBlink[0].attr(upRest_target_crv.name()),
    )

    cond_node_close = node.createConditionNode(
        contact_div_node.outputX, 1, 2, 1, 0
    )
    cond_node_close.colorIfFalseR.set(0)
    pm.connectAttr(
        cond_node_close.outColorR,
        bs_upBlink[0].attr(closeTarget_crv.name()),
    )

    pm.connectAttr(
        cond_node_close.outColorR,
        bs_lowBlink[0].attr(closeTarget_crv.name()),
    )

    pm.setAttr(bs_upBlink[0].attr(upProfile_target_crv.name()), 1)
    pm.setAttr(bs_lowBlink[0].attr(lowProfile_target_crv.name()), 1)

    # joints root
    jnt_root = primitive.addTransformFromPos(
        eye_root, setName("joints"), pos=bboxCenter
    )
    if deformers_group:
        deformers_group = pm.PyNode(deformers_group)
        pm.parentConstraint(eye_root, jnt_root, mo=True)
        pm.scaleConstraint(eye_root, jnt_root, mo=True)
        deformers_group.addChild(jnt_root)

    # head joint
    if headJnt:
        try:
            headJnt = pm.PyNode(headJnt)
            jnt_base = headJnt
        except pm.MayaNodeError:
            pm.displayWarning("Aborted can not find %s " % headJnt)
            return
    else:
        # Eye root
        jnt_base = jnt_root

    eyeTargets_root = primitive.addTransform(eye_root, setName("targets"))

    eyeCenter_jnt = rigbits.addJnt(
        arrow_ctl, jnt_base, grp=defset, jntName=setName("center_jnt")
    )

    # Upper Eyelid joints ##################################################

    cvs = up_crv.getCVs(space="world")
    upCrv_info = node.createCurveInfoNode(up_crv)

    # aim constrain targets and joints
    upperEyelid_aimTargets = []
    upperEyelid_jnt = []
    upperEyelid_jntRoot = []

    if z_up:
        axis = "zy"
        wupVector = [0, 0, 1]
    else:
        axis = "-yz"
        wupVector = [0, 1, 0]

    for i, cv in enumerate(cvs):
        if i % everyNVertex:
            continue

        # aim targets
        trn = primitive.addTransformFromPos(
            eyeTargets_root, setName("upEyelid_aimTarget", i), pos=cv
        )
        upperEyelid_aimTargets.append(trn)
        # connecting positions with crv
        pm.connectAttr(
            upCrv_info + ".controlPoints[%s]" % str(i), trn.attr("translate")
        )

        # joints
        jntRoot = primitive.addJointFromPos(
            jnt_root, setName("upEyelid_jnt_base", i), pos=bboxCenter
        )
        jntRoot.attr("radius").set(0.08)
        jntRoot.attr("visibility").set(False)
        upperEyelid_jntRoot.append(jntRoot)
        applyop.aimCns(
            jntRoot, trn, axis=axis, wupObject=jnt_root, wupVector=wupVector
        )

        jnt_ref = primitive.addJointFromPos(
            jntRoot, setName("upEyelid_jnt_ref", i), pos=cv
        )
        jnt_ref.attr("radius").set(0.08)
        jnt_ref.attr("visibility").set(False)

        jnt = rigbits.addJnt(
            jnt_ref, jnt_base, grp=defset, jntName=setName("upEyelid_jnt", i)
        )
        upperEyelid_jnt.append(jnt)

    # Lower Eyelid joints ##################################################

    cvs = low_crv.getCVs(space="world")
    lowCrv_info = node.createCurveInfoNode(low_crv)

    # aim constrain targets and joints
    lowerEyelid_aimTargets = []
    lowerEyelid_jnt = []
    lowerEyelid_jntRoot = []

    for i, cv in enumerate(cvs):
        if i in [0, len(cvs) - 1]:
            continue

        if i % everyNVertex:
            continue

        # aim targets
        trn = primitive.addTransformFromPos(
            eyeTargets_root, setName("lowEyelid_aimTarget", i), pos=cv
        )
        lowerEyelid_aimTargets.append(trn)
        # connecting positions with crv
        pm.connectAttr(
            lowCrv_info + ".controlPoints[%s]" % str(i), trn.attr("translate")
        )

        # joints
        jntRoot = primitive.addJointFromPos(
            jnt_root, setName("lowEyelid_base", i), pos=bboxCenter
        )
        jntRoot.attr("radius").set(0.08)
        jntRoot.attr("visibility").set(False)
        lowerEyelid_jntRoot.append(jntRoot)
        applyop.aimCns(
            jntRoot, trn, axis=axis, wupObject=jnt_root, wupVector=wupVector
        )

        jnt_ref = primitive.addJointFromPos(
            jntRoot, setName("lowEyelid_jnt_ref", i), pos=cv
        )
        jnt_ref.attr("radius").set(0.08)
        jnt_ref.attr("visibility").set(False)

        jnt = rigbits.addJnt(
            jnt_ref, jnt_base, grp=defset, jntName=setName("lowEyelid_jnt", i)
        )
        lowerEyelid_jnt.append(jnt)

    # Adding channels for eye tracking
    upVTracking_att = attribute.addAttribute(
        up_ctl, "vTracking", "float", upperVTrack, minValue=0
    )
    upHTracking_att = attribute.addAttribute(
        up_ctl, "hTracking", "float", upperHTrack, minValue=0
    )

    lowVTracking_att = attribute.addAttribute(
        low_ctl, "vTracking", "float", lowerVTrack, minValue=0
    )
    lowHTracking_att = attribute.addAttribute(
        low_ctl, "hTracking", "float", lowerHTrack, minValue=0
    )

    # vertical tracking connect
    up_mult_node = node.createMulNode(
        upVTracking_att, aimTrigger_ref.attr("ty")
    )
    low_mult_node = node.createMulNode(
        lowVTracking_att, aimTrigger_ref.attr("ty")
    )
    # remap to use the low or the up eyelid as driver contact base on
    # the eyetrack trigger direction
    uT_remap_node = pm.createNode("remapValue")
    aimTrigger_ref.attr("ty") >> uT_remap_node.inputValue
    uT_remap_node.inputMax.set(0.1)
    uT_remap_node.inputMin.set(-0.1)
    up_mult_node.outputX >> uT_remap_node.outputMax
    low_mult_node.outputX >> uT_remap_node.outputMin
    # up
    u_remap_node = pm.createNode("remapValue")
    contact_div_node.outputX >> u_remap_node.inputValue
    u_remap_node.value[0].value_Interp.set(2)
    u_remap_node.inputMin.set(0.9)
    up_mult_node.outputX >> u_remap_node.outputMin
    uT_remap_node.outColorR >> u_remap_node.outputMax

    # low
    l_remap_node = pm.createNode("remapValue")
    contact_div_node.outputX >> l_remap_node.inputValue
    l_remap_node.value[0].value_Interp.set(2)
    l_remap_node.inputMin.set(0.9)
    low_mult_node.outputX >> l_remap_node.outputMin
    uT_remap_node.outColorR >> l_remap_node.outputMax

    # up connect and turn down to low when contact
    pm.connectAttr(u_remap_node.outColorR, trackLvl[0].attr("ty"))

    pm.connectAttr(l_remap_node.outColorR, trackLvl[1].attr("ty"))

    # horizontal tracking connect
    mult_node = node.createMulNode(upHTracking_att, aimTrigger_ref.attr("tx"))
    # Correct right side horizontal tracking
    if side == "R":
        mult_node = node.createMulNode(mult_node.attr("outputX"), -1)
    pm.connectAttr(mult_node + ".outputX", trackLvl[0].attr("tx"))

    mult_node = node.createMulNode(lowHTracking_att, aimTrigger_ref.attr("tx"))
    # Correct right side horizontal tracking
    if side == "R":
        mult_node = node.createMulNode(mult_node.attr("outputX"), -1)
    pm.connectAttr(mult_node + ".outputX", trackLvl[1].attr("tx"))

    # adding channels for corner tracking
    # track_corner_lvl
    for i, ctl in enumerate(corner_ctl):
        VTracking_att = attribute.addAttribute(
            ctl, "vTracking", "float", 0.1, minValue=0
        )
        mult_node = node.createMulNode(VTracking_att, up_ctl.ty)
        mult_node2 = node.createMulNode(VTracking_att, low_ctl.ty)
        plus_node = node.createPlusMinusAverage1D(
            [mult_node.outputX, mult_node2.outputX]
        )
        pm.connectAttr(plus_node.output1D, track_corner_lvl[i].attr("ty"))

    ###########################################
    # Reparenting
    ###########################################
    if parent_node:
        try:
            if isinstance(parent_node, string_types):
                parent_node = pm.PyNode(parent_node)
            parent_node.addChild(eye_root)
        except pm.MayaNodeError:
            pm.displayWarning(
                "The eye rig can not be parent to: %s. Maybe "
                "this object doesn't exist." % parent_node
            )

    ###########################################
    # Auto Skinning
    ###########################################
    if doSkin:
        # eyelid vertex rows
        totalLoops = rigidLoops + falloffLoops
        vertexLoopList = meshNavigation.getConcentricVertexLoop(
            vertexList, totalLoops
        )
        vertexRowList = meshNavigation.getVertexRowsFromLoops(vertexLoopList)

        # we set the first value 100% for the first initial loop
        skinPercList = [1.0]
        # we expect to have a regular grid topology
        for r in range(rigidLoops):
            for rr in range(2):
                skinPercList.append(1.0)
        increment = 1.0 / float(falloffLoops)
        # we invert to smooth out from 100 to 0
        inv = 1.0 - increment
        for r in range(falloffLoops):
            for rr in range(2):
                if inv < 0.0:
                    inv = 0.0
                skinPercList.append(inv)
            inv -= increment

        # this loop add an extra 0.0 indices to avoid errors
        for r in range(10):
            for rr in range(2):
                skinPercList.append(0.0)

        # base skin
        geo = pm.listRelatives(edgeLoopList[0], parent=True)[0]
        # Check if the object has a skinCluster
        objName = pm.listRelatives(geo, parent=True)[0]

        skinCluster = skin.getSkinCluster(objName)
        if not skinCluster:
            skinCluster = pm.skinCluster(
                headJnt, geo, tsb=True, nw=2, n="skinClsEyelid"
            )

        eyelidJoints = upperEyelid_jnt + lowerEyelid_jnt
        pm.progressWindow(
            title="Auto skinning process", progress=0, max=len(eyelidJoints)
        )
        firstBoundary = False
        for jnt in eyelidJoints:
            pm.progressWindow(e=True, step=1, status="\nSkinning %s" % jnt)
            skinCluster.addInfluence(jnt, weight=0)
            v = meshNavigation.getClosestVertexFromTransform(geo, jnt)

            for row in vertexRowList:

                if v in row:
                    it = 0  # iterator
                    inc = 1  # increment
                    for i, rv in enumerate(row):
                        try:
                            perc = skinPercList[it]
                            t_val = [(jnt, perc), (headJnt, 1.0 - perc)]
                            pm.skinPercent(
                                skinCluster, rv, transformValue=t_val
                            )
                            if rv.isOnBoundary():
                                # we need to compare with the first boundary
                                # to check if the row have inverted direction
                                # and offset the value
                                if not firstBoundary:
                                    firstBoundary = True
                                    firstBoundaryValue = it

                                else:
                                    if it < firstBoundaryValue:
                                        it -= 1
                                    elif it > firstBoundaryValue:
                                        it += 1
                                inc = 2
                        except IndexError:
                            continue

                        it = it + inc
        pm.progressWindow(e=True, endProgress=True)

        # Eye Mesh skinning
        skinCluster = skin.getSkinCluster(eyeMesh)
        if not skinCluster:
            skinCluster = pm.skinCluster(
                eyeCenter_jnt, eyeMesh, tsb=True, nw=1, n="skinClsEye"
            )


##########################################################
# Helper Functions
##########################################################


# Getters


def get_edge_loop(edgeLoop):
    if edgeLoop:
        edgeLoopList = [pm.PyNode(e) for e in edgeLoop.split(",")]
        return edgeLoopList
    else:
        pm.displayWarning("Please set the edge loop first")
        return


def get_eye_mesh(eyeMesh):
    if eyeMesh:
        try:
            eyeMesh = pm.PyNode(eyeMesh)
            return eyeMesh
        except pm.MayaNodeError:
            pm.displayWarning(
                "The object %s can not be found in the " "scene" % (eyeMesh)
            )
            return
    else:
        pm.displayWarning("Please set the eye mesh first")


# Build from json file.
def rig_from_file(path):
    rig(**json.load(open(path)))
