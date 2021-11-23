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


"""
Abstract

Postprocessing of rigify rig

"""

import bpy
import os
from bpy.props import *
from ..error import *
from .utils import *

if bpy.app.version < (2, 79, 0):
    # Blender 2.78 and before
    Renames = [
        ("chest", "chest-0"),
        ("chest-1", "chest"),
        ("spine", "spine-0"),
        ("spine-1", "spine"),
    ]

    Extras = [
        ("spine-0", "hips", "spine"),
        ("chest-0", "spine", "chest"),
        ("neck-1", "neck", "head"),
    ]

    Parents = {
        "clavicle.L" : "ORG-chest",
        "clavicle.R" : "ORG-chest",
        "shoulder.L" : "clavicle.L",
        "shoulder.R" : "clavicle.R",
        "ORG-shoulder.L" : "clavicle.L",
        "ORG-shoulder.R" : "clavicle.R",
    }

    def deleteHead(meta):
        return

else:
    # Blender 2.79 and later
    Renames = [
        ("spine", "spine.001"),
        ("hips", "spine"),
        ("spine-1", "spine.002"),
        ("chest", "spine.003"),
        ("chest-1", "spine.004"),
        ("neck", "spine.005"),
        #("neck-1", "spine.005"),
        ("head", "spine.006"),
    ]

    Extras = [
        #("spine-0", "hips", "spine"),
        #("chest-0", "spine", "chest"),
        ("neck-1", "spine.005", "spine.006"),
    ]

    Parents = {
        "clavicle.L" : "ORG-chest",
        "clavicle.R" : "ORG-chest",
        "shoulder.L" : "clavicle.L",
        "shoulder.R" : "clavicle.R",
        "ORG-shoulder.L" : "clavicle.L",
        "ORG-shoulder.R" : "clavicle.R",
    }

    def deleteHead(meta):
        head = meta.data.edit_bones["spine.006"]
        deleteChildren(head, meta)


def deleteChildren(eb, meta):
    for child in eb.children:
        deleteChildren(child, meta)
        meta.data.edit_bones.remove(child)


class RigifyBone:
    def __init__(self, eb):
        self.name = eb.name
        self.realname = None
        self.realname1 = None
        self.realname2 = None
        self.fkname = None
        self.ikname = None

        self.head = eb.head.copy()
        self.tail = eb.tail.copy()
        self.roll = eb.roll
        self.customShape = None
        self.lockLocation = None
        self.deform = eb.use_deform
        self.parent = None
        self.child = None
        self.connect = False
        self.original = False
        self.nodef = False

        if (eb.name in [
                "clavicle.L", "clavicle.R",
                "breast.L", "breast.R",
                "pelvis.L", "pelvis.R"]):
            self.layer = 2
            self.nodef = True
        elif eb.layers[1]:   # Face
            self.layer = 1
            self.nodef = True
        else:
            self.layer = 27  # Muscle

    def __repr__(self):
        return ("<RigifyBone %s %s %s %d %d>" % (self.name, self.realname, self.realname1, self.layer, self.nodef))


def checkRigifyEnabled(context):
    for addon in context.preferences.addons:
        if addon.module == "rigify":
            return True
    return False


def rigifyMhx(context, parser, taken={}):
    from collections import OrderedDict
    from ..error import MhxError

    print("Modifying MHX rig to Rigify")
    rig = context.object
    scn = context.scene
    if not(rig and rig.type == 'ARMATURE'):
        raise RuntimeError("Rigify: %s is neither an armature nor has armature parent" % ob)
    activateObject(context, rig)

    collection = None
    for col in bpy.data.collections:
        if rig.name in col.objects:
            collection = col
            break
    print("Collection: %s" % collection)

    # Rename some bones
    for bname,bname1 in Renames:
        b = rig.data.bones[bname]
        b.name = bname1

    # Setup info about MHX bones
    bones = OrderedDict()
    bpy.ops.object.mode_set(mode='EDIT')

    for eb in rig.data.edit_bones:
        bone = bones[eb.name] = RigifyBone(eb)
        if eb.parent:
            bone.parent = eb.parent.name
            bones[bone.parent].child = eb.name

    bpy.ops.object.mode_set(mode='OBJECT')

    for pb in rig.pose.bones:
        bone = bones[pb.name]
        bone.lockLocation = pb.lock_location
        if pb.custom_shape:
            bone.customShape = pb.custom_shape
            if pb.custom_shape.parent:
                pb.custom_shape.parent.parent = None
                pb.custom_shape.parent = None
            pb.custom_shape = None

    # Create metarig
    try:
        bpy.ops.object.armature_human_metarig_add()
    except AttributeError:
        raise MhxError("The Rigify add-on is not enabled. It is found under rigging.")
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    bpy.ops.object.scale_clear()
    bpy.ops.transform.resize(value=(100, 100, 100))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Fit metarig to default MHX rig
    meta = context.object
    bpy.ops.object.mode_set(mode='EDIT')
    deleteHead(meta)
    extra = []
    for bone in bones.values():
        try:
            eb = meta.data.edit_bones[bone.name]
        except KeyError:
            eb = None
        if eb:
            eb.head = bone.head
            eb.tail = bone.tail
            eb.roll = bone.roll
            bone.original = True

    for bname,pname,cname in Extras:
        extra.append(bname)
        bone = bones[bname]
        bone.original = True
        eb = meta.data.edit_bones.new(bname)
        eb.use_connect = False
        eb.head = bones[pname].tail
        eb.tail = bones[cname].head
        eb.roll = bone.roll
        parent = meta.data.edit_bones[pname]
        child = meta.data.edit_bones[cname]
        child.parent = eb
        child.head = bones[bone.child].head
        parent.tail = bones[bone.parent].tail
        eb.parent = parent
        eb.use_connect = True
        eb.layers = list(child.layers)

    # Add rigify properties to extra bones
    bpy.ops.object.mode_set(mode='OBJECT')
    for bname in extra:
        pb = meta.pose.bones[bname]
        pb["rigify_type"] = ""

    # Generate rigify rig
    bpy.ops.pose.rigify_generate()
    gen = context.object
    print("Generated", gen)
    deleteObject(context, meta)

    for bone in bones.values():
        if bone.original:
            setBoneName(bone, gen)

    # Add extra bone to generated rig
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in bones.values():
        if not bone.original:
            try:
                taken[bone.name]
                change = False
            except KeyError:
                change = True
            if ((not change) or
                (bone.name[0:4] == "DEF-") or
                bone.nodef):
                bone.realname = bone.name
            elif bone.deform:
                bone.realname = "DEF-" + bone.name
            else:
                bone.realname = "MCH-" + bone.name

            eb = gen.data.edit_bones.new(bone.realname)
            eb.head = bone.head
            eb.tail = bone.tail
            eb.roll = bone.roll
            eb.use_deform = bone.deform
            if bone.parent:
                parent = bones[bone.parent]
                if parent.realname:
                    eb.parent = gen.data.edit_bones[parent.realname]
                elif parent.realname1:
                    eb.parent = gen.data.edit_bones[parent.realname1]
                else:
                    print(bone)

            eb.use_connect = (eb.parent != None and eb.parent.tail == eb.head)
            layers = 32*[False]
            if change:
                layers[bone.layer] = True
            else:
                layers[0] = True
            if bone.deform:
                layers[29] = True
            eb.layers = layers

    # Fix parents
    if "clavicle.L" in gen.data.edit_bones.keys():
        for bname in Parents.keys():
            eb = gen.data.edit_bones[bname]
            eb.parent = gen.data.edit_bones[Parents[bname]]

    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in bones.values():
        if not bone.original:
            pb = gen.pose.bones[bone.realname]
            db = rig.pose.bones[bone.name]
            pb.bone.hide_select = db.bone.hide_select
            pb.rotation_mode = db.rotation_mode
            pb.lock_location = bone.lockLocation
            if bone.customShape:
                pb.custom_shape = bone.customShape
            for cns1 in db.constraints:
                cns2 = pb.constraints.new(cns1.type)
                fixConstraint(cns1, cns2, gen, bones)

    # Rescale gizmos
    #from .build import rescaleGizmo
    #for bname in ["spine-0", "spine"]:
    #    pb = gen.pose.bones[bname]
    #    #pb.custom_shape = rescaleGizmo(pb.custom_shape, 3.0)

    # Add MHX properties
    for key in rig.keys():
        gen[key] = rig[key]

    # Copy MHX bone drivers
    if rig.animation_data:
        for fcu1 in rig.animation_data.drivers:
            rna,channel = fcu1.data_path.rsplit(".", 1)
            pb = mhxEval("gen.%s" % rna)
            fcu2 = pb.driver_add(channel, fcu1.array_index)
            copyDriver(fcu1, fcu2, gen)

    # Fix vertex groups
    vgrps = list(parser.vertexGroups.keys())
    vgrps.sort()
    #print("VG", vgrps)

    for gname,vgrp in list(parser.vertexGroups.items()):
        if gname[0:4] == "DEF-":
            gname = "DEF-" + rename(gname[4:])

        nname = None
        if gname in gen.data.bones.keys():
            continue
        elif gname[0:4] == "DEF-":
            if gname[4:] in gen.data.bones.keys():
                nname = gname[4:]
            else:
                words = gname.split(".")
                if len(words) == 3:
                    if words[1] == "01":
                        nname = ("%s.%s" % (words[0], words[2]))
                    elif words[1] == "02":
                        nname = ("%s.%s.001" % (words[0], words[2]))
            if nname in gen.data.bones.keys():
                parser.vertexGroups[nname] = vgrp
            else:
                nname = None
            del parser.vertexGroups[gname]
        if nname is None:
            print("Warning: missing vertex group %s" % gname)

    if collection:
        collection.objects.link(gen)

    # Parent widgets under empty
    empty = bpy.data.objects.new("Widgets", None)
    hidden = createHiddenCollection(context)
    hidden.objects.link(empty)
    putOnHiddenLayer(empty)
    empty.parent = gen
    for ob in getSceneObjects(context):
        if (ob.type == 'MESH' and
            ob.name[0:4] in ["WGT-", "GZM_"] and
            not ob.parent):
            ob.parent = empty
            #group.objects.link(ob)

    #Clean up
    setattr(gen, ShowXRay, True)
    setattr(gen, DrawType, 'WIRE')
    gen.MhxRigify = False
    name = rig.name
    deleteObject(context, rig)
    gen.name = name
    bpy.ops.object.mode_set(mode='POSE')
    print("MHX rig %s successfully rigified" % name)
    return gen


def fixRigifyMeshes(children):
    for ob in children:
        if ob.type == 'MESH':
            for bname,bname1 in Renames:
                for vgname in [bname, "DEF-" + bname]:
                    for vg in ob.vertex_groups:
                        if vg.name == vgname:
                            vg.name = "DEF-" + bname1

            '''
            if ob.data.animation_data:
                for fcu in ob.data.animation_data.drivers:
                    print(ob, fcu.data_path)
                    changeDriverTarget(fcu, gen)

            if ob.data.shape_keys and ob.data.shape_keys.animation_data:
                for fcu in ob.data.shape_keys.animation_data.drivers:
                    print(skey, fcu.data_path)
                    changeDriverTarget(fcu, gen)

            for mod in ob.modifiers:
                if mod.type == 'ARMATURE' and mod.object == rig:
                    mod.object = gen
            '''


def setBoneName(bone, gen):
    fkname = bone.name.replace(".", ".fk.")
    try:
        gen.data.bones[fkname]
        bone.fkname = fkname
        bone.ikname = fkname.replace(".fk.", ".ik")
    except KeyError:
        pass

    defname = "DEF-" + bone.name
    try:
        gen.data.bones[defname]
        bone.realname = defname
        return
    except KeyError:
        pass

    defname1 = "DEF-" + bone.name + ".01"
    try:
        gen.data.bones[defname1]
        bone.realname1 = defname1
        bone.realname2 = defname1.replace(".01.", ".02.")
        return
    except KeyError:
        pass

    defname1 = "DEF-" + bone.name.replace(".", ".01.")
    try:
        gen.data.bones[defname1]
        bone.realname1 = defname1
        bone.realname2 = defname1.replace(".01.", ".02")
        return
    except KeyError:
        pass

    try:
        gen.data.edit_bones[bone.name]
        bone.realname = bone.name
    except KeyError:
        pass


def fixConstraint(cns1, cns2, gen, bones):
    for key in dir(cns1):
        if ((key[0] != "_") and
            (key not in ["bl_rna", "type", "rna_type", "is_valid", "error_location", "error_rotation", "is_proxy_local"])):
            setattr(cns2, key, getattr(cns1, key))

    if hasattr(cns2, "target"):
        cns2.target = gen

    if cns1.type == 'STRETCH_TO':
        bone = bones[cns1.subtarget]
        if bone.realname:
            cns2.subtarget = bone.realname
            cns2.head_tail = cns1.head_tail
        elif not bone.realname1:
            raise RuntimeError("Cannot fix STRETCH_TO constraint for bone %s" % (bone))
        elif cns1.head_tail < 0.5:
            cns2.subtarget = bone.realname1
            cns2.head_tail = 2*cns1.head_tail
        else:
            cns2.subtarget = bone.realname2
            cns2.head_tail = 2*cns1.head_tail-1

    elif hasattr(cns1, "subtarget"):
        bone = bones[cns1.subtarget]
        if bone.realname is None:
            cns2.subtarget = bone.realname1
        else:
            cns2.subtarget = bone.realname


def copyDriver(fcu1, fcu2, id):
    drv1 = fcu1.driver
    drv2 = fcu2.driver

    for var1 in drv1.variables:
        var2 = drv2.variables.new()
        var2.name = var1.name
        var2.type = var1.type
        targ1 = var1.targets[0]
        targ2 = var2.targets[0]
        targ2.id = id
        targ2.data_path = targ1.data_path

    drv2.type = drv1.type
    drv2.expression = drv1.expression
    drv2.show_debug_info = drv1.show_debug_info


def changeDriverTarget(fcu, id):
    for var in fcu.driver.variables:
        targ = var.targets[0]
        targ.id = id


def rename(bname):
    for oname,nname in Renames:
        if bname == oname:
            return nname
    return bname

#------------------------------------------------------------------------
#   Finalize
#------------------------------------------------------------------------

def setParents(children, parent):
    for ob in children:
        ob.parent = parent
        for mod in ob.modifiers:
            if mod.type == 'ARMATURE':
                mod.object = parent

def listUsedVgroups(children):
    taken = {}
    for ob in children:
        if ob.type == 'MESH':
            for vg in ob.vertex_groups:
                taken[vg.name] = True
    return taken


class MHX_OT_MhxFinalizeRigify(bpy.types.Operator):
    bl_idname = "mhx2.finalize_rigify"
    bl_label = "Finalize Rigify"
    bl_description = "Finalize Rigify"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            children = list(context.object.children)
            setParents(children, None)
            taken = listUsedVgroups(children)
            gen = rigifyMhx(context, parser, taken)
            fixRigifyMeshes(children)
            setParents(children, gen)
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}

#----------------------------------------------------------
#   Initialize
#----------------------------------------------------------

classes = [
    MHX_OT_MhxFinalizeRigify,
]

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
