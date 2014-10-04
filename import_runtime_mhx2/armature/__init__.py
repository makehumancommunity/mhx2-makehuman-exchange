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
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

if "bpy" in locals():
    print("Reloading MHX2 armature")
    import imp
    imp.reload(flags)
    imp.reload(utils)
    imp.reload(rig_joints)
    imp.reload(rig_bones)
    imp.reload(rig_muscle)
    imp.reload(rig_face)
    imp.reload(rig_control)
    imp.reload(rig_merge)
    imp.reload(rig_panel)
    imp.reload(rig_rigify)
    imp.reload(parser)
    imp.reload(constraints)
    imp.reload(rigify)
else:
    print("Loading MHX2 armature")
    from . import flags
    from . import utils
    from . import rig_joints
    from . import rig_bones
    from . import rig_muscle
    from . import rig_face
    from . import rig_control
    from . import rig_merge
    from . import rig_panel
    from . import rig_rigify
    from . import parser
    from . import constraints
    from . import rigify

import bpy
from bpy.props import *
from ..utils import *
from .flags import *


def buildRig(mhHuman, cfg, context):
    from .parser import Parser


    scn = context.scene
    parser = Parser(mhHuman, cfg)
    parser.setup()

    rname = mhHuman["name"].split(":")[0]
    amt = bpy.data.armatures.new(rname)
    rig = bpy.data.objects.new(rname, amt)
    amt.draw_type = 'STICK'
    rig.draw_type = 'WIRE'
    rig.show_x_ray = True
    rig.data.layers = getLayers(parser.visibleLayers)
    scn.objects.link(rig)
    scn.objects.active = rig

    offset = Vector((0,0,0))

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in parser.bones.values():
        eb = amt.edit_bones.new(bone.name)
        eb.head = zup(bone.head)+offset
        eb.tail = zup(bone.tail)+offset
        try:
            eb.roll = bone.roll
        except:
            print("Illegal roll", bone.name, bone.roll)

        if cfg.useMhx:
            eb.layers = getLayers(bone.layers)
        elif cfg.useRigify and bone.layers & (L_PANEL|L_HEAD):
            eb.layers = 10*[False] + [True] + 21*[False]

    for bone in parser.bones.values():
        eb = amt.edit_bones[bone.name]
        if bone.parent:
            eb.parent = amt.edit_bones[bone.parent]
        elif parser.master and bone.name != parser.master:
            eb.parent = amt.edit_bones[parser.master]
        eb.use_connect = bone.conn

    bpy.ops.object.mode_set(mode='POSE')

    for bone in parser.bones.values():
        b = amt.bones[bone.name]
        b.use_deform = bone.deform
        b.use_inherit_scale = bone.scale
        b.show_wire = bone.wire
        b.hide_select = bone.restr

        pb = rig.pose.bones[bone.name]
        pb.lock_location = [bool(i) for i in bone.lockLocation]
        pb.lock_rotation = [bool(i) for i in bone.lockRotation]
        pb.lock_scale = [bool(i) for i in bone.lockScale]

    if parser.boneGroups:
        for bgname,theme,layer in parser.boneGroups:
            bpy.ops.pose.group_add()
            bgrp = rig.pose.bone_groups.active
            bgrp.name = bgname
            bgrp.color_set = theme
            for bone in parser.bones.values():
                if bone.layers & layer != 0:
                    pb = rig.pose.bones[bone.name]
                    pb.bone_group = bgrp

    for bname,constraints in parser.constraints.items():
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            print("No such bone:", bname)
            continue
        for cns in constraints:
            cns.build(pb, rig, parser)

    if len(parser.gizmos) > 0:
        empty = bpy.data.objects.new("%s:Gizmos" % rname, None)
        scn.objects.link(empty)
        empty.parent = rig
        empty.layers = 19*[False] + [True]

        gizmos = {}
        for gname,mhGizmo in parser.gizmos.items():
            gizmo = gizmos[gname] = addGizmo(gname, mhGizmo, scn)
            gizmo.parent = empty

        for bname,gname in parser.customShapes.items():
            if gname:
                try:
                    pb = rig.pose.bones[bname]
                except KeyError:
                    print("Missing bone %s" % bname)
                    continue
                pb.custom_shape = gizmos[gname]

    for key,data in cfg.properties.items():
        default = data["default"]
        desc = data["description"]
        if data["type"] == "float":
            prop = FloatProperty(default=default, description=desc)
        elif data["type"] == "int":
            prop = IntProperty(default=default, description=desc)
        elif data["type"] == "bool":
            prop = BoolProperty(default=default, description=desc)
        else:
            raise RuntimeError("Unknown property type: %s" % data["type"])
        setattr(bpy.types.Object, key, prop)
        rig[key] = default

    addPropDrivers(rig, parser.lrPropDrivers, ".L", "Mha")
    addPropDrivers(rig, parser.lrPropDrivers, ".R", "Mha")
    addPropDrivers(rig, parser.propDrivers, "", "Mha")

    bpy.ops.object.mode_set(mode='EDIT')
    # Rename bones according to config.
    # Vertex groups already renamed by parser.
    # Don't need to worry about deform prefix, because
    # not used by such rigs
    for bname,nname in cfg.bones.items():
        eb = amt.edit_bones[bname]
        eb.name = nname

    bpy.ops.object.mode_set(mode='OBJECT')

    if cfg.useRigify:
        from .rigify import rigifyMhx
        rig = rigifyMhx(context)

    rig.MhxRig = cfg.rigType
    rig["MhxVersion"] = 20
    rig["MhaRotationLimits"] = cfg.useRotationLimits
    rig.MhxFacePanel = cfg.useFacePanel
    return rig, parser


def getLayers(num):
    mask = 1
    layers = []
    for n in range(32):
        layers.append( (mask & num != 0) )
        mask <<= 1
    return layers


def addPropDrivers(rig, drvlist, suffix, prefix):
    from ..drivers import addDriver

    for drv in drvlist:
        bname,cname,data,expr = drv
        bname = "%s%s" % (bname, suffix)
        data = [(("%s%s%s" % (prefix, prop, suffix)).replace(".","_"), 1) for prop in data]
        pb = rig.pose.bones[bname]
        cns = pb.constraints[cname]
        addDriver(rig, cns, "influence", None, data, expr, False)


def addGizmo(gname, mhGizmo, scn):
    me = bpy.data.meshes.new(gname)
    me.from_pydata(mhGizmo["verts"], mhGizmo["edges"], [])
    ob = bpy.data.objects.new(gname, me)
    scn.objects.link(ob)
    ob.layers = 19*[False] + [True]
    if "subsurf" in mhGizmo.keys() and mhGizmo["subsurf"]:
        mod = ob.modifiers.new("Subsurf", 'SUBSURF')
    return ob



print("MHX2 armature loaded")
