#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains all commands available for ueGear
"""

from __future__ import print_function, division, absolute_import

import os
import tempfile
import traceback

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import pymel.core as pm

from mgear.vendor.Qt import QtWidgets
from mgear.core import pyFBX
from mgear.core import utils as mgUtils
from mgear.uegear import log, utils, tag, bridge, io, ioutils

# DEBUGGING
import importlib
importlib.reload(mgUtils)

logger = log.uegear_logger


def content_project_directory():
    """
    Returns the current Unreal Engine project root directory.

    :return: Unreal Engine project root directory.
    :rtype: str
    """

    uegear_bridge = bridge.UeGearBridge()

    return uegear_bridge.execute("project_content_directory").get(
        "ReturnValue", ""
    )


def import_selected_assets_from_unreal():
    """
    Imports current selected Content Browser Unreal assets into the Maya scene.

    :return: True if import selected assets from Unreal operation was successful; False otherwise.
    :rtype: bool
    """

    uegear_bridge = bridge.UeGearBridge()

    # export FBX file into a temporal folder
    temp_folder = tempfile.gettempdir()
    asset_export_datas = uegear_bridge.execute(
        "export_selected_assets", parameters={"directory": temp_folder}
    ).get("ReturnValue", list())

    if not asset_export_datas:
        logger.warning(
            "Was not possible to export selected assets from Unreal"
        )
        return False

    for asset_export_data in asset_export_datas:
        # import asset from FBX file
        fbx_file = asset_export_data.get("fbx_file", None)
        if not fbx_file or not os.path.isfile(fbx_file):
            logger.warning(
                "No FBX file found for asset data: {}".format(
                    asset_export_data
                )
            )
            continue
        logger.info('Importing Asset from FBX file: "{}"'.format(fbx_file))
        imported_nodes = utils.import_fbx(fbx_file)

        # tag imported transform nodes from FBX
        transform_nodes = cmds.ls(imported_nodes, type="transform")
        for transform_node in transform_nodes:
            asset_type = asset_export_data.get("asset_type", "")
            asset_name = asset_export_data.get("name", "")
            asset_path = asset_export_data.get("path", "")
            if asset_type:
                tag.apply_tag(
                    transform_node, tag.TAG_ASSET_TYPE_ATTR_NAME, asset_type
                )
            else:
                tag.auto_tag(transform_node)
            if asset_name:
                tag.apply_tag(
                    transform_node, tag.TAG_ASSET_NAME_ATTR_NAME, asset_name
                )
            if asset_path:
                tag.apply_tag(
                    transform_node, tag.TAG_ASSET_PATH_ATTR_NAME, asset_path
                )

    return True


def export_selected_assets_to_unreal(
    export_directory=None, export_in_original_path=True
):
    """
    Exports current selected assets in Maya scene into Unreal Engine Content Browser.

    :return: True if export selected assets to Unreal operation was successful; False otherwise.
    :rtype: bool
    """

    # TODO: For now, only static meshes are exported into Unreal
    # TODO: Add support for Skeletal Meshes (Skinned Meshes)

    uegear_bridge = bridge.UeGearBridge()

    temp_folder = tempfile.gettempdir()

    # retrieve a dictionary with the assets that can be exported.
    nodes_to_export = cmds.ls(sl=True, long=True)
    objects_map = io.exportable_assets(nodes=nodes_to_export)
    if not objects_map:
        logger.warning(
            'No exportable assets found in nodes to export: "{}". Make sure assets are tagged.'.format(
                nodes_to_export
            )
        )
        return False

    # retrieve the static meshes nodes to export as assets into Unreal Engine
    static_meshes = objects_map.get(tag.TagTypes.StaticMesh, list())
    if not static_meshes:
        logger.warning("No static meshes to update")
        return False

    # Retrieve current Unreal Engine project directory
    content_path = uegear_bridge.execute("project_content_directory").get(
        "ReturnValue", ""
    )
    if not content_path or not os.path.isdir(content_path):
        logger.warning(
            "Was not possible to retrieve current Unreal project content path"
        )
        return False

    import_path_for_new_assets = ""

    for static_mesh in static_meshes:
        asset_path = tag.tag_values(
            tag_name=tag.TAG_ASSET_PATH_ATTR_NAME, nodes=[static_mesh]
        )
        asset_path = asset_path[0] if asset_path else ""
        asset_exists = uegear_bridge.execute(
            "does_asset_exist", parameters={"asset_path": asset_path}
        ).get("ReturnValue", False)

        if not asset_exists:
            asset_file_name = static_mesh.split("|")[-1]
            logger.info(
                'Asset "{}" does not exists within current Unreal Project! New asset will be created...'.format(
                    asset_file_name
                )
            )

            export_file_name = "{}.fbx".format(asset_file_name)

            if not export_directory:
                asset_export_path = utils.join_path(
                    temp_folder, export_file_name
                )
            else:
                asset_export_path = utils.join_path(
                    export_directory, export_file_name
                )

            if export_directory:
                asset_export_directory = os.path.dirname(asset_export_path)
                if not os.path.isdir(asset_export_directory):
                    logger.info(
                        "Export directory does not exist, trying to create it: {}".format(
                            asset_export_directory
                        )
                    )
                    result = utils.create_folder(asset_export_directory)
                    if not result:
                        logger.warning(
                            'Was not possible to create original export path: "{}" | temp folder will be used instead...'.format(
                                asset_export_directory
                            )
                        )
                        asset_export_path = utils.join_path(
                            temp_folder, "{}.fbx".format(asset_file_name)
                        )
            asset_export_directory = os.path.dirname(asset_export_path)

            # export FBX file into disk
            fbx_file_path = ioutils.export_static_mesh(
                asset_export_directory, static_mesh, file_name=export_file_name
            )
            if not os.path.isfile(fbx_file_path):
                logger.warning(
                    'Something went wrong while exporting asset FBX file: "{}"'.format(
                        fbx_file_path
                    )
                )
                continue

            if not import_path_for_new_assets or not os.path.isdir(
                import_path_for_new_assets
            ):
                import_path_for_new_assets = QtWidgets.QFileDialog.getExistingDirectory(
                    None,
                    "Select Folder where Unreal Asset (.uasset) will be located",
                    content_path,
                )
            if not import_path_for_new_assets or not os.path.isdir(
                import_path_for_new_assets
            ):
                logger.warning(
                    'Path where Unreal Asset (.uasset) will be located does not exist: "{}"'.format(
                        import_path_for_new_assets
                    )
                )
                continue

            try:
                relative_path = os.path.relpath(
                    import_path_for_new_assets, content_path
                )
            except ValueError:
                logger.warning(
                    "Selected Path is not in the proper project drive. Skipping import..."
                )
                continue
            if ".." in relative_path:
                logger.warning(
                    "Selected Path does not belong to current Unreal project directory. Skipping import..."
                )
                continue
            relative_path = (
                content_path if relative_path == "." else relative_path
            )
            asset_path = utils.join_path(
                "Game",
                relative_path,
                "{}.{}".format(asset_file_name, asset_file_name),
            )

            # TODO: Import options should be configurable by the user (through UI? or passing JSON import option files?)
            import_options = {
                "destination_name": asset_file_name,
                "import_materials": False,
                "import_textures": False,
                "save": False,
            }
            result = uegear_bridge.execute(
                "import_static_mesh",
                parameters={
                    "fbx_file": fbx_file_path,
                    "import_path": import_path_for_new_assets,
                    "import_options": str(import_options),
                },
            ).get("ReturnValue", False)
            if not result:
                logger.warning(
                    "Was not possible to export asset: {}. Please check Unreal Engine Output Log".format(
                        static_mesh
                    )
                )
                continue

            tag.apply_tag(
                static_mesh, tag.TAG_ASSET_NAME_ATTR_NAME, asset_file_name
            )
            tag.apply_tag(
                static_mesh, tag.TAG_ASSET_PATH_ATTR_NAME, asset_path
            )

        else:
            # Verify .uasset file for the asset exists within current Unreal Engine project directory
            asset_file_name = os.path.basename(asset_path).split(".")[0]
            uasset_file_name = asset_file_name + ".uasset"
            content_uasset_path = utils.join_path(
                content_path,
                os.path.dirname(asset_path).replace("/Game/", "/"),
                uasset_file_name,
            )
            if not os.path.isfile(content_uasset_path):
                logger.warning(
                    '.uasset file was not found: "{}"'.format(
                        content_uasset_path
                    )
                )
                continue

            export_file_name = "{}.fbx".format(asset_file_name)

            if not export_directory and export_in_original_path:
                # We try to retrieve the export path from the metadata of the Asset within Unreal Engine project
                asset_export_path = uegear_bridge.execute(
                    "asset_export_path", parameters={"asset_path": asset_path}
                ).get("ReturnValue", "")
                export_file_name = "{}.fbx".format(
                    os.path.basename(asset_export_path).split(".")[0]
                )
            else:
                if not export_directory:
                    asset_export_path = utils.join_path(
                        temp_folder, export_file_name
                    )
                else:
                    asset_export_path = utils.join_path(
                        export_directory, export_file_name
                    )

            # if it is not possible to find/create the original FBX export path we export the asset into a temp folder
            if export_directory or export_in_original_path:
                asset_export_directory = os.path.dirname(asset_export_path)
                if not os.path.isdir(asset_export_directory):
                    logger.info(
                        "Export directory does not exist, trying to create it: {}".format(
                            asset_export_directory
                        )
                    )
                    result = utils.create_folder(asset_export_directory)
                    if not result:
                        logger.warning(
                            'Was not possible to create original export path: "{}" | temp folder will be used instead...'.format(
                                asset_export_directory
                            )
                        )
                        asset_export_path = utils.join_path(
                            temp_folder, "{}.fbx".format(asset_file_name)
                        )
            asset_export_directory = os.path.dirname(asset_export_path)

            # export FBX file into disk
            fbx_file_path = ioutils.export_static_mesh(
                asset_export_directory, static_mesh, file_name=export_file_name
            )
            if not os.path.isfile(fbx_file_path):
                logger.warning(
                    'Something went wrong while exporting asset FBX file: "{}"'.format(
                        fbx_file_path
                    )
                )
                continue

            # TODO: Import options should be retrieved from the .uasset file located in Unreal
            import_options = {
                "destination_name": asset_file_name,
                "replace_existing": True,
                "save": False,
            }
            result = uegear_bridge.execute(
                "import_static_mesh",
                parameters={
                    "fbx_file": fbx_file_path,
                    "import_path": os.path.dirname(content_uasset_path),
                    "import_options": str(import_options),
                },
            ).get("ReturnValue", False)
            if not result:
                logger.warning(
                    "Was not possible to export asset: {}. Please check Unreal Engine Output Log".format(
                        static_mesh
                    )
                )
                continue

    return True


def export_cameras(cameras=None):
    # TODO: WIP
    """
    This method is still under heavy development, as the surrounding API does not
    yet have all the needed functionality implemented.

    If this does not get implemented, please remove it.
    """
    # FIXME: export_layout_json, does not support camera objects

    cameras = utils.force_list(cameras or utils.get_selected_cameras())
    if not cameras:
        logger.warning("No cameras to export")
        return False

    temp_folder = tempfile.gettempdir()
    cameras_file = io.export_layout_json(
        nodes=cameras, output_path=temp_folder
    )

    print("Camera Export Debug: {}".format(cameras_file))


    return False # Early exit for debugging reasons 

    result = self.execute(
        "import_maya_data_from_file", parameters={"data_file": cameras_file}
    )
    utils.safe_delete_file(cameras_file)

    return True


def export_layout_to_unreal(self, nodes=None):
    """
    Export nodes into a ueGear layout file and imports that layout into current opened Unreal level.

    :param str or list(str) or None nodes: list of nodes to include into the layout file. If not given, all current
            selected nodes will be added.
    :return: True if the export layout to Unreal operation was successful; False otherwise.
    :rtype: bool
    """

    nodes = utils.force_list(nodes or cmds.ls(sl=True, long=True))
    if not nodes:
        logger.warning("No layout nodes selected to export")
        return False

    temp_folder = tempfile.gettempdir()
    layout_file = io.export_layout_json(nodes=nodes, output_path=temp_folder)
    result = self.execute(
        "import_maya_layout_from_file", parameters={"layout_file": layout_file}
    )
    utils.safe_delete_file(layout_file)

    return True


def import_layout_from_unreal(export_assets=True):

    uegear_bridge = bridge.UeGearBridge()

    temp_folder = tempfile.gettempdir()
    temp_assets_folder = utils.clean_path(
        os.path.join(temp_folder, "uegear_temp_assets")
    )
    if os.path.isdir(temp_assets_folder):
        utils.safe_delete_folder(temp_assets_folder)
    utils.ensure_folder_exists(temp_assets_folder)

    result = uegear_bridge.execute(
        "export_maya_layout",
        parameters={
            "directory": temp_assets_folder,
            "export_assets": export_assets,
        },
    ).get("ReturnValue", "")

    if result and os.path.isfile(result):
        layout_data = utils.read_json_file(result)
        if layout_data:
            for actor_data in layout_data:
                fbx_file = actor_data.get("assetExportPath", None)
                if not fbx_file or not os.path.isfile(fbx_file):
                    continue
                

                # Check if object already exists in scene,
                dag_path = mgUtils.get_dag_path(actor_data["name"])
                # Check if object has the same guid and actor name
                asset_guid = actor_data.get("guid", "")
                actor_name = actor_data["name"]
                if dag_path:
                    guid_match = tag.tag_match(dag_path, asset_guid, tag.TAG_ASSET_GUID_ATTR_NAME)
                    name_match = tag.tag_match(dag_path, actor_name, tag.TAG_ACTOR_NAME_ATTR_NAME)
                    #   Object passes all checks, it needs to be deleted.
                    if guid_match and name_match:
                        dag_mod = OpenMaya.MDagModifier()
                        dag_mod.deleteNode(OpenMaya.MFnDagNode(dag_path).object())
                        dag_mod.doIt()

                imported_nodes = utils.import_static_fbx(fbx_file)

                transform_nodes = cmds.ls(imported_nodes, type="transform")
                transform_node = utils.get_first_in_list(transform_nodes)
                if not transform_node:
                    continue
                for transform_node in transform_nodes:
                    asset_guid = actor_data.get("guid", "")
                    asset_type = actor_data.get("assetType", "")
                    asset_name = actor_data.get("assetName", "")
                    asset_path = actor_data.get("assetPath", "")
                    actor_name = actor_data["name"]
                    translation = actor_data["translation"]
                    rotation = actor_data["rotation"]
                    scale = actor_data["scale"]
                    tag.apply_tag(
                        transform_node,
                        tag.TAG_ASSET_GUID_ATTR_NAME,
                        asset_guid,
                    )
                    if asset_type:
                        tag.apply_tag(
                            transform_node,
                            tag.TAG_ASSET_TYPE_ATTR_NAME,
                            asset_type,
                        )
                    else:
                        tag.auto_tag(transform_node)
                    tag.apply_tag(
                        transform_node,
                        tag.TAG_ASSET_NAME_ATTR_NAME,
                        asset_name,
                    )
                    tag.apply_tag(
                        transform_node,
                        tag.TAG_ASSET_PATH_ATTR_NAME,
                        asset_path,
                    )
                    tag.apply_tag(
                        transform_node,
                        tag.TAG_ACTOR_NAME_ATTR_NAME,
                        actor_name,
                    )
                    transform_node = cmds.rename(transform_node, actor_name)

                    # Converts the unreal matrix into maya matrix
                    obj_trans_matrix = OpenMaya.MTransformationMatrix()
                    obj_trans_matrix.setTranslation(OpenMaya.MVector(translation), OpenMaya.MSpace.kWorld)
                    obj_trans_matrix.setRotation(OpenMaya.MEulerRotation(rotation))
                    obj_trans_matrix.setScale(OpenMaya.MVector(scale), OpenMaya.MSpace.kWorld)

                    maya_trans_matrix = utils.convert_transformationmatrix_Unreal_to_Maya(obj_trans_matrix)

                    dag_path = mgUtils.get_dag_path(transform_node)
                    if dag_path:
                        transform_fn = OpenMaya.MFnTransform(dag_path)
                        transform_fn.setTransformation(OpenMaya.MTransformationMatrix(maya_trans_matrix))

    utils.safe_delete_folder(temp_assets_folder)

    return True


# def update_selected_transforms():
# 	"""
# 	Updates matching Unreal objects within current level with the transforms of the currently selected
# 	objects within Maya scene.
# 	"""
#
# 	uegear_bridge = bridge.UeGearBridge()
#
# 	selected_nodes = pm.selected()
# 	old_rotation_orders = list()
# 	for selected_node in selected_nodes:
# 		old_rotation_orders.append(selected_node.getRotationOrder())
# 		selected_node.setRotationOrder('XZY', True)
# 	try:
# 		objects = cmds.ls(sl=True, sn=True)
# 		for obj in objects:
# 			ue_world_transform = utils.get_unreal_engine_transform_for_maya_node(obj)
# 			result = uegear_bridge.execute('set_actor_world_transform', parameters={
# 				'actor_name': obj,
# 				'translation': str(ue_world_transform['rotatePivot']),
# 				'rotation': str(ue_world_transform['rotation']),
# 				'scale': str(ue_world_transform['scale']),
# 			})
# 	finally:
# 		for i, selected_node in enumerate(selected_nodes):
# 			selected_node.setRotationOrder(old_rotation_orders[i], True)
#
#
# def update_static_mesh(self, export_options=None):
#
# 	default_export_options = {
# 		'GenerateLog': False,
# 		'AnimationOnly': False,
# 		'Shapes': True,
# 		'Skins': False,
# 		'SmoothingGroups': True
# 	}
# 	export_options = export_options or dict()
# 	default_export_options.update(export_options)
#
# 	selected_mesh = utils.get_first_in_list(pm.ls(sl=True, type='transform'))
# 	if not selected_mesh:
# 		logger.warning('No selected mesh to export')
# 		return
#
# 	meshes = selected_mesh.getShapes() if selected_mesh else None
# 	if not meshes:
# 		logger.warning('Selected node has no shapes to export')
# 		return
#
# 	temp_folder = tempfile.gettempdir()
# 	fbx_temp_file_path = os.path.join(temp_folder, 'uegear_temp_static_mesh.fbx')
# 	try:
# 		utils.touch_path(fbx_temp_file_path)
# 		fbx_export_path = os.path.normpath(fbx_temp_file_path).replace('\\', '/')
# 		pyFBX.FBXExportGenerateLog(v=default_export_options.get('GenerateLog', False))
# 		pyFBX.FBXExportAnimationOnly(v=default_export_options.get('AnimationOnly', False))
# 		pyFBX.FBXExportShapes(v=default_export_options.get('Shapes', True))
# 		pyFBX.FBXExportSkins(v=default_export_options.get('Skins', False))
# 		pyFBX.FBXExportSmoothingGroups(v=default_export_options.get('SmoothingGroups', True))
# 		pyFBX.FBXExport(f=fbx_export_path, s=True)
# 	except Exception as exc:
# 		logger.error('Something went wrong while exporting static mesh: {}'.format(traceback.format_exc()))
# 	finally:
# 		try:
# 			pass
# 		except Exception as exc:
# 			logger.error('Something went wrong while importing static mesh into Unreal: {}'.format(
# 				traceback.format_exc()))
# 		try:
# 			utils.get_permission(fbx_temp_file_path)
# 		except Exception:
# 			pass
# 		try:
# 			os.remove(fbx_temp_file_path)
# 		except Exception:
# 			pass


# NOT IMPLEMENTED
def import_sequencer_cameras_timeline_from_unreal():
    """
    Imports the current active sequencer data from Unreal into Maya.
    Imports:
        - All Camera Tracks from Sequencer
    Updates:
        - Mayas Timerange, to match that of the sequencer.
        - Maya FPS, to match that of the dequencer.
    """
    print("Import Sequencer's Cameras and Timeline data - In Development")

    # [ ] Get active Sequencer in Unreal, else return
    # [ ] Get Cameras in Sequencer, else return
    # [ ] Get Sequencer Data, else return

    # Unreal Cameras exported to location
    # export FBX file into a temporal folder
    temp_folder = tempfile.gettempdir()


def import_selected_cameras_from_unreal():
    """
    Triggers the Unreal bridge call, to export the selected Camera
    tracks in the active sequencer, and import it into Maya.
    """
    print("Importing Selected Sequencer Cameras from Unreal...")

    uegear_bridge = bridge.UeGearBridge()

    # export FBX file into a temporal folder
    temp_folder = tempfile.gettempdir()

    # Send Unreal Command
    
    asset_export_datas = uegear_bridge.execute(
        "export_selected_sequencer_cameras", 
        parameters={"directory": temp_folder}
    ).get("ReturnValue", list())
    if not asset_export_datas:
        logger.warning(
            "Was not possible to export selected camera from Unreal"
        )
        return False
    
    # Loop over Unreal result

    for asset_export_data in asset_export_datas:
        # import asset from FBX file
        fbx_file = asset_export_data.get("fbx_file", None)
        if not fbx_file or not os.path.isfile(fbx_file):
            logger.warning(
                "No FBX file found for asset data: {}".format(
                    asset_export_data
                )
            )
            continue
        logger.info('Importing Asset from FBX file: "{}"'.format(fbx_file))
        imported_nodes = utils.import_fbx(fbx_file)

        # TODO: Check if Camera with the same name and metadata exists in the Level
        #   [ ] Update it
        #  - I would recommend not deleting it incase it has been added to layers or grouping.
        #   Deleting would be the most destructive outcome.

        # tag imported transform nodes from FBX
        transform_nodes = cmds.ls(imported_nodes, type="transform")
        for transform_node in transform_nodes:
            asset_type = asset_export_data.get("asset_type", "")
            asset_name = asset_export_data.get("name", "")
            asset_path = asset_export_data.get("path", "")
            if asset_type:
                tag.apply_tag(
                    transform_node, tag.TAG_ASSET_TYPE_ATTR_NAME, asset_type
                )
            else:
                tag.auto_tag(transform_node)
            if asset_name:
                tag.apply_tag(
                    transform_node, tag.TAG_ASSET_NAME_ATTR_NAME, asset_name
                )
            if asset_path:
                tag.apply_tag(
                    transform_node, tag.TAG_ASSET_PATH_ATTR_NAME, asset_path
                )

    return True


def update_sequencer_camera_from_maya():
    print("[mGear] Updating Sequencer, using selected Maya Camera")

    uegear_bridge = bridge.UeGearBridge()

    # Retrieve a dictionary with the assets that can be exported.
    nodes_to_export = cmds.ls(sl=True, long=True)
    objects_map = io.exportable_assets(nodes=nodes_to_export)
    if not objects_map:
        msg = 'No exportable assets found in nodes to export: "{}".'
        msg += 'Make sure assets are tagged.'
        logger.warning(msg.format(nodes_to_export))
        return False

    # Retrieve the Camera nodes to update active sequencer
    cameras = objects_map.get(tag.TagTypes.Camera, list())
    if not cameras:
        logger.warning("No cameras to update")
        return False
    
    # Create a list of AssetPaths, Camera Name, export_path
    ue_camera_names = tag.tag_values(tag.TAG_ASSET_NAME_ATTR_NAME, cameras)
    camera_sequence_paths = tag.tag_values(tag.TAG_ASSET_PATH_ATTR_NAME, cameras)
    camera_export_path = dict()

    # Export Camera to temp location
    temp_folder = tempfile.gettempdir()

    # Export FBX file into disk
    for i in range(len(cameras)):
        camera_name = ue_camera_names[i]
        fbx_file_path = os.path.join(temp_folder, camera_name + ".fbx")
        
        try:
            cmds.file(fbx_file_path, force=True, typ="FBX export", pr=True, es=True)
            msg = "Camera '{}' exported as FBX to '{}'"
            print(msg.format(camera_name, fbx_file_path))
        except Exception as e:
            print("Error exporting camera: {}".format(str(e)))
            continue

        if not os.path.isfile(fbx_file_path):
            msg ='Something went wrong while exporting asset FBX file: "{}"' 
            logger.warning(msg.format(fbx_file_path))
            continue

        camera_export_path[camera_name] = fbx_file_path

        uegear_bridge.execute("update_sequencer_camera_from_maya", 
            parameters={
                "camera_name": camera_name,
                "sequencer_package":camera_sequence_paths[i],
                "fbx_path":fbx_file_path
            }
        ).get("ReturnValue", False)

    
    # Clean up temporary data
    for path in camera_export_path.values():
        try:
            os.remove(path)
        except PermissionError as p_e:
            print(p_e)
        except IOError as io_e:
            print(io_e)
        