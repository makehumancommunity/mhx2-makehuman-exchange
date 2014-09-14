# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    'name': 'Import-Runtime: MakeHuman Exchange 2 (.mhx2)',
    'author': 'Thomas Larsson',
    'version': (0,1,0),
    "blender": (2, 71, 0),
    'location': "File > Import > MakeHuman (.mhx2)",
    'description': 'Import files in the new MakeHuman eXhange format (.mhx2)',
    'warning': '',
    'wiki_url': '',
    'category': 'MakeHuman'}

if "bpy" in locals():
    print("Reloading MHX2 importer-runtime v %d.%d.%d" % bl_info["version"])
    import imp
    imp.reload(armature)
    imp.reload(hm8)
    imp.reload(utils)
    imp.reload(error)
    imp.reload(config)
    imp.reload(load_json)
    imp.reload(importer)
    imp.reload(materials)
    imp.reload(proxy)
    imp.reload(geometries)
    imp.reload(layers)
    imp.reload(fkik)
    imp.reload(drivers)
    imp.reload(bone_drivers)
    imp.reload(faceshift)
    imp.reload(hide)
    imp.reload(shapekeys)
    imp.reload(visemes)
    imp.reload(merge)
else:
    print("Loading MHX2 importer-runtime v %d.%d.%d" % bl_info["version"])
    from . import armature
    from . import hm8
    from . import utils
    from . import error
    from . import config
    from . import load_json
    from . import importer
    from . import materials
    from . import proxy
    from . import geometries
    from . import layers
    from . import fkik
    from . import drivers
    from . import bone_drivers
    from . import faceshift
    from . import hide
    from . import shapekeys
    from . import visemes
    from . import merge

import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import os

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

class ImportMHX2(bpy.types.Operator, ImportHelper):
    """Import from MHX2 file format (.mhx2)"""
    bl_idname = "import_scene.makehuman_mhx2"
    bl_description = 'Import from MHX2 file format (.mhx2)'
    bl_label = "Import MHX2"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".mhx2"
    filter_glob = StringProperty(default="*.mhx2", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    useHelpers = BoolProperty(name="Helper Geometry", description="Keep helper geometry", default=False)
    useOffset = BoolProperty(name="Offset", description="Add offset for feet on ground", default=True)
    useOverride = BoolProperty(name="Override Exported Data", description="Override rig and mesh definitions in mhx2 file", default=False)

    useCustomShapes = BoolProperty(name="Custom Shapes", description="Custom bone shapes", default=True)
    useFaceShapes = BoolProperty(name="Face Shapes", description="Face shapes", default=False)
    useFaceDrivers = BoolProperty(name="Face Drivers", description="Face drivers", default=False)
    useFacePanel = BoolProperty(name="Face Panel", description="Face panel", default=False)
    useRig = BoolProperty(name="Add Rig", description="Add rig", default=False)

    useHumanType = EnumProperty(
        items = [('BASE', "Base", "Base mesh"),
                 ('PROXY', "Proxy", "Exported topology (if exists)"),
                 ('BOTH', "Both", "Both base mesh and proxy mesh"),
                 ],
        name = "Import Human Type",
        description = "Human types to be imported",
        default = 'BOTH')
    mergeBodyParts = BoolProperty(name="Merge Body Parts", description="Merge body parts", default=False)
    mergeToProxy = BoolProperty(name="Merge To Proxy", description="Merge body parts to proxy mesh is such exists", default=True)
    mergeMaxType = EnumProperty(
        items = [('BODY', "Body", "Merge up to body"),
                 ('HAIR', "Hair", "Merge up to hair"),
                 ('CLOTHES', "Clothes", "Merge all"),
                 ],
        name = "Maximum Merge Type",
        description = "Maximum type to merge",
        default = 'BODY')

    rigTypes = []
    folder = os.path.dirname(__file__)
    for file in os.listdir(os.path.join(folder, "armature/data/rigs")):
        fname = os.path.splitext(file)[0]
        entry = (fname.upper(), fname.capitalize(), file)
        if fname == "mhx":
            mhx = entry
        elif fname == "rigify":
            rigify = entry
        else:
            rigTypes.append(entry)
    rigTypes = [mhx, rigify] + rigTypes

    rigType = EnumProperty(
        items = rigTypes,
        name = "Rig Type",
        description = "Rig type",
        default = 'MHX')

    genitalia = EnumProperty(
        items = [("NONE", "None", "None"),
                 ("PENIS", "Male", "Add male genitalia"),
                 ("VULVA", "Female", "Add female genitalia")],
        name = "Genitalia",
        description = "Genitalia",
        default = 'NONE')
    usePenisRig = BoolProperty(name="Penis Rig", description="Add a penis rig", default=False)

    def execute(self, context):
        from .config import Config
        cfg = Config().fromSettings(self)
        importer.importMhx2File(self.filepath, cfg, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "useOverride")

        layout.separator()
        box = layout.box()
        box.label("Merging")
        box.prop(self, "mergeBodyParts")
        if self.mergeBodyParts and self.useHumanType != 'BODY':
            box.prop(self, "mergeToProxy")
        if self.mergeBodyParts:
            box.prop(self, "mergeMaxType")

        if not self.useOverride:
            return

        layout.separator()
        layout.label("Import Human Type:")
        layout.prop(self, "useHumanType", expand=True)

        layout.prop(self, "useHelpers")
        layout.prop(self, "useOffset")
        layout.prop(self, "useFaceShapes")
        if (self.useFaceShapes and
            not self.useFacePanel):
            layout.prop(self, "useFaceDrivers")

        layout.label("Add Genitalia:")
        layout.prop(self, "genitalia", expand=True)

        box = layout.box()
        box.label("Rigging")
        box.prop(self, "useRig")
        if self.useRig:
            box.prop(self, "rigType")
            box.prop(self, "useCustomShapes")
            if self.useFaceShapes and not self.useFaceDrivers:
                box.prop(self, "useFacePanel")
            if self.genitalia == 'PENIS':
                box.prop(self, "usePenisRig")

#------------------------------------------------------------------------
#    Setup panel
#------------------------------------------------------------------------

class MhxSetupPanel(bpy.types.Panel):
    bl_label = "MHX Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        scn = context.scene

        layout.operator("import_scene.makehuman_mhx2")
        if ob is None:
            return

        if ob.type == 'MESH':
            layout.separator()
            layout.operator("mhx2.add_hair")
            layout.operator("mhx2.merge_objects")

        layout.separator()
        layout.operator("mhx2.add_hide_drivers")
        layout.operator("mhx2.remove_hide_drivers")

        layout.separator()
        layout.operator("mhx2.add_facerig_drivers")
        layout.operator("mhx2.remove_facerig_drivers")
        layout.operator("mhx2.load_faceshift_bvh")

        layout.separator()
        op = layout.operator("mhx2.add_shapekeys", text="Add Face Shapes")
        op.filename="data/hm8/faceshapes/faceshapes.json"
        layout.operator("mhx2.add_shapekey_drivers")
        layout.operator("mhx2.remove_shapekey_drivers")

#------------------------------------------------------------------------
#    Mhx Layers Panel
#------------------------------------------------------------------------

from .layers import MhxLayers, OtherLayers

class MhxLayersPanel(bpy.types.Panel):
    bl_label = "Layers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig == 'MHX')

    def draw(self, context):
        layout = self.layout
        layout.operator("mhx2.pose_enable_all_layers")
        layout.operator("mhx2.pose_disable_all_layers")

        rig = context.object
        if rig.MhxRig == 'MHX':
            layers = MhxLayers
        else:
            layers = OtherLayers

        for (left,right) in layers:
            row = layout.row()
            if type(left) == str:
                row.label(left)
                row.label(right)
            else:
                for (n, name, prop) in [left,right]:
                    row.prop(rig.data, "layers", index=n, toggle=True, text=name)

        return
        layout.separator()
        layout.label("Export/Import MHP")
        layout.operator("mhx2.saveas_mhp")
        layout.operator("mhx2.load_mhp")


#------------------------------------------------------------------------
#    Mhx FK/IK switch panel
#------------------------------------------------------------------------

class MhxFKIKPanel(bpy.types.Panel):
    bl_label = "FK/IK Switch"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig == 'MHX')

    def draw(self, context):
        rig = context.object
        layout = self.layout

        row = layout.row()
        row.label("")
        row.label("Left")
        row.label("Right")

        layout.label("FK/IK switch")
        row = layout.row()
        row.label("Arm")
        self.toggleButton(row, rig, "MhaArmIk_L", " 3", " 2")
        self.toggleButton(row, rig, "MhaArmIk_R", " 19", " 18")
        row = layout.row()
        row.label("Leg")
        self.toggleButton(row, rig, "MhaLegIk_L", " 5", " 4")
        self.toggleButton(row, rig, "MhaLegIk_R", " 21", " 20")

        layout.label("IK Influence")
        row = layout.row()
        row.label("Arm")
        row.prop(rig, '["MhaArmIk_L"]', text="")
        row.prop(rig, '["MhaArmIk_R"]', text="")
        row = layout.row()
        row.label("Leg")
        row.prop(rig, '["MhaLegIk_L"]', text="")
        row.prop(rig, '["MhaLegIk_R"]', text="")

        try:
            ok = (rig["MhxVersion"] >= 12)
        except KeyError:
            ok = False
        if not ok:
            layout.label("Snapping only works with MHX version 1.12 and later.")
            return

        layout.separator()
        layout.label("Snapping")
        row = layout.row()
        row.label("Rotation Limits")
        row.prop(rig, '["MhaRotationLimits"]', text="")
        row.prop(rig, "MhxSnapExact", text="Exact Snapping")

        layout.label("Snap Arm bones")
        row = layout.row()
        row.label("FK Arm")
        row.operator("mhx2.snap_fk_ik", text="Snap L FK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx2.snap_fk_ik", text="Snap R FK Arm").data = "MhaArmIk_R 18 19 28"
        row = layout.row()
        row.label("IK Arm")
        row.operator("mhx2.snap_ik_fk", text="Snap L IK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx2.snap_ik_fk", text="Snap R IK Arm").data = "MhaArmIk_R 18 19 28"

        layout.label("Snap Leg bones")
        row = layout.row()
        row.label("FK Leg")
        row.operator("mhx2.snap_fk_ik", text="Snap L FK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx2.snap_fk_ik", text="Snap R FK Leg").data = "MhaLegIk_R 20 21 28"
        row = layout.row()
        row.label("IK Leg")
        row.operator("mhx2.snap_ik_fk", text="Snap L IK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx2.snap_ik_fk", text="Snap R IK Leg").data = "MhaLegIk_R 20 21 28"


    def toggleButton(self, row, rig, prop, fk, ik):
        if rig[prop] > 0.5:
            row.operator("mhx2.toggle_fk_ik", text="IK").toggle = prop + " 0" + fk + ik
        else:
            row.operator("mhx2.toggle_fk_ik", text="FK").toggle = prop + " 1" + ik + fk


#------------------------------------------------------------------------
#   Visibility panel
#------------------------------------------------------------------------

class VisibilityPanel(bpy.types.Panel):
    bl_label = "Visibility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'ARMATURE' and ob.MhxVisibilityDrivers)

    def draw(self, context):
        ob = context.object
        layout = self.layout
        layout.operator("mhx2.prettify_visibility")
        props = list(ob.keys())
        props.sort()
        for prop in props:
            if prop[0:3] == "Mhh":
                if hasattr(ob, prop):
                    path = prop
                else:
                    path = '["%s"]' % prop
                layout.prop(ob, path, text=prop[3:])

#------------------------------------------------------------------------
#   Facerig panel
#------------------------------------------------------------------------

class FaceComponentsPanel(bpy.types.Panel):
    bl_label = "Face Components"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxFaceRigDrivers)

    def draw(self, context):
        drawPropPanel(self, context.object, "Mfa")

#------------------------------------------------------------------------
#   Shapekey panel
#------------------------------------------------------------------------

class MhxShapekeyPanel(bpy.types.Panel):
    bl_label = "Shapekeys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxShapekeyDrivers)

    def draw(self, context):
        drawPropPanel(self, context.object, "Mhs")

#------------------------------------------------------------------------
#   Common drawing code for property panels
#------------------------------------------------------------------------

def drawPropPanel(self, ob, prefix):
    from .drivers import getArmature
    rig = getArmature(ob)
    if rig:
        layout = self.layout
        layout.operator("mhx2.reset_props").prefix = prefix
        for prop in rig.keys():
            if prop[0:3] != prefix:
                continue
            row = layout.split(0.8)
            row.prop(rig, '["%s"]' % prop, text=prop[3:])
            op = row.operator("mhx2.pin_prop", icon='UNPINNED')
            op.key = prop
            op.prefix = prefix

#------------------------------------------------------------------------
#   Visemes panel
#------------------------------------------------------------------------

class MhxVisemesPanel(bpy.types.Panel):
    bl_label = "Visemes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and (ob.MhxShapekeyDrivers or ob.MhxFacePanel))

    def draw(self, context):
        from .visemes import getLayout
        for vrow in getLayout():
            row = self.layout.row()
            for vis in vrow:
                row.operator("mhx2.set_viseme", text=vis).viseme = vis

        self.layout.separator()
        self.layout.operator("mhx2.load_moho")
        self.layout.operator("mhx2.delete_lipsync")

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def menu_func(self, context):
    self.layout.operator(ImportMHX2.bl_idname, text="MakeHuman (.mhx2)...")

def register():
    bpy.types.Object.MhxRig = StringProperty(default="")
    bpy.types.Object.MhxHuman = BoolProperty(default=False)
    bpy.types.Object.MhxScale = FloatProperty(default=1.0)
    bpy.types.Object.MhxMesh = BoolProperty(default=False)
    bpy.types.Object.MhxSeedMesh = BoolProperty(default=False)
    bpy.types.Object.MhxRigify = BoolProperty(default=False)
    bpy.types.Object.MhxSnapExact = BoolProperty(default=False)
    bpy.types.Object.MhxVisibilityDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxHasFaceShapes = BoolProperty(default=False)
    bpy.types.Object.MhxFacePanel = BoolProperty(default=False)
    bpy.types.Object.MhxShapekeyDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxFaceRig = BoolProperty(default=False)
    bpy.types.Object.MhxFaceRigDrivers = BoolProperty(default=False)

    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        pass
    try:
        bpy.types.INFO_MT_file_import.remove(menu_func)
    except:
        pass

if __name__ == "__main__":
    unregister()
    register()

print("MHX2 successfully (re)loaded")
