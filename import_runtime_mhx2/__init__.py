# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script Copyright (C) Thomas Larsson 2014 - 2020
#  Script Copyright (C) MakeHuman Community 2020
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
    'version': (0,32),
    'blender': (2, 80, 0),
    'location': "File > Import-Export",
    'description': 'Import files in the new MakeHuman eXchange format (.mhx2)',
    'warning': '',
    'wiki_url': 'http://thomasmakehuman.wordpress.com/mhx2-documentation/',
    'category': 'MakeHuman'}

if "bpy" in locals():
    print("Reloading MHX2 importer-runtime v %d.%d" % bl_info["version"])
    import importlib
    importlib.reload(utils)
    importlib.reload(import_props)
    importlib.reload(buttons28)
    importlib.reload(armature)
    importlib.reload(hm8)
    importlib.reload(error)
    importlib.reload(config)
    importlib.reload(load_json)
    importlib.reload(masks)
    importlib.reload(materials)
    importlib.reload(shaders)
    importlib.reload(proxy)
    importlib.reload(hair)
    importlib.reload(geometries)
    importlib.reload(layers)
    importlib.reload(fkik)
    importlib.reload(drivers)
    importlib.reload(bone_drivers)
    importlib.reload(faceshift)
    importlib.reload(hide)
    importlib.reload(shapekeys)
    importlib.reload(visemes)
    importlib.reload(merge)
    importlib.reload(importer)
else:
    import bpy
    print("Loading MHX2 importer-runtime v %d.%d" % bl_info["version"])
    from . import utils
    from . import import_props
    from . import buttons28
    from . import armature
    from . import materials
    from . import shaders
    from . import proxy
    from . import hair
    from . import layers
    from . import fkik
    from . import drivers
    from . import bone_drivers
    from . import faceshift
    from . import hide
    from . import shapekeys
    from . import visemes
    from . import merge
    from . import importer

from bpy.props import *
from .error import *
from .utils import *

Region = "UI"

#------------------------------------------------------------------------
#    Setup panel
#------------------------------------------------------------------------

class MHX_PT_Setup(bpy.types.Panel):
    bl_label = "MHX Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        scn = context.scene

        layout.operator("import_scene.makehuman_mhx2")
        #layout.operator("mhx2.make_skin_shader")

        if (ob is None or
            (ob.type == 'MESH' and not ob.MhxUuid) or
            (ob.type == 'ARMATURE' and not ob.MhxRig) or
            (ob.type not in ['MESH', 'ARMATURE'])):
            return

        layout.separator()
        layout.operator("mhx2.add_simple_materials")
        layout.operator("mhx2.merge_objects")
        if ob.MhxRigify:
            layout.operator("mhx2.finalize_rigify")

        layout.separator()
        box = layout.box()
        box.label(text="Design Human")
        box.prop(scn, "MhxDesignHuman", text="")
        box.operator("mhx2.set_design_human")
        box.operator("mhx2.clear_design_human")

        layout.separator()
        box = layout.box()
        box.label(text="Assets")
        box.operator("mhx2.add_asset")
        box.prop(scn, "MhxUseConservativeMasks")
        box.prop(scn, "MhxHairColor")
        box.prop(scn, "MhxUseHairDynamics")
        #box.prop(scn, "MhxUseDeflector")
        box.prop(scn, "MhxMinHairLength")
        box.prop(scn, "MhxMinHairOrientation")
        box.prop(scn, "MhxHairKeySeparation")

        #Not in release
        #box.operator("mhx2.particlify_hair")

        layout.separator()
        box = layout.box()
        box.label(text="Visibility")
        box.operator("mhx2.add_hide_drivers")
        box.operator("mhx2.remove_hide_drivers")

        layout.separator()
        box = layout.box()
        box.label(text="Facial Rig")
        #box.operator("mhx2.add_facerig_drivers")
        box.operator("mhx2.remove_facerig_drivers")

        layout.separator()
        box = layout.box()
        box.label(text="Shapekeys")
        op = box.operator("mhx2.add_shapekeys", text="Add Face Shapes")
        op.filename="data/hm8/faceshapes/faceshapes.mxa"
        box.separator()
        box.operator("mhx2.add_face_shape_drivers")
        box.operator("mhx2.remove_face_shape_drivers")
        box.separator()
        box.operator("mhx2.add_other_shape_drivers")
        box.operator("mhx2.remove_other_shape_drivers")


#------------------------------------------------------------------------
#    Mhx License Panel
#------------------------------------------------------------------------

class MHX_PT_License(bpy.types.Panel):
    bl_label = "License"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        ob = context.object
        if ob and ob.type == 'MESH':
            layout.label(text="Mesh:")
            layout.prop(ob, "MhxAuthor", text="Author")
            layout.prop(ob, "MhxLicense", text="License")
            layout.prop(ob, "MhxHomePage", text="Homepage")

            if ob.particle_systems:
                layout.separator()
                layout.label(text="Hair:")
                layout.prop(ob, "MhxHairAuthor", text="Author")
                layout.prop(ob, "MhxHairLicense", text="License")
                layout.prop(ob, "MhxHairHomePage", text="Homepage")

#------------------------------------------------------------------------
#    Mhx Layers Panel
#------------------------------------------------------------------------

from .layers import MhxLayers, OtherLayers

class MHX_PT_Layers(bpy.types.Panel):
    bl_label = "Layers"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig in ('MHX', 'EXPORTED_MHX'))

    def draw(self, context):
        layout = self.layout
        layout.operator("mhx2.pose_enable_all_layers")
        layout.operator("mhx2.pose_disable_all_layers")

        rig = context.object
        if rig.MhxRig in ('MHX', 'EXPORTED_MHX'):
            layers = MhxLayers
        else:
            layers = OtherLayers

        for (left,right) in layers:
            row = layout.row()
            if type(left) == str:
                row.label(text=left)
                row.label(text=right)
            else:
                for (n, name, prop) in [left,right]:
                    row.prop(rig.data, "layers", index=n, toggle=True, text=name)

        return
        layout.separator()
        layout.label(text="Export/Import MHP")
        layout.operator("mhx2.saveas_mhp")
        layout.operator("mhx2.load_mhp")


#------------------------------------------------------------------------
#    Mhx FK/IK switch panel
#------------------------------------------------------------------------

class MHX_PT_FKIK(bpy.types.Panel):
    bl_label = "FK/IK Switch"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig in ('MHX', 'EXPORTED_MHX'))

    def draw(self, context):
        rig = context.object
        layout = self.layout

        row = layout.row()
        row.label(text="")
        row.label(text="Left")
        row.label(text="Right")

        layout.label(text="FK/IK switch")
        row = layout.row()
        row.label(text="Arm")
        self.toggle(row, rig, "MhaArmIk_L", " 3", " 2")
        self.toggle(row, rig, "MhaArmIk_R", " 19", " 18")
        row = layout.row()
        row.label(text="Leg")
        self.toggle(row, rig, "MhaLegIk_L", " 5", " 4")
        self.toggle(row, rig, "MhaLegIk_R", " 21", " 20")

        layout.label(text="IK Influence")
        row = layout.row()
        row.label(text="Arm")
        row.prop(rig, '["MhaArmIk_L"]', text="")
        row.prop(rig, '["MhaArmIk_R"]', text="")
        row = layout.row()
        row.label(text="Leg")
        row.prop(rig, '["MhaLegIk_L"]', text="")
        row.prop(rig, '["MhaLegIk_R"]', text="")

        layout.separator()
        layout.label(text="Snapping")
        row = layout.row()
        row.label(text="Rotation Limits")
        row.prop(rig, "MhaRotationLimits", text="")
        #row.prop(rig, "MhxSnapExact", text="Exact Snapping")

        layout.label(text="Snap Arm bones")
        row = layout.row()
        row.label(text="FK Arm")
        row.operator("mhx2.snap_fk_ik", text="Snap L FK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx2.snap_fk_ik", text="Snap R FK Arm").data = "MhaArmIk_R 18 19 28"
        row = layout.row()
        row.label(text="IK Arm")
        row.operator("mhx2.snap_ik_fk", text="Snap L IK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx2.snap_ik_fk", text="Snap R IK Arm").data = "MhaArmIk_R 18 19 28"

        layout.label(text="Snap Leg bones")
        row = layout.row()
        row.label(text="FK Leg")
        row.operator("mhx2.snap_fk_ik", text="Snap L FK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx2.snap_fk_ik", text="Snap R FK Leg").data = "MhaLegIk_R 20 21 28"
        row = layout.row()
        row.label(text="IK Leg")
        row.operator("mhx2.snap_ik_fk", text="Snap L IK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx2.snap_ik_fk", text="Snap R IK Leg").data = "MhaLegIk_R 20 21 28"


    def toggle(self, row, rig, prop, fk, ik):
        if getattr(rig, prop) > 0.5:
            row.operator("mhx2.toggle_fk_ik", text="IK").toggle = prop + " 0" + fk + ik
        else:
            row.operator("mhx2.toggle_fk_ik", text="FK").toggle = prop + " 1" + ik + fk


#------------------------------------------------------------------------
#   MHX Control panel
#------------------------------------------------------------------------

class MHX_PT_Control(bpy.types.Panel):
    bl_label = "MHX Control"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig in ('MHX', 'EXPORTED_MHX'))

    def draw(self, context):
        ob = context.object
        layout = self.layout

        lrProps = []
        props = []
        lrFaceProps = []
        plist = list(ob.keys())
        plist.sort()
        for prop in plist:
            if prop[0:3] == 'Mha':
                if prop[-2:] == '_L':
                    lrProps.append(prop[:-2])
                elif prop[-2:] != '_R':
                    props.append(prop)

        for prop in props:
            layout.prop(ob,prop, text=prop[3:])

        layout.separator()
        row = layout.row()
        row.label(text="Left")
        row.label(text="Right")
        for prop in lrProps:
            row = layout.row()
            row.prop(ob, prop+"_L", text=prop[3:])
            row.prop(ob, prop+"_R", text=prop[3:])

#------------------------------------------------------------------------
#   Visibility panel
#------------------------------------------------------------------------

class Visibility(bpy.types.Panel):
    bl_label = "Visibility"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
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

class FaceUnits(bpy.types.Panel):
    bl_label = "Face Units"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxFaceRigDrivers)

    def draw(self, context):
        rig = context.object
        layout = self.layout
        layout.operator("mhx2.reset_props", text="Reset Expressions").prefix = "Mfa"
        layout.operator("mhx2.load_faceshift_bvh")
        drawProperties(layout, rig, "Mfa")

#------------------------------------------------------------------------
#   Expression
#------------------------------------------------------------------------

class Expression(bpy.types.Panel):
    bl_label = "Expressions"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxFaceRigDrivers and rig.MhxExpressions != "")

    def draw(self, context):
        rig = context.object
        layout = self.layout
        layout.operator("mhx2.reset_props", text="Reset Expressions").prefix = "Mfa"
        layout.prop(rig, "MhxExprStrength")
        exprs = rig.MhxExpressions.split("&")
        for ename in exprs:
            btn = layout.operator("mhx2.set_expression", text=ename)
            btn.units = rig["Mhu"+ename]

#------------------------------------------------------------------------
#   Face Shape panel
#------------------------------------------------------------------------

class MHX_PT_FaceShape(bpy.types.Panel):
    bl_label = "Facial Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxFaceShapeDrivers)

    def draw(self, context):
        rig = context.object
        if rig:
            layout = self.layout
            layout.operator("mhx2.reset_props").prefix = "Mhf"
            drawProperties(layout, rig, "Mhf")

#------------------------------------------------------------------------
#   Pose panel
#------------------------------------------------------------------------

class MHX_PT_Pose(bpy.types.Panel):
    bl_label = "Poses"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxPoses)

    def draw(self, context):
        rig = context.object
        layout = self.layout
        for anim in rig.MhxPoses.split("&"):
            aname,rest = anim.split(":",1)
            layout.operator("mhx2.set_pose", text=aname).string = rest

#------------------------------------------------------------------------
#   Other Shape panel
#------------------------------------------------------------------------

class MHX_PT_OtherShape(bpy.types.Panel):
    bl_label = "Other Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxOtherShapeDrivers)

    def draw(self, context):
        rig = context.object
        if rig:
            layout = self.layout
            layout.operator("mhx2.reset_props").prefix = "Mho"
            drawProperties(layout, rig, "Mho")

#------------------------------------------------------------------------
#   Common drawing code for property panels
#------------------------------------------------------------------------

def drawProperties(layout, rig, prefix):
    for prop in rig.keys():
        if prop[0:3] != prefix:
            continue
        row = splitLayout(layout, 0.8)
        row.prop(rig, '["%s"]' % prop, text=prop[3:])
        op = row.operator("mhx2.pin_prop", icon='UNPINNED')
        op.key = prop
        op.prefix = prefix

#------------------------------------------------------------------------
#   Visemes panel
#------------------------------------------------------------------------

class MHX_PT_Visemes(bpy.types.Panel):
    bl_label = "Visemes"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and (ob.MhxFaceShapeDrivers or ob.MhxHasFaceShapes or ob.MhxFacePanel))

    def draw(self, context):
        from .visemes import getLayout
        for vrow in getLayout():
            row = self.layout.row()
            for vis in vrow:
                row.operator("mhx2.set_viseme", text=vis).viseme = vis

        self.layout.separator()
        self.layout.operator("mhx2.load_moho")
        self.layout.operator("mhx2.bake_face_anim")
        self.layout.operator("mhx2.delete_lipsync")


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

classes = [
    MHX_PT_Setup,
    MHX_PT_License,
    MHX_PT_Layers,
    MHX_PT_FKIK,
    MHX_PT_Control,
    MHX_PT_FaceShape,
    MHX_PT_Pose,
    MHX_PT_OtherShape,
    MHX_PT_Visemes,

    ErrorOperator
]

def menu_func(self, context):
    self.layout.operator(importer.MHX_OT_Import.bl_idname, text="MakeHuman (.mhx2)")

def register():
    bpy.types.Object.MhxRig = StringProperty(default="")
    bpy.types.Object.MhxHuman = BoolProperty(default=False)
    bpy.types.Object.MhxUuid = StringProperty(default="")
    bpy.types.Object.MhxScale = FloatProperty(default=1.0)
    bpy.types.Object.MhxOffset = StringProperty(default="[0,0,0]")
    bpy.types.Object.MhxMesh = BoolProperty(default=False)
    bpy.types.Object.MhxSeedMesh = BoolProperty(default=False)
    bpy.types.Object.MhxRigify = BoolProperty(default=False)
    bpy.types.Object.MhxSnapExact = BoolProperty(default=False)
    bpy.types.Object.MhxVisibilityDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxHasFaceShapes = BoolProperty(default=False)
    bpy.types.Object.MhxFacePanel = BoolProperty(default=False)
    bpy.types.Object.MhxFaceShapeDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxOtherShapeDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxFaceRig = BoolProperty(default=False)
    bpy.types.Object.MhxFaceRigDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxExpressions = StringProperty(default="")
    bpy.types.Object.MhxExprStrength = FloatProperty(name="Expression strength", default=1.0, min=0.0, max=1.0)

    bpy.types.Object.MhxPoses = StringProperty(default="")

    # License properties
    bpy.types.Object.MhxAuthor = StringProperty(default="")
    bpy.types.Object.MhxLicense = StringProperty(default="")
    bpy.types.Object.MhxHomePage = StringProperty(default="")
    bpy.types.Object.MhxHairAuthor = StringProperty(default="")
    bpy.types.Object.MhxHairLicense = StringProperty(default="")
    bpy.types.Object.MhxHairHomePage = StringProperty(default="")

    # MHX Control properties
    bpy.types.Object.MhaGazeFollowsHead = FloatProperty(default=1.0, min=0.0, max=1.0)
    bpy.types.Object.MhaRotationLimits = FloatProperty(default=0.8, min=0.0, max=1.0)

    bpy.types.Object.MhaArmHinge_L = BoolProperty(default=False)
    bpy.types.Object.MhaArmIk_L = FloatProperty(default=0.0, min=0.0, max=1.0)
    #bpy.types.Object.MhaElbowPlant_L = BoolProperty(default=False)
    bpy.types.Object.MhaFingerControl_L = BoolProperty(default=False)
    bpy.types.Object.MhaLegHinge_L = BoolProperty(default=False)
    bpy.types.Object.MhaLegIkToAnkle_L = BoolProperty(default=False)
    bpy.types.Object.MhaLegIk_L = FloatProperty(default=0.0, min=0.0, max=1.0)

    bpy.types.Object.MhaArmHinge_R = BoolProperty(default=False)
    bpy.types.Object.MhaArmIk_R = FloatProperty(default=0.0, min=0.0, max=1.0)
    #bpy.types.Object.MhaElbowPlant_R = BoolProperty(default=False)
    bpy.types.Object.MhaFingerControl_R = BoolProperty(default=False)
    bpy.types.Object.MhaLegHinge_R = BoolProperty(default=False)
    bpy.types.Object.MhaLegIkToAnkle_R = BoolProperty(default=False)
    bpy.types.Object.MhaLegIk_R = FloatProperty(default=0.0, min=0.0, max=1.0)

    bpy.types.Scene.MhxHairColor = import_props.HairColorProperty
    bpy.types.Scene.MhxMinHairLength = IntProperty(default=10, min=4, max=40)
    bpy.types.Scene.MhxMinHairOrientation = FloatProperty(default=0.6, min=0.0, max=1.0)
    bpy.types.Scene.MhxHairKeySeparation = FloatProperty(default=0.2, min=0.001, max=10.0)

    bpy.types.Scene.MhxUseDeflector = BoolProperty(name="Add Deflector", description="Add deflector", default=False)
    bpy.types.Scene.MhxUseHairDynamics = BoolProperty(name="Hair Dynamics", description="Add dynamics to hair", default=False)

    bpy.types.Scene.MhxUseConservativeMasks = BoolProperty(name="Conservative Masks", description="Only delete faces with two delete-verts", default=True)
    bpy.types.Scene.MhxDesignHuman = StringProperty(default="None")

    bone_drivers.initialize()
    drivers.initialize()
    faceshift.initialize()
    fkik.initialize()
    hair.initialize()
    hide.initialize()
    importer.initialize()
    layers.initialize()
    materials.initialize()
    merge.initialize()
    proxy.initialize()
    shaders.initialize()
    shapekeys.initialize()
    #varia.initialize()
    visemes.initialize()
    armature.rigify.initialize()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bone_drivers.uninitialize()
    drivers.uninitialize()
    faceshift.uninitialize()
    fkik.uninitialize()
    hair.uninitialize()
    hide.uninitialize()
    importer.uninitialize()
    layers.uninitialize()
    materials.uninitialize()
    merge.uninitialize()
    proxy.uninitialize()
    shaders.uninitialize()
    shapekeys.uninitialize()
    #varia.uninitialize()
    visemes.uninitialize()
    armature.rigify.uninitialize()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()

print("MHX2 successfully (re)loaded")
