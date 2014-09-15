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

import bpy
import os
import time
import math
import mathutils
from mathutils import Vector, Matrix, Quaternion
from bpy.props import *
from .hm8 import *
from .error import *
from .utils import *

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def importMhx2File(filepath, cfg, context):
    from .load_json import loadJson

    filepath = os.path.expanduser(filepath)
    cfg.folder = os.path.dirname(filepath)
    if os.path.splitext(filepath)[1].lower() != ".mhx2":
        print("Error: Not a mhx2 file: %s" % filepath.encode('utf-8', 'strict'))
        return
    print( "Opening MHX2 file %s " % filepath.encode('utf-8', 'strict') )

    time1 = time.clock()
    struct = loadJson(filepath)
    build(struct, cfg, context)
    time2 = time.clock()
    print("File %s loaded in %g s" % (filepath, time2-time1))


def build(struct, cfg, context):
    from .armature import buildRig
    from .armature.rigify import checkRigifyEnabled
    from .materials import buildMaterial
    from .geometries import buildGeometry, getScaleOffset

    scn = context.scene

    if (cfg.useOverride and
        cfg.rigType == 'RIGIFY' and
        not checkRigifyEnabled(context)):
        pass
        raise MhxError("The Rigify add-on is not enabled. It is found under rigging.")

    mats = {}
    for mhMaterial in struct["materials"]:
        mname,mat = buildMaterial(mhMaterial, scn, cfg)
        mats[mname] = mat

    parser = None
    rig = None
    print(cfg)
    for mhGeo in struct["geometries"]:
        if mhGeo["human"]:
            mhHuman = mhGeo
            setMhHuman(mhHuman)
            break
    if cfg.useOverride and cfg.useRig:
        rig,parser = buildRig(mhHuman, cfg, context)
    elif "skeleton" in struct.keys():
        rig = buildSkeleton(struct["skeleton"], scn, cfg)
    if rig:
        rig.MhxScale = mhHuman["scale"]
        rig.MhxOffset = str(list(zup(mhHuman["offset"])))

    human = None
    proxies = []
    proxy = None
    for mhGeo in struct["geometries"]:
        if "proxy" in mhGeo.keys():
            mhProxy = mhGeo["proxy"]
            if mhGeo["human"]:
                if cfg.useHelpers:
                    if cfg.useHumanType != 'BASE':
                        proxy = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, False, "proxy_seed_mesh")
                        proxy.MhxHuman = True
                    if cfg.useHumanType != 'PROXY':
                        human = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, True, "seed_mesh")
                        human.MhxHuman = True
                else:
                    proxy = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, False, "mesh")
                    proxy.MhxHuman = True
                if proxy:
                    proxies.append((mhGeo, proxy))
            else:
                ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.useHelpers)
                proxies.append((mhGeo, ob))
        elif mhGeo["human"]:
            human = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.useHelpers)
            human.MhxHuman = True

    if cfg.genitalia != "NONE":
        from .proxy import addProxy
        filepath = os.path.join("data/hm8/genitalia", cfg.genitalia.lower() + ".json")
        print("Adding genitalia:", filepath)
        mhGeo,sscale = addProxy(filepath, mhHuman)
        ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.useHelpers)
        proxies.append((mhGeo, ob))
        if "targets" in mhGeo.keys():
            from .shapekeys import addTargets
            addTargets(ob, mhGeo["targets"], sscale)

    if cfg.hairType != "NONE":
        from .proxy import getHairCoordinates
        folder = os.path.dirname(__file__)
        filepath = os.path.join(folder, "data/hm8/hair", cfg.hairType)
        hair,hcoords = getHairCoordinates(mhHuman, filepath)

    if cfg.useFaceShapes:
        from .shapekeys import addShapeKeys
        path = "data/hm8/faceshapes/faceshapes.json"
        proxyTypes = ["Proxymeshes", "Eyebrows", "Eyelashes", "Teeth", "Tongue"]
        addShapeKeys(human, path, mhHuman=mhHuman, proxies=proxies, proxyTypes=proxyTypes)

        if cfg.useFaceDrivers:
            from .shapekeys import addShapeKeyDriversToAll
            meshes = [human] + [ob for (_,ob) in proxies]
            addShapeKeyDriversToAll(rig, meshes)
        elif parser and parser.boneDrivers:
            from .drivers import addBoneShapeDrivers
            addBoneShapeDrivers(rig, human, parser.boneDrivers, proxies=proxies, proxyTypes=proxyTypes)

    if cfg.useHelpers:
        proxyTypes = ["Proxymeshes", "Genitals"]
        addMasks(human, proxies, proxyTypes=proxyTypes)

    if cfg.deleteHelpers:
        deleteHelpers(human, scn)

    gname = mhHuman["name"].split(":",1)[0]
    grp = bpy.data.groups.new(gname)
    if rig:
        grp.objects.link(rig)
    if human:
        grp.objects.link(human)
    for _,ob in proxies:
        grp.objects.link(ob)

    if cfg.mergeBodyParts:
        from .merge import mergeBodyParts
        proxyTypes = ["Eyes", "Eyebrows", "Eyelashes", "Teeth", "Tongue", "Genitals"]
        if cfg.mergeMaxType == 'HAIR':
            proxyTypes += ['Hair']
        if cfg.mergeMaxType == 'CLOTHES':
            proxyTypes += ['Hair', 'Clothes']
        if proxy and cfg.mergeToProxy:
            mergeBodyParts(proxy, proxies, scn, proxyTypes=proxyTypes)
        else:
            mergeBodyParts(human, proxies, scn, proxyTypes=proxyTypes)

    if cfg.hairType != "NONE":
        from .proxy import addHair
        scn.objects.active = human
        addHair(human, hair, hcoords)

    if rig:
        scn.objects.active = rig
        bpy.ops.object.mode_set(mode='POSE')
    elif human:
        scn.objects.active = human
        bpy.ops.object.mode_set(mode='OBJECT')
    elif proxy:
        scn.objects.active = proxy
        bpy.ops.object.mode_set(mode='OBJECT')


def buildSkeleton(mhSkel, scn, cfg):
    from .geometries import getScaleOffset

    rname = mhSkel["name"]
    amt = bpy.data.armatures.new(rname)
    rig = bpy.data.objects.new(rname, amt)
    amt.draw_type = 'STICK'
    rig.show_x_ray = True
    scn.objects.link(rig)
    scn.objects.active = rig

    scale,offset = getScaleOffset(mhSkel, cfg, True)
    bpy.ops.object.mode_set(mode='EDIT')
    for mhBone in mhSkel["bones"]:
        eb = amt.edit_bones.new(mhBone["name"])
        eb.head = zup(mhBone["head"])+offset
        eb.tail = zup(mhBone["tail"])+offset
        eb.roll = mhBone["roll"]
        if "parent" in mhBone.keys():
            eb.parent = amt.edit_bones[mhBone["parent"]]
        if mhBone["name"] == "levator02.L":
            rig.MhxFaceRig = True

    bpy.ops.object.mode_set(mode='OBJECT')
    return rig


def addMasks(human, proxies, proxyTypes=[]):
    from .proxy import proxifyMask

    for mhGeo,ob in proxies:
        mhProxy = mhGeo["proxy"]
        vnums = [vn for vn,delete in enumerate(mhProxy["delete_verts"]) if delete]
        #pname = mhProxy["name"]
        pname = getProxyName(ob)
        if human:
            addMask(human, vnums, pname)
        for mhGeo1,ob1 in proxies:
            if ob == ob1:
                continue
            mhProxy1 = mhGeo1["proxy"]
            if mhProxy1["type"] in proxyTypes:
                pvnums = proxifyMask(mhProxy1, vnums)
                if pvnums:
                    addMask(ob1, pvnums, pname)


def addMask(ob, vnums, pname):
    if vnums:
        mod = ob.modifiers.new("Mask:%s" % pname, 'MASK')
        vgrp = ob.vertex_groups.new("Delete:%s" % pname)
        mod.vertex_group = vgrp.name
        mod.invert_vertex_group = True
        for vn in vnums:
            vgrp.add([vn], 1, 'REPLACE')


def deleteHelpers(human, scn):
    if human is None:
        return
    scn.objects.active = human
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for vn in range(NBodyVerts, NTotalVerts):
        human.data.vertices[vn].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')

