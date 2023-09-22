import maya.cmds as cmds
import mgear

from mgear.core import string

menuID = "ueGear"


def install():
    """Installs ueGear sub-menu"""

    cmds.setParent(mgear.menu_id, menu=True)
    cmds.menuItem(divider=True)
    commands = (
        ("Apply ueGear Tag to selected nodes", str_auto_tag),
        ("Remove ueGear Tags from selected nodes", str_remove_tag),
        ("-----", None),
        (
            "Import Selected Assets from Unreal",
            str_import_selected_assets_from_unreal,
        ),
        (
            "Export Selected Assets to Unreal",
            str_export_selected_assets_to_unreal,
        ),
        ("-----", None),
        (
            "Import Selected Camers from Sequencer",
            str_import_selected_cameras_from_unreal,
        ),
        (
            "Update Sequencer Camers from Maya Selection",
            str_update_sequencer_camera_from_maya,
        ),
        ("-----", None),
        (
            "Import Selected Assets from Level",
            str_import_selected_assets_from_level_unreal,
        ),
        # (
        #     "Update Sequencer Camers from Maya Selection",
        #     str_update_sequencer_camera_from_maya,
        # ),
    )

    mgear.menu.install(menuID, commands, image="UE5.svg")


str_auto_tag = """
from mgear.uegear import tag
tag.auto_tag()
"""

str_remove_tag = """
from mgear.uegear import tag
tag.remove_all_tags()
"""

str_import_selected_assets_from_unreal = """
from mgear.uegear import commands
commands.import_selected_assets_from_unreal()
"""

str_export_selected_assets_to_unreal = """
from mgear.uegear import commands
commands.export_selected_assets_to_unreal()
"""

str_import_selected_cameras_from_unreal = """
from mgear.uegear import commands
commands.import_selected_cameras_from_unreal()
"""

str_update_sequencer_camera_from_maya = """
from mgear.uegear import commands
commands.update_sequencer_camera_from_maya()
"""

str_import_selected_assets_from_level_unreal = """
from mgear.uegear import commands
commands.import_layout_from_unreal()
"""