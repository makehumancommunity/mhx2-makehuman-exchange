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
from .utils import *
from .hm8 import *

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def buildGeometry(mhGeo, mats, rig, parser, scn, cfg, useSeedMesh, meshType=None):
    if meshType is None:
        if useSeedMesh:
            meshType = "seed_mesh"
        else:
            meshType = "mesh"

    ob = buildMesh(mhGeo, mhGeo[meshType], scn, cfg, useSeedMesh)
    ob.MhxSeedMesh = useSeedMesh
    ob.MhxUuid = mhGeo["uuid"]

    if cfg.useOverride and cfg.useRig:
        if "proxy" in mhGeo.keys():
            mhProxy = mhGeo["proxy"]
            if mhGeo["human"] and useSeedMesh:
                vgrps = parser.vertexGroups
            else:
                from .proxy import proxifyVertexGroups
                vgrps = proxifyVertexGroups(mhProxy, parser.vertexGroups)
        else:
            vgrps = parser.vertexGroups
        buildVertexGroups(vgrps, ob, rig)
    elif ("weights" in mhGeo.keys() and
        not cfg.useHelpers and
        rig):
        buildVertexGroups(mhGeo["weights"], ob, rig)

    if rig:
        ob.parent = rig
        ob.lock_location = (True,True,True)
        ob.lock_rotation = (True,True,True)
        ob.lock_scale = (True,True,True)

    mat = mats[mhGeo["material"]]
    ob.data.materials.append(mat)
    return ob


def buildMesh(mhGeo, mhMesh, scn, cfg, useSeedMesh):
    print("BUILD", mhGeo["name"])
    if mhGeo["human"] and useSeedMesh:
        gname = ("%s:Body" % mhGeo["name"].split(':',1)[0])
    else:
        gname = mhGeo["name"]
    scale,offset = getScaleOffset(mhGeo, cfg, useSeedMesh)
    verts = [scale*zup(co)+offset for co in mhMesh["vertices"]]
    ob = addMeshToScene(verts, gname, mhMesh, scn)
    ob.MhxScale = mhGeo["scale"]
    ob.MhxOffset = str(list(zup(mhGeo["offset"])))
    return ob


def addMeshToScene(verts, gname, mhMesh, scn):
    me = bpy.data.meshes.new(gname)
    try:
        faces = mhMesh["faces"]
        edges = []
    except KeyError:
        edges = mhMesh["edges"]
        faces = []
    me.from_pydata(verts, edges, faces)

    for f in me.polygons:
        f.use_smooth = True

    uvtex = me.uv_textures.new()
    uvlayer = me.uv_layers.active
    uvcoords = mhMesh["uv_coordinates"]
    n = 0
    for f in mhMesh["uv_faces"]:
        for vn in f:
            uvlayer.data[n].uv = uvcoords[vn]
            n += 1

    ob = bpy.data.objects.new(gname, me)
    scn.objects.link(ob)
    return ob


def buildVertexGroups(vweights, ob, rig):
    mod = ob.modifiers.new('ARMATURE', 'ARMATURE')
    mod.use_vertex_groups = True
    mod.use_bone_envelopes = False
    mod.object = rig

    for vgname,data in vweights.items():
        vgrp = ob.vertex_groups.new(vgname)
        for vn,w in data:
            vgrp.add([vn], w, 'REPLACE')


def getScaleOffset(struct, cfg, useSeedMesh):
    if useSeedMesh:
        scale = struct["scale"]
    else:
        scale = 1
    if cfg.useOffset:
        offset = zup(struct["offset"])
    else:
        offset = Vector((0,0,0))
    return scale,offset

