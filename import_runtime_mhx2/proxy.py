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

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import *
from mathutils import Vector
from .error import *
from .utils import *
from .hm8 import *
from .hair import isHairStruct

# ---------------------------------------------------------------------
#   Add proxy
# ---------------------------------------------------------------------

def addProxy(filepath, mhHuman, mats, scn, cfg):
    from .load_json import loadJsonRelative
    from .materials import getMaterial, buildMaterial

    mhGeo = loadJsonRelative(filepath)
    mhProxy = mhGeo["proxy"]
    pxyGeo = mhGeo
    pxyGeo["human"] = False
    pxyGeo["name"] = ("%s:%s" % (mhHuman["name"].split(":")[0], mhProxy["name"]))
    pxyGeo["offset"] = mhHuman["offset"]
    if "material" in mhGeo.keys():
        mhMaterial = getMaterial(mhGeo["material"], pxyGeo["name"])
        mname,mat = buildMaterial(mhMaterial, scn, cfg)
        pxyGeo["material"] = mname
        mats[mname] = mat
    else:
        pxyGeo["material"] = mhHuman["material"]
    pxyGeo["scale"] = 1.0   # mhHuman["scale"]
    mhMesh = pxyGeo["seed_mesh"] = pxyGeo["mesh"] = mhGeo["mesh"]
    pxyGeo["bounding_box"] = mhProxy["bounding_box"]
    pverts,scales = fitProxy(mhHuman, mhProxy["fitting"], pxyGeo["bounding_box"])
    mhMesh["vertices"] = pverts
    return pxyGeo,scales


def fitProxy(mhHuman, mhFitting, mhScale):
    from .shapekeys import getScales
    scales = getScales(None, mhScale, mhHuman)
    scale = mhHuman["scale"]
    hverts = [scale*Vector(co) for co in mhHuman["seed_mesh"]["vertices"]]
    pverts = []
    for vnums,weights,offset in mhFitting:
        pco = (weights[0]*hverts[vnums[0]] +
               weights[1]*hverts[vnums[1]] +
               weights[2]*hverts[vnums[2]])
        pverts.append(Vector([pco[n]+scales[n]*offset[n] for n in range(3)]))
    return pverts,scales

# ---------------------------------------------------------------------
#   Vertex groups
# ---------------------------------------------------------------------

def proxifyVertexGroups(mhProxy, mhHuman, parser=None):
    if parser is None:
        try:
            parser = mhHuman["parser"]
        except KeyError:
            pass
    if parser:
        vgrps = parser.vertexGroups
    else:
        mhSeed = mhHuman["seed_mesh"]
        if "weights" in mhSeed.keys():
            vgrps = mhSeed["weights"]
        else:
            return {}

    mhFitting = mhProxy["fitting"]
    ngrps = {}
    for gname,ogrp in vgrps.items():
        grp0 = dict([(vn,0.0) for vn in range(NTotalVerts)])
        for vn,w in ogrp:
            grp0[vn] = w

        grp1 = []
        for pvn,pdata in enumerate(mhFitting):
            vnums,weights,_offsets = pdata
            grp1 += [(pvn, weights[n]*grp0[vn]) for n,vn in enumerate(vnums)]
        grp1.sort()

        ngrp = []
        if len(grp1) > 0:
            vn0 = grp1[0][0]
            wsum = 0.0
            for vn,w in grp1:
                if vn == vn0:
                    wsum += w
                else:
                    if wsum > 1e-4:
                        ngrp.append((vn0,wsum))
                    vn0 = vn
                    wsum = w
            if wsum > 1e-4:
                ngrp.append((vn0,wsum))
            if len(ngrp) > 0:
                ngrps[gname] = ngrp
    return ngrps

# ---------------------------------------------------------------------
#   Targets
# ---------------------------------------------------------------------

def proxifyTargets(mhProxy, targets):
    mhFitting = mhProxy["fitting"]
    ntrgs = {}
    for tname,otrg in targets.items():
        trg0 = dict([(vn,Vector()) for vn in range(NTotalVerts)])
        for vn,delta in otrg:
            trg0[vn] = Vector(delta)

        trg1 = []
        for pvn,pdata in enumerate(mhFitting):
            vnums,weights,_offsets = pdata
            trg1 += [(pvn, weights[n]*trg0[vn]) for n,vn in enumerate(vnums)]
        trg1.sort()

        ntrg = []
        if len(trg1) > 0:
            vn0 = trg1[0][0]
            dsum = Vector()
            for vn,delta in trg1:
                if vn == vn0:
                    dsum += delta
                else:
                    if dsum.length > 1e-3:
                        ntrg.append((vn0,dsum))
                    vn0 = vn
                    dsum = delta
            if dsum > 1e-4:
                ntrg.append((vn0,dsum))
            if len(ntrg) > 0:
                ntrgs[tname] = ntrg
    return ntrgs

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def getProxyCoordinates(mhHuman, filepath):
    from .load_json import loadJson

    mhGeo = loadJson(filepath)

    if isHairStruct(mhGeo):
        from .hair import getHairCoords
        return getHairCoords(mhHuman, mhGeo)
    else:
        offset = Vector(zup(mhHuman["offset"]))
        mhProxy = mhGeo["proxy"]
        pverts,scales = fitProxy(mhHuman, mhProxy["fitting"], mhProxy["bounding_box"])
        coords = [Vector(zup(v)) + offset for v in pverts]
        return mhGeo,coords,scales


def addMxa(context, filepath):
    ob = context.object
    rig = getArmature(ob)
    scn = context.scene

    #if len(ob.data.vertices) not in [NBodyVerts, NTotalVerts]:
    #    raise MhxError(
    #        "Mxa can only be added to a\n" +
    #        "MakeHuman mesh with\n" +
    #        "%d or %d vertices" % (NBodyVerts, NTotalVerts))

    mhHuman = getMhHuman(ob)
    mhGeo,coords,scales = getProxyCoordinates(mhHuman, filepath)
    if isHairStruct(mhGeo):
        from .hair import addHair
        addHair(ob, mhGeo, coords, scn)
    else:
        from .geometries import addMeshToScene, getVertexGroupsFromObject, buildVertexGroups
        from .masks import addMasks

        mhProxy = mhGeo["proxy"]
        gname = ("%s:%s" % (getRigName(ob), mhProxy["name"]))
        pxy = addMeshToScene(coords, gname, mhGeo["mesh"], scn)
        if rig:
            pxy.parent = rig
        else:
            pxy.parent = ob
        addMasks(mhHuman, ob, [(mhGeo,pxy)], [mhProxy["type"]], scn.MhxUseConservativeMasks)
        ngrps = proxifyVertexGroups(mhProxy, mhHuman)
        buildVertexGroups(ngrps, pxy, rig)
        if "targets" in mhGeo.keys():
            from .shapekeys import addTargets
            addTargets(pxy, mhGeo["targets"], scales)


class VIEW3D_OT_AddMxaButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx2.add_asset"
    bl_label = "Add Asset (.mxa)"
    bl_description = "Add clothes, genitalia or hair stored in am .mxa file"
    bl_options = {'UNDO'}

    filename_ext = ".mxa"
    filter_glob = StringProperty(default="*.mxa", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for loading the hair file", maxlen=1024, default="")

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob and ob.MhxHuman)

    def execute(self, context):
        try:
            addMxa(context, self.properties.filepath)
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

