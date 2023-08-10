import os
import sys
import json
import ctypes
import ctypes.wintypes
import traceback
import subprocess
from collections import OrderedDict

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from mgear.vendor.Qt import QtWidgets
from mgear.vendor.Qt import QtCore

from mgear.core import string, pyqt, pyFBX as pfbx
from mgear.shifter.game_tools_fbx import game_tools_fbx_sdk_utils, fbx_export_node

NO_EXPORT_TAG = "no_export"
WORLD_CONTROL_NAME = "world_ctl"

FRAMES_PER_SECOND = {
    "24 FPS": ("film", 24),
    "30 FPS": ("ntsc", 30),
    "60 FPS": ("ntscf", 60),
    "120 FPS": ("120fps", 120),
}
AS_FRAMES = dict(FRAMES_PER_SECOND.values())
TRANSFORM_ATTRIBUTES = [
    "tx",
    "ty",
    "tz",
    "rx",
    "ry",
    "rz",
    "sx",
    "sy",
    "sz",
    "visibility",
]


class SelectorDialog(QtWidgets.QDialog):
    def __init__(
        self, items=[], title="Selector Dialog", parent=pyqt.maya_main_window()
    ):
        super(SelectorDialog, self).__init__(parent)
        self.title = title
        self.items = items
        self.item = None

        self.setWindowTitle(self.title)
        self.setWindowFlags(
            self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
        )

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.list_wgt = QtWidgets.QListWidget()
        for item in self.items:
            self.list_wgt.addItem(item.name())

        self.ok_btn = QtWidgets.QPushButton("OK")

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.list_wgt)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.list_wgt.itemClicked.connect(self.get_item)
        self.list_wgt.itemDoubleClicked.connect(self.accept)

        self.ok_btn.clicked.connect(self.accept)

    def get_item(self, item):
        self.item = item.text()


def export_skeletal_mesh(jnt_roots, geo_roots, **export_data):

    file_path = export_data.get("file_path", "")
    file_name = export_data.get("file_name", "")
    preset_path = export_data.get("preset_path", None)
    up_axis = export_data.get("up_axis", None)
    file_type = export_data.get("file_type", "binary").lower()
    fbx_version = export_data.get("fbx_version", None)
    remove_namespaces = export_data.get("remove_namespace")
    scene_clean = export_data.get("scene_clean", True)
    deformations = export_data.get("deformations", True)
    skinning = export_data.get("skinning", True)
    blendshapes = export_data.get("blendshapes", True)
    use_partitions = export_data.get("use_partitions", True)
    partitions = export_data.get("partitions", None)

    if not file_name.endswith(".fbx"):
        file_name = "{}.fbx".format(file_name)
    path = string.normalize_path(os.path.join(file_path, file_name))
    print("\t>>> Export Path: {}".format(path))

    # export settings config
    pfbx.FBXResetExport()

    # set configuration
    if preset_path is not None:
        # load FBX export preset file
        pfbx.FBXLoadExportPresetFile(f=preset_path)
    pfbx.FBXExportSkins(v=skinning)
    pfbx.FBXExportShapes(v=blendshapes)
    fbx_version_str = None
    if up_axis is not None:
        pfbx.FBXExportUpAxis(up_axis)
    if fbx_version is not None:
        fbx_version_str = "{}00".format(
            fbx_version.split("/")[0].replace(" ", "")
        )
        pfbx.FBXExportFileVersion(v=fbx_version_str)
    if file_type == "ascii":
        pfbx.FBXExportInAscii(v=True)

    # select elements and export all the data
    pm.select(jnt_roots + geo_roots)

    fbx_modified = False
    pfbx.FBXExport(f=path, s=True)
    fbx_file = game_tools_fbx_sdk_utils.FbxSdkGameToolsWrapper(path)

    # Make sure root joints are parented to world
    for jnt_root in jnt_roots:
        fbx_file.parent_to_world(jnt_root, remove_top_parent=False)
    if geo_roots:
        for geo_root in geo_roots:
            meshes = (
                cmds.listRelatives(geo_root, children=True, type="transform")
                or list()
            )
            if geo_root == geo_roots[-1]:
                for mesh in meshes:
                    # if we are in the last geo root and in the last mesh, we parent the last mesh to the world
                    # and we remove the parent hierarchy of nodes
                    # TODO: This is a bit hacky, find a better implementation
                    # TODO: Ideally we should find the root node before reparenting joints and meshes and just
                    # TODO: delete that node once the root joints and meshes are parented to the world
                    if mesh == meshes[-1]:
                        fbx_file.parent_to_world(mesh, remove_top_parent=True)
                    else:
                        fbx_file.parent_to_world(mesh, remove_top_parent=False)
            else:
                for mesh in meshes:
                    fbx_file.parent_to_world(mesh, remove_top_parent=False)

    if remove_namespaces:
        fbx_file.remove_namespaces()
        fbx_modified = True
    if scene_clean:
        fbx_file.clean_scene(
            no_export_tag=NO_EXPORT_TAG, world_control_name=WORLD_CONTROL_NAME
        )
        fbx_modified = True
    if fbx_modified:
        fbx_file.save(
            mode=file_type,
            file_version=fbx_version_str,
            close=True,
            preset_path=preset_path,
            skins=skinning,
            blendshapes=blendshapes,
        )

    # post process with FBX SDK if available
    if pfbx.FBX_SDK:
        if use_partitions:
            export_skeletal_mesh_partitions(jnt_roots=jnt_roots, **export_data)

            # when using partitions, we remove full FBX file
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError:
                    cmds.warning(
                        'Was not possible to remove temporal FBX file "{}"'.format(
                            path
                        )
                    )

    return True


def export_skeletal_mesh_partitions(jnt_roots, **export_data):

    if not pfbx.FBX_SDK:
        cmds.warning(
            "Python FBX SDK is not available. Skeletal Mesh partitions export functionality is not available!"
        )
        return False

    file_path = export_data.get("file_path", "")
    file_name = export_data.get("file_name", "")
    deformations = export_data.get("deformations", True)
    skinning = export_data.get("skinning", True)
    blendshapes = export_data.get("blendshapes", True)

    if not file_name.endswith(".fbx"):
        file_name = "{}.fbx".format(file_name)
    path = string.normalize_path(os.path.join(file_path, file_name))
    print("\t>>> Export Path: {}".format(path))

    partitions = export_data.get("partitions", dict())
    if not partitions:
        cmds.warning("Partitions not defined!")
        return False

    # data that will be exported into a temporal file
    partitions_data = OrderedDict()

    for partition_name, meshes in partitions.items():

        joint_hierarchy = OrderedDict()
        for mesh in meshes:

            # we retrieve all end joints from the influenced joints
            influences = pm.skinCluster(mesh, query=True, influence=True)

            # make sure the hierarchy from the root joint to the influence joints is retrieved.
            for jnt_root in jnt_roots:
                joint_hierarchy.setdefault(jnt_root, list())
                for inf_jnt in influences:
                    jnt_hierarchy = get_joint_list(jnt_root, inf_jnt)
                    for hierarchy_jnt in jnt_hierarchy:
                        if hierarchy_jnt not in joint_hierarchy[jnt_root]:
                            joint_hierarchy[jnt_root].append(hierarchy_jnt)

        partitions_data.setdefault(partition_name, dict())

        # the joint chain to export will be the shorter one between the root joint and the influences
        short_hierarchy = None
        for root_jnt, joint_hierarchy in joint_hierarchy.items():
            total_joints = len(joint_hierarchy)
            if total_joints <= 0:
                continue
            if short_hierarchy is None:
                short_hierarchy = joint_hierarchy
                partitions_data[partition_name]["root"] = root_jnt
            elif len(short_hierarchy) > len(joint_hierarchy):
                short_hierarchy = joint_hierarchy
                partitions_data[partition_name]["root"] = root_jnt
        if short_hierarchy is None:
            continue

        # we make sure we update the hierarchy to include all joints between the skeleton root joint and
        # the first joint of the found joint hierarchy
        root_jnt = get_root_joint(short_hierarchy[0])
        if root_jnt not in short_hierarchy:
            parent_hierarchy = get_joint_list(root_jnt, short_hierarchy[0])
            short_hierarchy = parent_hierarchy + short_hierarchy

        partitions_data[partition_name]["hierarchy"] = [
            jnt.name() for jnt in short_hierarchy
        ]

    try:
        for partition_name, partition_data in partitions_data.items():
            fbx_file = game_tools_fbx_sdk_utils.FbxSdkGameToolsWrapper(path)
            partition_meshes = partitions.get(partition_name)
            fbx_file.export_skeletal_mesh(
                file_name=partition_name,
                mesh_names=partition_meshes,
                hierarchy_joints=partition_data["hierarchy"],
                deformations=deformations,
                skins=skinning,
                blendshapes=blendshapes,
            )
            fbx_file.close()
    except Exception:
        cmds.error(
            "Something wrong happened while export skeleton mesh: {}".format(
                traceback.format_exc()
            )
        )
        return False

    return True


def export_animation_clip(root_joint, **export_data):

    if not root_joint or not cmds.objExists(root_joint):
        cmds.warning(
            'Was not possible to export animation clip because root joint "{}" was not found within scene'.format(
                root_joint
            )
        )
        return False

    # only enabled animation clips will be exported
    enabled = export_data.get("enabled", False)
    if not enabled:
        return False

    # namespace = pm.PyNode(root_joint).namespace()
    # if not namespace:
    # 	cmds.warning('Only animations with namespaces can be exported')
    # 	return False
    # namespace = namespace[:-1]

    time_range = cmds.playbackOptions(
        query=True, minTime=True
    ), cmds.playbackOptions(query=True, maxTime=True)
    start_frame = export_data.get("startFrame", time_range[0])
    end_frame = export_data.get("endFrame", time_range[1])
    if start_frame > end_frame:
        cmds.error(
            "Start frame {} must be lower than the end frame {}".format(
                start_frame, end_frame
            )
        )
        return False

    title = export_data.get("title", "")
    file_path = export_data.get("file_path", "")
    file_name = export_data.get("file_name", "")
    preset_path = export_data.get("preset_path", None)
    up_axis = export_data.get("up_axis", None)
    file_type = export_data.get("file_type", "binary").lower()
    fbx_version = export_data.get("fbx_version", None)
    remove_namespaces = export_data.get("remove_namespace")
    scene_clean = export_data.get("scene_clean", True)
    frame_rate = export_data.get("frameRate", "30 FPS")
    anim_layer = export_data.get("animLayer", "")

    if not file_path or not file_name:
        cmds.warning(
            "No valid file path or file name given for the FBX to export!"
        )
        return False
    if title:
        file_name = "{}_{}".format(file_name, title)
    if not file_name.endswith(".fbx"):
        file_name = "{}.fbx".format(file_name)
    path = string.normalize_path(os.path.join(file_path, file_name))
    print("\t>>> Export Path: {}".format(path))

    original_selection = pm.ls(sl=True)
    auto_key_state = pm.autoKeyframe(query=True, state=True)
    cycle_check = pm.cycleCheck(query=True, evaluation=True)
    scene_modified = cmds.file(query=True, modified=True)
    current_frame_range = cmds.currentUnit(query=True, time=True)
    current_frame = cmds.currentTime(query=True)
    original_start_frame = int(pm.playbackOptions(min=True, query=True))
    original_end_frame = int(pm.playbackOptions(max=True, query=True))
    temp_mesh = None
    temp_skin_cluster = None
    original_anim_layer_weights = None

    try:
        # set anim layer to enable
        if (
            anim_layer
            and cmds.objExists(anim_layer)
            and cmds.nodeType(anim_layer) == "animLayer"
        ):
            to_activate = None
            to_deactivate = []
            anim_layers = all_anim_layers_ordered(include_base_animation=False)
            original_anim_layer_weights = {
                anim_layer: cmds.animLayer(anim_layer, query=True, weight=True)
                for anim_layer in anim_layers
            }
            for found_anim_layer in anim_layers:
                if found_anim_layer != anim_layer:
                    to_deactivate.append(found_anim_layer)
                else:
                    to_activate = found_anim_layer
            for anim_layer_to_deactivate in to_deactivate:
                cmds.animLayer(anim_layer_to_deactivate, edit=True, weight=0.0)
            cmds.animLayer(to_activate, edit=True, weight=1.0)

        # disable viewport
        mel.eval("paneLayout -e -manage false $gMainPane")

        pfbx.FBXResetExport()

        # set configuration
        if preset_path is not None:
            # load FBX export preset file
            pfbx.FBXLoadExportPresetFile(f=preset_path)
        pfbx.FBXExportSkins(v=False)
        pfbx.FBXExportShapes(v=False)
        fbx_version_str = None
        if up_axis is not None:
            pfbx.FBXExportUpAxis(up_axis)
        if fbx_version is not None:
            fbx_version_str = "{}00".format(
                fbx_version.split("/")[0].replace(" ", "")
            )
            pfbx.FBXExportFileVersion(v=fbx_version_str)
        if file_type == "ascii":
            pfbx.FBXExportInAscii(v=True)

        # # create temporal triangle to skin
        # temp_mesh = cmds.polyCreateFacet(point=[(-0, 0, 0), (0, 0, 0), (0, 0, 0)], name='mgear_temp_mesh')[0]
        # temp_skin_cluster = cmds.skinCluster(
        #     [root_joint], temp_mesh, toSelectedBones=False, maximumInfluences=1, skinMethod=0)[0]

        # select elements to export
        pm.select([root_joint])

        # Set frame range
        cmds.currentTime(start_frame)
        old_frame_rate = AS_FRAMES[cmds.currentUnit(query=True, time=True)]
        new_frame_rate = FRAMES_PER_SECOND[frame_rate][1]
        # only set if frame rate changed
        mult_rate = new_frame_rate / old_frame_rate
        if mult_rate != 1:
            old_range = start_frame, end_frame
            start_frame = old_range[0] * mult_rate
            end_frame = old_range[1] * mult_rate
            cmds.currentUnit(time=FRAMES_PER_SECOND[frame_rate][0])

        pm.autoKeyframe(state=False)
        pfbx.FBXExportAnimationOnly(v=False)
        pfbx.FBXExportBakeComplexAnimation(v=True)
        pfbx.FBXExportBakeComplexStart(v=start_frame)
        pfbx.FBXExportBakeComplexEnd(v=end_frame)
        pfbx.FBXExportCameras(v=True)
        pfbx.FBXExportConstraints(v=True)
        pfbx.FBXExportLights(v=True)
        pfbx.FBXExportQuaternion(v="quaternion")
        pfbx.FBXExportAxisConversionMethod("none")
        pfbx.FBXExportApplyConstantKeyReducer(v=False)
        pfbx.FBXExportSmoothMesh(v=False)
        pfbx.FBXExportShapes(v=True)
        pfbx.FBXExportSkins(v=True)
        pfbx.FBXExportSkeletonDefinitions(v=True)
        pfbx.FBXExportEmbeddedTextures(v=False)
        pfbx.FBXExportInputConnections(v=True)
        pfbx.FBXExportInstances(v=True)
        pfbx.FBXExportUseSceneName(v=True)
        pfbx.FBXExportSplitAnimationIntoTakes(c=True)
        pfbx.FBXExportGenerateLog(v=False)
        pfbx.FBXExport(f=path, s=True)

        fbx_modified = False
        fbx_file = game_tools_fbx_sdk_utils.FbxSdkGameToolsWrapper(path)
        fbx_file.parent_to_world(root_joint, remove_top_parent=True)
        if remove_namespaces:
            fbx_file.remove_namespaces()
            fbx_modified = True
        if scene_clean:
            fbx_file.clean_scene(
                no_export_tag=NO_EXPORT_TAG,
                world_control_name=WORLD_CONTROL_NAME,
            )
            fbx_modified = True
        if fbx_modified:
            fbx_file.save(
                mode=file_type,
                file_version=fbx_version_str,
                close=True,
                preset_path=preset_path,
                skins=True,
            )

    except Exception as exc:
        raise exc
    finally:

        # setup again original anim layer weights
        if anim_layer and original_anim_layer_weights:
            for name, weight in original_anim_layer_weights.items():
                cmds.animLayer(name, edit=True, weight=weight)

        if temp_skin_cluster and cmds.objExists(temp_skin_cluster):
            cmds.delete(temp_skin_cluster)
        if temp_mesh and cmds.objExists(temp_mesh):
            cmds.delete(temp_mesh)

        cmds.currentTime(current_frame)
        cmds.currentUnit(time=current_frame_range)

        pm.autoKeyframe(state=auto_key_state)
        pm.cycleCheck(evaluation=cycle_check)
        cmds.playbackOptions(min=original_start_frame, max=original_end_frame)

        if original_selection:
            pm.select(original_selection)

        # if the scene was not modified before doing our changes, we force it back now
        if scene_modified is False:
            cmds.file(modified=False)

        # enable viewport
        mel.eval("paneLayout -e -manage true $gMainPane")

    return True


def create_mgear_playblast(
    file_name="", folder=None, start_frame=None, end_frame=None, scale=75
):

    file_name = file_name or "playblast"
    file_name = os.path.splitext(os.path.basename(file_name))[0]
    file_name = "{}.avi".format(file_name)
    time_range = cmds.playbackOptions(
        query=True, minTime=True
    ), cmds.playbackOptions(query=True, maxTime=True)
    start_frame = start_frame if start_frame is not None else time_range[0]
    end_frame = end_frame if end_frame is not None else time_range[1]
    if end_frame <= start_frame:
        end_frame = start_frame + 1

    if not folder or not os.path.isdir(folder):
        folder = get_mgear_playblasts_folder()
        if not os.path.isdir(folder):
            os.makedirs(folder)
    if not os.path.isdir(folder):
        cmds.warning(
            'Was not possible to create mgear playblasts folder: "{}"'.format(
                folder
            )
        )
        return False
    full_path = os.path.join(folder, file_name)
    count = 1
    while os.path.isfile(full_path):
        _file_name = "{}_{}{}".format(
            os.path.splitext(file_name)[0],
            count,
            os.path.splitext(file_name)[1],
        )
        full_path = os.path.join(folder, _file_name)
        count += 1

    cmds.playbackOptions(
        animationStartTime=start_frame,
        minTime=start_frame,
        animationEndTime=end_frame,
        maxTime=end_frame,
    )
    cmds.currentTime(start_frame, edit=True)
    cmds.playblast(p=scale, filename=full_path, forceOverwrite=True)

    return True


def get_mgear_playblasts_folder():

    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
    )
    documents_folder = os.path.abspath(buf.value)
    playblasts_folder = os.path.join(documents_folder, "mgear_playblasts")

    return playblasts_folder


def open_mgear_playblast_folder():
    folder = get_mgear_playblasts_folder()
    if not folder or not os.path.isdir(folder):
        cmds.warning(
            'Was not possible to open mgear playblasts folder: "{}"'.format(
                folder
            )
        )
        return False

    if sys.platform.startswith("darwin"):
        subprocess.Popen(["open", folder])
    elif os.name == "nt":
        os.startfile(folder)
    elif os.name == "posix":
        subprocess.Popen(["xdg-open", folder])
    else:
        cmds.error("OS not supported: {}".format(os.name))

    return True


def get_geo_grp():
    """Return the geometry group (objectSet in Maya) of the rig.
    If more than one xxx_geo_grp is available will pop up a selection list

    Returns:
            PyNode: objectSet
    """
    geo_grp = None
    geo_groups = pm.ls("*:*_geo_grp", "*_geo_grp", type="objectSet")
    if geo_groups:
        if len(geo_groups) > 1:
            item = select_item(geo_groups, "Select Geo Group")
            if item:
                geo_grp = pm.PyNode(item)
        else:
            geo_grp = geo_groups[0]
    return geo_grp


def get_geo_root():
    geo_grp = get_geo_grp()
    if geo_grp:
        memb = geo_grp.members()
        if memb:
            return memb
        else:
            pm.displayWarning("Geo_grp is empty. Please set geo root manually")
    else:
        pm.displayWarning(
            "Not Geo_grp available, please set geo roots manually"
        )


def get_joint_org():
    jnt_org = None
    joint_orgs = pm.ls("*:jnt_org", "*jnt_org", type="transform")
    if joint_orgs:
        if len(joint_orgs) > 1:
            item = select_item(joint_orgs, "Select Joint Org Node")
            if item:
                jnt_org = pm.PyNode(item)
        else:
            jnt_org = joint_orgs[0]
    return jnt_org


def get_joint_root():
    jnt_org = get_joint_org()
    if jnt_org:
        return jnt_org.getChildren()
    else:
        pm.displayWarning(
            "Not Joint found under jnt_org, please set joint roots manually"
        )


def select_item(items, title):
    """Create modal dialog to select item from list and return the selected tiem

    Args:
            items (list): List of str items
            title (str): Tittle for the modoal dialo

    Returns:
            str: selected item
    """
    item = None
    select_dialog = SelectorDialog(items, title)

    result = select_dialog.exec_()

    if result == QtWidgets.QDialog.Accepted:
        item = select_dialog.item

    return item


def get_root_joint(start_joint):
    """
    Recursively traverses up the hierarchy until finding the first object that does not have a parent.

    :param str node_name: node name to get root of.
    :param str node_type: node type for the root node.
    :return: found root node.
    :rtype: str
    """

    parent = pm.listRelatives(start_joint, parent=True, type="joint")
    parent = parent[0] if parent else None

    return get_root_joint(parent) if parent else start_joint


def get_joint_list(start_joint, end_joint):
    """Returns a list of joints between and including given start and end joint

    Args:
            start_joint str: start joint of joint list
            end_joint str end joint of joint list

    Returns:
            list[str]: joint list
    """

    if start_joint == end_joint:
        return [start_joint]

    # check hierarchy
    descendant_list = pm.ls(
        pm.listRelatives(start_joint, ad=True, fullPath=True),
        long=True,
        type="joint",
    )
    if not descendant_list.count(end_joint):
        # raise Exception('End joint "{}" is not a descendant of start joint "{}"'.format(end_joint, start_joint))
        return list()

    joint_list = [end_joint]
    while joint_list[-1] != start_joint:
        parent_jnt = pm.listRelatives(
            joint_list[-1], p=True, pa=True, fullPath=True
        )
        if not parent_jnt:
            raise Exception(
                'Found root joint while searching for start joint "{}"'.format(
                    start_joint
                )
            )
        joint_list.append(parent_jnt[0])

    joint_list.reverse()

    return joint_list


def get_end_joint(start_joint):

    end_joint = None
    next_joint = start_joint
    while next_joint:
        child_list = (
            pm.listRelatives(next_joint, fullPath=True, c=True) or list()
        )
        child_joints = pm.ls(child_list, long=True, type="joint") or list()
        if child_joints:
            next_joint = child_joints[0]
        else:
            end_joint = next_joint
            next_joint = None

    return end_joint


def all_anim_layers_ordered(include_base_animation=True):
    """Recursive function that returns all available animation layers within current scene.

    Returns:
            list[str]: list of animation layers.
    """

    def _add_node_recursive(layer_node):
        all_layers.append(layer_node)
        child_layers = (
            cmds.animLayer(layer_node, query=True, children=True) or list()
        )
        for child_layer in child_layers:
            _add_node_recursive(child_layer)

    all_layers = list()
    root_layer = cmds.animLayer(query=True, root=True)
    if not root_layer:
        return all_layers
    _add_node_recursive(root_layer)

    if not include_base_animation:
        if "BaseAnimation" in all_layers:
            all_layers.remove("BaseAnimation")

    return all_layers


if __name__ == "__main__":

    if sys.version_info[0] == 2:
        reload(pfbx)
    else:
        import importlib
        importlib.reload(pfbx)

    # export_skeletal_mesh(
    #     "Root", "geo_root", r"C:\Users/Miquel/Desktop/testing_auto2.fbx"
    # )

    grp = get_joint_root()
    print(grp)
