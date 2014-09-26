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
    from .__init__ import bl_info

    filepath = os.path.expanduser(filepath)
    cfg.folder = os.path.dirname(filepath)
    if os.path.splitext(filepath)[1].lower() != ".mhx2":
        print("Error: Not a mhx2 file: %s" % filepath.encode('utf-8', 'strict'))
        return
    print( "Opening MHX2 file %s " % filepath.encode('utf-8', 'strict') )

    time1 = time.clock()
    struct = loadJson(filepath)

    print(bl_info["version"])
    impVersion = ("%d.%d" % bl_info["version"])
    try:
        fileVersion = struct["mhx2_version"]
    except KeyError:
        fileVersion = "Unknown"

    if impVersion != fileVersion:
        raise MhxError(
            ("Incompatible MHX2 versions:\n" +
            "Importer: %s\n" % impVersion +
            "MHX2 file: %s" % fileVersion)
            )

    build(struct, cfg, context)
    time2 = time.clock()
    print("File %s loaded in %g s" % (filepath, time2-time1))


def build(struct, cfg, context):
    from .armature import buildRig
    from .armature.rigify import checkRigifyEnabled
    from .materials import buildMaterial
    from .geometries import buildGeometry, getScaleOffset
    from .proxy import setMhHuman

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

    for mhGeo in struct["geometries"]:
        if mhGeo["human"]:
            mhHuman = mhGeo
            setMhHuman(mhHuman)

    parser = None
    rig = None
    if cfg.useOverride:
        if cfg.useRig:
            if cfg.rigType == 'EXPORTED':
                if "skeleton" in struct.keys():
                    rig = buildSkeleton(struct["skeleton"], scn, cfg)
            else:
                rig,parser = buildRig(mhHuman, cfg, context)
    elif "skeleton" in struct.keys():
        rig = buildSkeleton(struct["skeleton"], scn, cfg)
    if rig:
        rig.MhxScale = mhHuman["scale"]
        rig.MhxOffset = str(list(zup(mhHuman["offset"])))
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
            elif mhProxy["type"] == "Hair" and cfg.hairType != 'NONE':
                pass
            elif mhProxy["type"] == "Genitals" and cfg.genitalia != 'NONE':
                pass
            else:
                ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.useHelpers)
                proxies.append((mhGeo, ob))
        elif mhGeo["human"]:
            human = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.useHelpers)
            human.MhxHuman = True

    if proxy:
        proxy.MhxUuid = mhHuman["uuid"]

    groupName = mhHuman["name"].split(":",1)[0]

    if cfg.useOverride and cfg.genitalia != "NONE":
        genitalia = addMeshProxy("genitalia", cfg.genitalia, mhHuman, mats, rig, parser, scn, cfg)
        proxies.append(genitalia)

    if cfg.useOverride and cfg.useDeflector:
        deflector = addMeshProxy("deflector", "deflector", mhHuman, mats, rig, parser, scn, cfg)
        makeCollision(deflector[1])
        proxies.append(deflector)

    if cfg.useOverride and cfg.hairType != "NONE":
        from .proxy import getProxyCoordinates
        folder = os.path.dirname(__file__)
        filepath = os.path.join(folder, "data/hm8/hair", cfg.hairType)
        hair,hcoords = getProxyCoordinates(mhHuman, filepath)

    if cfg.useOverride and cfg.useFaceShapes:
        from .shapekeys import addShapeKeys
        path = "data/hm8/faceshapes/faceshapes.json"
        proxyTypes = ["Proxymeshes", "Eyebrows", "Eyelashes", "Teeth", "Tongue"]
        addShapeKeys(human, path, mhHuman=mhHuman, proxies=proxies, proxyTypes=proxyTypes)

        if cfg.useFaceDrivers:
            from .shapekeys import addShapeKeyDriversToAll
            meshes = [human] + [ob for (_,ob) in proxies]
            addShapeKeyDriversToAll(rig, meshes, "Mhf")
        elif parser and parser.boneDrivers:
            from .drivers import addBoneShapeDrivers
            addBoneShapeDrivers(rig, human, parser.boneDrivers, proxies=proxies, proxyTypes=proxyTypes)

    if cfg.useOverride and cfg.useHelpers:
        proxyTypes = ["Proxymeshes", "Genitals"]
        addMasks(human, proxies, proxyTypes=proxyTypes)

    if cfg.deleteHelpers:
        deleteHelpers(human, scn)

    grp = bpy.data.groups.new(groupName)
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
        ob = getEffectiveHuman(human, proxy, cfg.mergeToProxy)
        if ob:
            mergeBodyParts(ob, proxies, scn, proxyTypes=proxyTypes)

    if rig:
        scn.objects.active = rig
        bpy.ops.object.mode_set(mode='POSE')
    elif human:
        scn.objects.active = human
        bpy.ops.object.mode_set(mode='OBJECT')
    elif proxy:
        scn.objects.active = proxy
        bpy.ops.object.mode_set(mode='OBJECT')

    if cfg.hairType != "NONE":
        from .proxy import addHair
        ob = getEffectiveHuman(human, proxy, cfg.useHairOnProxy)
        if ob:
            scn.objects.active = ob
            addHair(ob, hair, hcoords, scn, cfg)


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

        filepath = os.path.join("data/hm8/%s" % type, pname.lower() + ".mhc2")
        print("Adding %s:" % pname, filepath)
        mhGeo,scales = addProxy(filepath, mhHuman, mats, scn, cfg)
        ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.useHelpers)
        if "targets" in mhGeo.keys():
            from .shapekeys import addTargets
            addTargets(ob, mhGeo["targets"], scales)
        return mhGeo,ob


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
        if "delete_verts" not in mhProxy.keys():
            continue
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
                if "proxy_seed_mesh" in mhGeo1.keys():
                    mhMesh = mhGeo1["proxy_seed_mesh"]
                else:
                    mhMesh = mhGeo1["seed_mesh"]
                pvnums = proxifyMask(mhProxy1, mhMesh, vnums)
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


def makeCollision(ob):
    ob.draw_type = 'WIRE'
    mod = ob.modifiers.new("Collision", 'COLLISION')
    print(ob.collision, ob.collision.use)


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

