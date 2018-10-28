# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014-2018
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
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import time
import math
import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector, Matrix, Quaternion

from .hm8 import *
from .error import *
from .utils import *

LowestVersion = 22
HighestVersion = 49

# ---------------------------------------------------------------------
#   Properties
# ---------------------------------------------------------------------

HairColorProperty = FloatVectorProperty(
    name = "Hair Color",
    subtype = "COLOR",
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.15, 0.03, 0.005, 1.0)
    )

UseMaskProperty = EnumProperty(
    items = [
        ('IGNORE', "Ignore", "Ignore masks"),
        ('APPLY', "Apply", "Apply masks (delete vertices permanently)"),
        ('MODIFIER', "Modifier", "Create mask modifier"),
    ],
    name = "Masks",
    description = "How to deal with masks",
    default = 'MODIFIER')

UseHumanTypeProperty = EnumProperty(
    items = [
        ('BASE', "Base", "Base mesh"),
        ('PROXY', "Proxy", "Exported topology (if exists)"),
        ('BOTH', "Both", "Both base mesh and proxy mesh"),
    ],
    name = "Import Human Type",
    description = "Human types to be imported",
    default = 'BOTH')

MergeMaxTypeProperty = EnumProperty(
    items = [
        ('BODY', "Body", "Merge up to body"),
        ('HAIR', "Hair", "Merge up to hair"),
        ('CLOTHES', "Clothes", "Merge all"),
    ],
    name = "Maximum Merge Type",
    description = "Maximum type to merge",
    default = 'BODY')

def getRigTypeItems():
    rigTypes = []
    folder = os.path.dirname(__file__)
    for file in os.listdir(os.path.join(folder, "armature/data/rigs")):
        fname = os.path.splitext(file)[0]
        if fname == "mhx":
            mhx = ("MHX", "MHX", "An advanced control rig")
        elif fname == "exported_mhx":
            exp_mhx = ("EXPORTED_MHX", "Exported MHX", "MHX rig based on exported deform rig")
        elif fname == "rigify":
            rigify = ("RIGIFY", "Rigify", "Modified Rigify rig")
        elif fname == "exported_rigify":
            exp_rigify = ("EXPORTED_RIGIFY", "Exported Rigify", "Rigify rig based on exported deform rig")
        else:
            entry = (fname.upper(), fname.capitalize(), "%s-compatible rig" % fname.capitalize())
            rigTypes.append(entry)
    rigTypes = [('EXPORTED', "Exported", "Use rig in mhx2 file"),
                exp_mhx, exp_rigify, mhx, rigify] + rigTypes
    return rigTypes

RigTypeProperty = EnumProperty(
    items = getRigTypeItems(),
    name = "Rig Type",
    description = "Rig type",
    default = 'EXPORTED')

GenitaliaProperty = EnumProperty(
    items = [
        ("NONE", "None", "None"),
        ("PENIS", "Male", "Male genitalia"),
        ("PENIS2", "Male 2", "Better male genitalia"),
        ("VULVA", "Female", "Female genitalia"),
        ("VULVA2", "Female 2", "Better female genitalia")
    ],
    name = "Genitalia",
    description = "Genitalia",
    default = 'NONE')

def getHairItems():
    hairItems = [("NONE", "None", "None")]
    folder = os.path.join(os.path.dirname(__file__), "data", "hm8", "hair")
    for file in os.listdir(folder):
        fname,ext = os.path.splitext(file)
        if ext == ".mxa":
            hairItems.append((file, fname, fname))
    return hairItems

HairTypeProperty = EnumProperty(
    items = getHairItems(),
    name = "Hair",
    description = "Hair",
    default = "NONE")

# ---------------------------------------------------------------------
#   Import class, for B2.7 and B2.8
# ---------------------------------------------------------------------

print("BPA", bpy.app.version)
if True or bpy.app.version < (2,80,0):
    print("OLD")
    class Mhx2Import(ImportHelper):
        filename_ext = ".mhx2"
        filter_glob = StringProperty(default="*.mhx2", options={'HIDDEN'})
        filepath = StringProperty(subtype='FILE_PATH')

        useHelpers = BoolProperty(name="Helper Geometry", description="Keep helper geometry", default=False)
        useOffset = BoolProperty(name="Offset", description="Add offset for feet on ground", default=True)
        useOverride = BoolProperty(name="Override Exported Data", description="Override rig and mesh definitions in mhx2 file", default=False)

        useCustomShapes = BoolProperty(name="Custom Shapes", description="Custom bone shapes", default=True)
        useFaceShapes = BoolProperty(name="Face Shapes", description="Face shapes", default=False)
        useFaceShapeDrivers = BoolProperty(name="Face Shape Drivers", description="Drive face shapes with rig properties", default=False)
        useFaceRigDrivers = BoolProperty(name="Face Rig Drivers", description="Drive face rig with rig properties", default=True)
        useFacePanel = BoolProperty(name="Face Panel", description="Face panel", default=False)
        useRig = BoolProperty(name="Add Rig", description="Add rig", default=True)
        finalizeRigify = BoolProperty(name="Finalize Rigify", description="If off, only load metarig. Press Finalize Rigify to complete rigification later", default=True)
        useRotationLimits = BoolProperty(name="Rotation Limits", description="Use rotation limits for MHX rig", default=True)
        useDeflector = BoolProperty(name="Add Deflector", description="Add deflector", default=False)
        useHairDynamics = BoolProperty(name="Hair Dynamics", description="Add dynamics to hair", default=False)
        useHairOnProxy = BoolProperty(name="Hair On Proxy", description="Add hair to proxy rather than base human", default=False)
        useConservativeMasks = BoolProperty(name="Conservative Masks", description="Only delete faces with two delete-verts", default=True)

        useSubsurf = BoolProperty(name="Subsurface", description="Add a subsurf modifier to all meshes", default=False)
        subsurfLevels = IntProperty(name="Levels", description="Subsurface levels (viewport)", default=0)
        subsurfRenderLevels = IntProperty(name=" Render Levels", description="Subsurface levels (render)", default=1)

        useMasks = UseMaskProperty,
        useHumanType = UseHumanTypeProperty,

        mergeBodyParts = BoolProperty(name="Merge Body Parts", description="Merge body parts", default=False)
        mergeToProxy = BoolProperty(name="Merge To Proxy", description="Merge body parts to proxy mesh is such exists", default=False)
        mergeMaxType = MergeMaxTypeProperty,

        rigType = RigTypeProperty,
        genitalia = GenitaliaProperty,
        usePenisRig = BoolProperty(name="Penis Rig", description="Add a penis rig", default=False)
        hairType = HairTypeProperty,
        hairColor = HairColorProperty

else:
    print("NEW")

# ---------------------------------------------------------------------
#   Import button
# ---------------------------------------------------------------------

class MHX_OT_Import(bpy.types.Operator, Mhx2Import):
    """Import from MHX2 file format (.mhx2)"""
    bl_idname = "import_scene.makehuman_mhx2"
    bl_description = 'Import from MHX2 file format (.mhx2)'
    bl_label = "Import MHX2"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        from .config import Config
        cfg = Config().fromSettings(self)
        try:
            importMhx2File(self.filepath, cfg, context)
        except MhxError:
            handleMhxError(context)

        if AutoWeight:
            scn = context.scene
            rig = scn.objects["Bar"]
            ob = scn.objects["Bar:Body"]
            ob.select = True
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "useOverride")
        if not self.useOverride:
            return

        layout.separator()
        layout.label(text="Import Human Type:")
        layout.prop(self, "useHumanType", expand=True)

        layout.prop(self, "useHelpers")
        layout.prop(self, "useOffset")
        layout.prop(self, "useFaceShapes")
        if (self.useFaceShapes and
            not self.useFacePanel):
            layout.prop(self, "useFaceShapeDrivers")

        layout.separator()
        box = layout.box()
        box.label(text="Subdivision surface")
        box.prop(self, "useSubsurf")
        if self.useSubsurf:
            box.prop(self, "subsurfLevels")
            box.prop(self, "subsurfRenderLevels")

        layout.separator()
        layout.label(text="Masking:")
        layout.prop(self, "useMasks", expand=True)
        layout.prop(self, "useConservativeMasks")

        layout.separator()
        box = layout.box()
        box.label(text="Merging")
        box.prop(self, "mergeBodyParts")
        if self.mergeBodyParts and self.useHumanType != 'BODY':
            box.prop(self, "mergeToProxy")
        if self.mergeBodyParts:
            box.prop(self, "mergeMaxType")

        layout.prop(self, "genitalia", text="Genitalia")

        layout.separator()
        box = layout.box()
        box.prop(self, "hairType")
        if self.hairType != 'NONE':
            box.prop(self, "hairColor")
            box.prop(self, "useHairOnProxy")
            box.prop(self, "useHairDynamics")
        box.prop(self, "useDeflector")

        layout.separator()
        box = layout.box()
        box.label(text="Rigging")
        box.prop(self, "useRig")
        if self.useRig:
            box.prop(self, "rigType")
            box.prop(self, "useCustomShapes")
            if self.rigType in ('MHX', 'EXPORTED_MHX'):
                box.prop(self, "useRotationLimits")
            #elif self.rigType in ('RIGIFY', 'EXPORTED_RIGIFY'):
            #    box.prop(self, "finalizeRigify")
            if self.useFaceShapes and not self.useFaceShapeDrivers:
                box.prop(self, "useFacePanel")
            if self.rigType[0:8] == 'EXPORTED':
                box.prop(self, "useFaceRigDrivers")
            if self.genitalia[0:5] == 'PENIS' and self.rigType[0:8] != 'EXPORTED':
                box.prop(self, "usePenisRig")

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def importMhx2File(filepath, cfg, context):
    filepath = os.path.expanduser(filepath)
    cfg.folder = os.path.dirname(filepath)
    struct, time1 = importMhx2Json(filepath)
    build(struct, cfg, context)
    time2 = time.clock()
    print("File %s loaded in %g s" % (filepath, time2-time1))


def importMhx2Json(filepath):
    from .load_json import loadJson

    if os.path.splitext(filepath)[1].lower() != ".mhx2":
        print("Error: Not a mhx2 file: %s" % filepath.encode('utf-8', 'strict'))
        return
    print( "Opening MHX2 file %s " % filepath.encode('utf-8', 'strict') )

    time1 = time.clock()
    struct = loadJson(filepath)

    try:
        vstring = struct["mhx2_version"]
    except KeyError:
        vstring = ""

    if vstring:
        high,low = vstring.split(".")
        fileVersion = 100*int(high) + int(low)
    else:
        fileVersion = 0

    if (fileVersion > HighestVersion or
        fileVersion < LowestVersion):
        raise MhxError(
            ("Incompatible MHX2 versions:\n" +
            "MHX2 file: %s\n" % vstring +
            "Must be between\n" +
            "0.%d and 0.%d" % (LowestVersion, HighestVersion))
            )

    return struct, time1


def build(struct, cfg, context):
    from .armature.build import buildRig
    from .armature.rigify import checkRigifyEnabled
    from .materials import buildMaterial
    from .geometries import buildGeometry, getScaleOffset
    from .proxy import setMhHuman

    scn = context.scene

    if (cfg.useOverride and
        cfg.rigType == 'RIGIFY' and
        cfg.finalizeRigify and
        not checkRigifyEnabled(context)):
        pass
        #raise MhxError("The Rigify add-on is not enabled. It is found under rigging.")

    mats = {}
    for mhMaterial in struct["materials"]:
        mname,mat = buildMaterial(mhMaterial, scn, cfg)
        mats[mname] = mat

    for mhGeo in struct["geometries"]:
        if mhGeo["human"]:
            mhHuman = mhGeo
            setMhHuman(mhHuman)
            scn.MhxDesignHuman = getMhHuman()["name"]

    parser = None
    rig = None
    if cfg.useOverride:
        if cfg.useRig:
            if cfg.rigType == 'EXPORTED':
                if "skeleton" in struct.keys():
                    mhSkel = struct["skeleton"]
                    rig = buildSkeleton(mhSkel, scn, cfg)
            elif cfg.rigType in ['EXPORTED_MHX', 'EXPORTED_RIGIFY']:
                from .armature.rerig import isDefaultRig
                if "skeleton" in struct.keys():
                    mhSkel = struct["skeleton"]
                    if isDefaultRig(mhSkel):
                        rig,parser = buildRig(mhHuman, mhSkel, cfg, context)
                    else:
                        print("Can only build %s rig if the Default rig (with or without toes) was exported from MakeHuman." % cfg.rigType)
                        rig = buildSkeleton(mhSkel, scn, cfg)
            else:
                rig,parser = buildRig(mhHuman, None, cfg, context)
    elif "skeleton" in struct.keys():
        mhSkel = struct["skeleton"]
        rig = buildSkeleton(mhSkel, scn, cfg)

    if rig:
        rig.MhxScale = mhHuman["scale"]
        rig.MhxOffset = str(list(zup(mhHuman["offset"])))
        if "levator02.L" in rig.data.bones.keys():
            rig.MhxFaceRig = True
    mhHuman["parser"] = parser

    human = None
    proxies = []
    proxy = None
    for mhGeo in struct["geometries"]:
        if "proxy" in mhGeo.keys():
            mhProxy = mhGeo["proxy"]
            if mhGeo["human"]:
                if cfg.useHelpers:
                    if cfg.useHumanType != 'BASE':
                        proxy = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, "proxy_seed_mesh")
                        proxy.MhxHuman = True
                    if cfg.useHumanType != 'PROXY':
                        human = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, "seed_mesh")
                        human.MhxHuman = True
                else:
                    proxy = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, "mesh")
                    proxy.MhxHuman = True
                if proxy:
                    proxies.append((mhGeo, proxy))
            elif mhProxy["type"] == "Hair" and cfg.hairType != 'NONE':
                pass
            elif mhProxy["type"] == "Genitals" and cfg.genitalia != 'NONE':
                pass
            else:
                ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.getMeshType())
                proxies.append((mhGeo, ob))
        elif mhGeo["human"]:
            human = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.getMeshType())
            human.MhxHuman = True

    if proxy:
        proxy.MhxUuid = mhHuman["uuid"]

    groupName = mhHuman["name"].split(":",1)[0]

    if cfg.useOverride and cfg.genitalia != "NONE":
        genitalia = addMeshProxy("genitalia", cfg.genitalia, mhHuman, mats, rig, parser, scn, cfg)
        proxies.append(genitalia)

    if cfg.useOverride and cfg.useDeflector:
        from .hair import makeDeflector
        deflHead = addMeshProxy("deflector", "deflector_head", mhHuman, mats, None, None, scn, cfg)
        makeDeflector(deflHead, rig, ["head"], cfg)
        proxies.append(deflHead)
        deflTorso = addMeshProxy("deflector", "deflector_torso", mhHuman, mats, None, None, scn, cfg)
        makeDeflector(deflTorso, rig, ["chest-1","chest"], cfg)
        proxies.append(deflTorso)

    if cfg.useOverride and cfg.useRigify and cfg.finalizeRigify and rig:
        from .armature.rigify import fixRigifyMeshes
        fixRigifyMeshes(rig.children)

    if cfg.useOverride and cfg.hairType != "NONE":
        from .proxy import getProxyCoordinates
        folder = os.path.dirname(__file__)
        filepath = os.path.join(folder, "data/hm8/hair", cfg.hairType)
        hair,hcoords,_scales = getProxyCoordinates(mhHuman, filepath)

    if cfg.useOverride and cfg.useFaceShapes:
        from .shapekeys import addShapeKeys
        path = "data/hm8/faceshapes/faceshapes.mxa"
        proxyTypes = ["Proxymeshes", "Eyebrows", "Eyelashes", "Teeth", "Tongue"]
        addShapeKeys(human, path, mhHuman=mhHuman, proxies=proxies, proxyTypes=proxyTypes)

        if cfg.useFaceShapeDrivers:
            from .shapekeys import addShapeKeyDriversToAll
            meshes = [human] + [ob for (_,ob) in proxies]
            addShapeKeyDriversToAll(rig, meshes, "Mhf")
        elif parser and parser.boneDrivers:
            from .drivers import addBoneShapeDrivers
            addBoneShapeDrivers(rig, human, parser.boneDrivers, proxies=proxies, proxyTypes=proxyTypes)

    deselectAll(human, proxies, scn)

    if cfg.useOverride and cfg.useHelpers:
        from .masks import addMasks, selectAllMaskVGroups
        proxyTypes = ["Proxymeshes", "Genitals"]
        if cfg.useMasks == 'MODIFIER':
            addMasks(mhHuman, human, proxies, proxyTypes, cfg.useConservativeMasks)
        elif cfg.useMasks == 'APPLY':
            addMasks(mhHuman, human, proxies, proxyTypes, cfg.useConservativeMasks)
            selectAllMaskVGroups(human, proxies)
        elif cfg.useMasks == 'IGNORE':
            pass

    if (cfg.useOverride and cfg.useRig and cfg.useFaceRigDrivers and
        cfg.rigType in ['EXPORTED_MHX', 'EXPORTED_RIGIFY']):
        from .armature.rerig import makeBonesPosable
        scn.objects.active = rig
        makeBonesPosable(rig, cfg.useMhx)

    if cfg.deleteHelpers:
        selectHelpers(human)

    if cfg.useOverride:
        deleteAllSelected(human, proxies, scn)

    grp = bpy.data.groups.new(groupName)
    if rig:
        grp.objects.link(rig)
    if human:
        grp.objects.link(human)
    for _,ob in proxies:
        grp.objects.link(ob)

    if cfg.useOverride and cfg.mergeBodyParts:
        from .merge import mergeBodyParts
        proxyTypes = ["Eyes", "Eyebrows", "Eyelashes", "Teeth", "Tongue", "Genitals"]
        if cfg.mergeMaxType == 'HAIR':
            proxyTypes += ['Hair']
        if cfg.mergeMaxType == 'CLOTHES':
            proxyTypes += ['Hair', 'Clothes']
        ob = getEffectiveHuman(human, proxy, cfg.mergeToProxy)
        if ob:
            mergeBodyParts(ob, proxies, scn, proxyTypes=proxyTypes)

    if cfg.useOverride and cfg.hairType != "NONE":
        from .hair import addHair
        ob = getEffectiveHuman(human, proxy, cfg.useHairOnProxy)
        if ob:
            reallySelect(ob, scn)
            addHair(ob, hair, hcoords, scn, cfg)

    if rig:
        reallySelect(rig, scn)
        bpy.ops.object.mode_set(mode='POSE')
    elif human:
        reallySelect(human, scn)
        bpy.ops.object.mode_set(mode='OBJECT')
    elif proxy:
        reallySelect(proxy, scn)
        bpy.ops.object.mode_set(mode='OBJECT')


def getEffectiveHuman(human, proxy, useProxy):
    if proxy and (useProxy or not human):
        return proxy
    elif human and (not useProxy or not proxy):
        return human
    else:
        return None


def addMeshProxy(type, pname, mhHuman, mats, rig, parser, scn, cfg):
    from .proxy import addProxy
    from .geometries import buildGeometry

    filepath = os.path.join("data/hm8/%s" % type, pname.lower() + ".mxa")
    print("Adding %s:" % pname, filepath)
    mhGeo,scales = addProxy(filepath, mhHuman, mats, scn, cfg)
    ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.getMeshType())
    ob.MhxScale = mhHuman["scale"]
    if "targets" in mhGeo.keys():
        from .shapekeys import addTargets
        addTargets(ob, mhGeo["targets"], scales)
    return mhGeo,ob


def buildSkeleton(mhSkel, scn, cfg):
    from .geometries import getScaleOffset
    from .bone_drivers import buildAnimation, buildExpressions

    rname = mhSkel["name"]
    amt = bpy.data.armatures.new(rname)
    rig = bpy.data.objects.new(rname, amt)
    amt.draw_type = 'STICK'
    rig.show_x_ray = True
    scn.objects.link(rig)
    reallySelect(rig, scn)

    scale,offset = getScaleOffset(mhSkel, cfg, True)
    bpy.ops.object.mode_set(mode='EDIT')
    for mhBone in mhSkel["bones"]:
        eb = amt.edit_bones.new(mhBone["name"])
        eb.head = zup(mhBone["head"])+offset
        eb.tail = zup(mhBone["tail"])+offset
        if "matrix" in mhBone.keys():
            mat = Matrix(mhBone["matrix"])
            nmat = Matrix((mat[0], -mat[2], mat[1])).to_3x3().to_4x4()
            nmat.col[3] = eb.matrix.col[3]
            eb.matrix = nmat
        else:
            eb.roll = mhBone["roll"]
        if "parent" in mhBone.keys():
            eb.parent = amt.edit_bones[mhBone["parent"]]

    bpy.ops.object.mode_set(mode='OBJECT')
    for mhBone in mhSkel["bones"]:
        pb = rig.pose.bones[mhBone["name"]]
        if pb.parent:
            pb.lock_location = [True,True,True]

    rig.MhxRig = "Exported"
    buildExpressions(mhSkel, rig, scn, cfg)
    buildAnimation(mhSkel, rig, scn, offset, cfg)
    return rig

#------------------------------------------------------------------------
#   Selecting and deleting verts
#------------------------------------------------------------------------

def deselectAll(human, proxies, scn):
    if human:
        reallySelect(human, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
    for _,pxy in proxies:
        reallySelect(pxy, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')


def deleteAllSelected(human, proxies, scn):
    if human:
        reallySelect(human, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
    for _,pxy in proxies:
        reallySelect(pxy, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')


def selectHelpers(human):
    if human is None:
        return
    for vn in range(NBodyVerts, NTotalVerts):
        human.data.vertices[vn].select = True

#------------------------------------------------------------------------
#   Design human
#------------------------------------------------------------------------

def setDesignHuman(filepath, context):
    filepath = os.path.expanduser(filepath)
    struct, _time1 = importMhx2Json(filepath)
    for mhGeo in struct["geometries"]:
        if mhGeo["human"]:
            mhHuman = mhGeo
            setMhHuman(mhGeo)
            context.scene.MhxDesignHuman = getMhHuman()["name"]
            return
    raise MhxError("Unable to set design human")


class MHX_OT_SetDesignHuman(bpy.types.Operator, Mhx2Import):
    bl_idname = "mhx2.set_design_human"
    bl_label = "Set Design Human (.mhx2)"
    bl_description = "Load definition of human to be designed"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            setDesignHuman(self.properties.filepath, context)
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MHX_OT_ClearDesignHuman(bpy.types.Operator):
    bl_idname = "mhx2.clear_design_human"
    bl_label = "Clear Design Human"
    bl_description = "Clear definition of human to be designed"
    bl_options = {'UNDO'}

    def execute(self, context):
        mhHuman = None
        context.scene.MhxDesignHuman = "None"
        return{'FINISHED'}

#----------------------------------------------------------
#   Initialize
#----------------------------------------------------------

classes = [
    MHX_OT_Import,
    MHX_OT_SetDesignHuman,
    MHX_OT_ClearDesignHuman,
]

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)