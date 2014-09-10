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

import os
import bpy
from bpy.props import *
from mathutils import Vector

from .drivers import *
from .utils import zup2

#------------------------------------------------------------------------
#   Setup shapekeys
#------------------------------------------------------------------------

def addShapeKeys(human, filename, proxies=[], proxyTypes=[]):
    from .load_json import loadJsonRelative
    from .proxy import proxifyTargets

    print("Setting up shapekeys")
    struct = loadJsonRelative(filename)
    scale = getScale(human.data.vertices, struct["sscale"])
    addTargets(human, struct["targets"], scale)

    for mhGeo,ob in proxies:
        mhProxy = mhGeo["proxy"]
        print(mhProxy["name"])
        if mhProxy["type"] in proxyTypes:
            ptargets = proxifyTargets(mhProxy, struct["targets"])
            addTargets(ob, ptargets, scale)


def addTargets(ob, targets, scale):
    targets = list(targets.items())
    targets.sort()
    if not ob.data.shape_keys:
        basic = ob.shape_key_add("Basic")
    else:
        basic = ob.data.shape_keys.key_blocks[0]

    for tname,data in targets:
        print(tname)
        skey = ob.shape_key_add(tname)
        skey.value = 0
        skey.slider_min = -0.5
        skey.slider_max = 1.5
        for v in ob.data.vertices:
            skey.data[v.index].co = v.co
        nVerts = len(ob.data.vertices)
        for vn,delta in data[:nVerts]:
            if vn >= nVerts:
                break
            skey.data[vn].co += zup2(delta, scale)


def getScale(verts, struct):
    print(struct)
    scale = Vector((1,1,1))
    for comp,idx in [("x",0), ("z",1), ("y",2)]:
        vn1,vn2,s0 = struct[comp]
        co1 = verts[vn1].co
        co2 = verts[vn2].co
        scale[idx] = abs((co2[idx] - co1[idx])/s0)
    return scale


class VIEW3D_OT_AddShapekeysButton(bpy.types.Operator):
    bl_idname = "mhx2.add_shapekeys"
    bl_label = "Add Shapekeys"
    bl_description = "Add shapekeys"
    bl_options = {'UNDO'}

    filename = StringProperty()

    @classmethod
    def poll(self, context):
        ob = context.object
        return ob and ob.MhxHuman and ob.MhxSeedMesh and not ob.MhxHasFaceShapes

    def execute(self, context):
        ob = context.object
        addShapeKeys(ob, self.filename)
        ob.MhxHasFaceShapes = True
        return{'FINISHED'}

#------------------------------------------------------------------------
#   Setup and remove drivers
#------------------------------------------------------------------------

def addShapeKeyDriversToAll(rig, meshes):
    if rig is None:
        print("No rig. Cannot add drivers")
        return
    success = False
    for ob in meshes:
        if hasShapekeys(ob):
            addShapekeyDrivers(rig, ob)
            ob.MhxShapekeyDrivers = True
            success = True
    if success:
        rig.MhxShapekeyDrivers = True
        print("Shapekey drivers added")
    else:
        print("No meshes with shapekeys")


def addShapekeyDrivers(rig, ob):
    if not ob.data.shape_keys:
        return
    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if skey.name != "Basis":
            sname = getShapekeyName(skey)
            rig[sname] = 0.0
            try:
                rnaUI = rig["_RNA_UI"]
            except KeyError:
                rnaUI = rig["_RNA_UI"] = {}
            rig["_RNA_UI"][sname] = {"min":skey.slider_min, "max":skey.slider_max}
            addDriver(rig, skey, "value", sname, [], "x", False)


def getShapekeyName(skey):
    if skey.name[0:3] == "Mhs":
        return skey.name
    else:
        return "Mhs"+skey.name


def hasShapekeys(ob):
    if (ob.type != 'MESH' or
        ob.data.shape_keys is None):
        return False
    for skey in ob.data.shape_keys.key_blocks:
        if skey.name != "Basis":
            return True
    return False


class VIEW3D_OT_AddShapekeyDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.add_shapekey_drivers"
    bl_label = "Add Shapekey Drivers"
    bl_description = "Control shapekeys with rig properties. For file linking."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and
                rig.type == 'ARMATURE' and
                not rig.MhxShapekeyDrivers and
                not rig.MhxFacePanel
               )

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        initRnaProperties(rig)
        addShapeKeyDriversToAll(rig, meshes)
        return{'FINISHED'}


def removeShapekeyDrivers(ob, rig):
    if not ob.data.shape_keys:
        return
    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if skey.name != "Basis":
            sname = getShapekeyName(skey)
            skey.driver_remove("value")
            deleteRigProperty(rig, sname)


class VIEW3D_OT_MhxRemoveShapekeyDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.remove_shapekey_drivers"
    bl_label = "Remove Shapekey Drivers"
    bl_description = "Remove ability to control shapekeys from rig property"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxShapekeyDrivers)

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        for ob in meshes:
            removeShapekeyDrivers(ob, rig)
            ob.MhxShapekeyDrivers = False
        if context.object == rig:
            rig.MhxShapekeyDrivers = False
        return{'FINISHED'}

#------------------------------------------------------------------------
#   Prettifying
#------------------------------------------------------------------------

class VIEW3D_OT_MhxPrettifyButton(bpy.types.Operator):
    bl_idname = "mhx2.prettify_visibility"
    bl_label = "Prettify Visibility Panel"
    bl_description = "Prettify visibility panel"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,_meshes = getRigMeshes(context)
        for prop in rig.keys():
            if prop[0:3] == "Mhh":
                setattr(bpy.types.Object, prop, BoolProperty(default=True))
        return{'FINISHED'}

