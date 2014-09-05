# ##### BEGIN GPL LICENSE BLOCK #####
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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) Thomas Larsson 2014


"""
Abstract

"""

import bpy
from .utils import *
from .hm8 import *

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def buildGeometry(mhGeo, mats, rig, parser, scn, cfg, useSeedMesh):
    if useSeedMesh:
        ob = buildMesh(mhGeo, mhGeo["seed_mesh"], scn, cfg, True)
        ob.MhxSeedMesh = True
    else:
        ob = buildMesh(mhGeo, mhGeo["mesh"], scn, cfg, False)
        ob.MhxSeedMesh = False

    if cfg.useOverrideRig:
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

    mat = mats[mhGeo["material"]]
    ob.data.materials.append(mat)
    return ob


def buildMesh(mhGeo, mhMesh, scn, cfg, useSeedMesh):
    if mhGeo["human"] and useSeedMesh:
        gname = ("%s:Body" % mhGeo["name"].split(':',1)[0])
    else:
        gname = mhGeo["name"]

    me = bpy.data.meshes.new(gname)
    scale,offset = getScaleOffset(mhGeo, cfg)
    verts = [scale*zup(co)+offset for co in mhMesh["vertices"]]

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


def getScaleOffset(struct, cfg):
    if cfg.useHelpers:
        scale = struct["scale"]
    else:
        scale = 1
    if cfg.useOffset:
        offset = zup(struct["offset"])
    else:
        offset = Vector((0,0,0))
    return scale,offset

