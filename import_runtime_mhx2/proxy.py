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


# ---------------------------------------------------------------------
#   Add proxy
# ---------------------------------------------------------------------

def addProxy(filepath, mhHuman):
    from .load_json import loadJsonRelative
    mhGeo = loadJsonRelative(filepath)
    mhProxy = mhGeo["proxy"]
    return proxyToGeometry(mhHuman, mhProxy, mhGeo)


def proxyToGeometry(mhHuman, mhProxy, mhGeo):
    pxyGeo = mhGeo
    pxyGeo["human"] = False
    pxyGeo["name"] = ("%s:%s" % (mhHuman["name"].split(":")[0], mhProxy["name"]))
    pxyGeo["offset"] = mhHuman["offset"]
    pxyGeo["material"] = mhHuman["material"]
    pxyGeo["scale"] = mhHuman["scale"]
    mhMesh = pxyGeo["seed_mesh"] = pxyGeo["mesh"] = mhGeo["mesh"]
    pxyGeo["sscale"] = mhProxy["sscale"]
    pverts,sscale = fitProxy(mhHuman, pxyGeo["proxy"], pxyGeo["sscale"])
    mhMesh["vertices"] = pverts
    return pxyGeo,sscale


def fitProxy(mhHuman, mhProxy, mhScale):
    from .shapekeys import getScale
    print(mhProxy.keys())
    sscale = getScale(None, mhScale, mhHuman)
    hverts = [Vector(co) for co in mhHuman["seed_mesh"]["vertices"]]
    pverts = []
    for vnums,weights,offset in mhProxy["fitting"]:
        pco = (weights[0]*hverts[vnums[0]] +
               weights[1]*hverts[vnums[1]] +
               weights[2]*hverts[vnums[2]])
        pverts.append(Vector([pco[n]+sscale[n]*offset[n] for n in range(3)]))
    return pverts,sscale

# ---------------------------------------------------------------------
#   Vertex groups
# ---------------------------------------------------------------------

def proxifyVertexGroups(mhProxy, vgrps):
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


def proxifyMask(mhProxy, vnums):
    vgrps = { "Mask" : [(vn,1.0) for vn in vnums] }
    ngrps = proxifyVertexGroups(mhProxy, vgrps)
    if "Mask" in ngrps.keys():
        pvnums = [pvn for (pvn,w) in ngrps["Mask"] if w > 0.9]
    else:
        pvnums = []
    return pvnums

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

def isHairStruct(struct):
    return ("particles" in struct.keys())


def getProxyCoordinates(mhHuman, filepath):
    from .load_json import loadJson

    offset = Vector(zup(mhHuman["offset"]))
    struct = loadJson(filepath)
    mhProxy = struct["proxy"]
    pverts,_sscale = fitProxy(mhHuman, mhProxy, mhProxy["sscale"])

    if isHairStruct(struct):
        hlist = struct["particles"]["hairs"]
        nhairs = int(len(hlist))
        hlen = int(len(hlist[0]))
        coords = []
        for m in range(nhairs):
            coords.append( [Vector(zup(v)) + offset for v in pverts[m*hlen:(m+1)*hlen]] )
    else:
        coords = [Vector(zup(v)) + offset for v in pverts]

    return struct,coords


def addHair(ob, struct, hcoords):
    from .materials import buildBlenderMaterial
    mat = buildBlenderMaterial(struct["blender_material"])
    ob.data.materials.append(mat)

    psys = ob.particle_systems.active
    if psys is not None:
        bpy.ops.object.particle_system_remove()
    bpy.ops.object.particle_system_add()

    psys = ob.particle_systems.active
    pstruct = struct["particles"]
    for key,value in pstruct.items():
        if key not in ["settings", "vertices"]:
            try:
                setattr(psys, key, value)
            except AttributeError:
                #print("***", key,value)
                pass

    pset = psys.settings
    for key,value in pstruct["settings"].items():
        if key[0] != "_":
            try:
                setattr(pset, key, value)
            except AttributeError:
                #print("  ***", key,value)
                pass

    pset.count = int(len(hcoords))
    hlen = int(len(hcoords[0]))
    pset.hair_step = hlen-1

    bpy.ops.object.mode_set(mode='PARTICLE_EDIT')

    for m,hair in enumerate(psys.particles):
        verts = hcoords[m]
        for n,v in enumerate(hair.hair_keys):
            v.co = verts[n]

    bpy.ops.object.mode_set(mode='OBJECT')


def addMhc2(ob, scn, filepath):
    from .geometries import addMeshToScene

    mhHuman = getMhHuman(ob)
    struct,coords = getProxyCoordinates(mhHuman, filepath)
    if isHairStruct(struct):
        addHair(ob, struct, coords)
    else:
        gname = ("%s:%s" % (getRigName(ob), struct["proxy"]["name"]))
        addMeshToScene(coords, gname, struct["mesh"], scn)


class VIEW3D_OT_AddMhc2Button(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx2.add_mhc2"
    bl_label = "Add Mhc2 (.mhc2)"
    bl_description = "Add clothes, genitalia or hair stored in a mhc2 file"
    bl_options = {'UNDO'}

    filename_ext = ".mhc2"
    filter_glob = StringProperty(default="*.mhc2", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for loading the hair file", maxlen=1024, default="")

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob and ob.type == 'MESH')

    def execute(self, context):
        try:
            addMhc2(context.object, context.scene, self.properties.filepath)
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ---------------------------------------------------------------------
#   Global variable that holds the loaded json struct for the
#   current human.
# ---------------------------------------------------------------------

def setMhHuman(human):
    global theMhHuman
    theMhHuman = human

def getMhHuman(ob):
    global theMhHuman
    try:
        theMhHuman
    except:
        raise MhxError("No saved human")
    if theMhHuman["uuid"] != ob.MhxUuid:
        raise MhxError("Saved human %s\ndoes not match current object")
    return theMhHuman

print("Hair loaded")