#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/external_tools_license.html)

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

**Coding Standards:**  See http://www.makehuman.org/node/165

"""

import bpy
import os
from makeclothes import mc
from .error import MHError, handleMHError, addWarning
from .objects import *

#
#    writeProxy(context, hum, clo, data, matfile):
#

def getHeader(scn):
    if scn.MCAuthor == "Unknown":
        addWarning("Author unknown")
    return (
        "# Exported from MakeProxy (TM)\n" +
        "# author %s\n" % scn.MCAuthor +
        "# license %s\n" % scn.MCLicense +
        "# homepage %s\n" % scn.MCHomePage)


def writeProxyHeader(fp, scn):
    import sys
    from .main import theSettings

    if sys.platform == 'win32':
        # Avoid error message in blender by using a version without ctypes
        from makeclothes import uuid4 as uuid
    else:
        import uuid

    fp.write(getHeader(scn))
    fp.write("uuid %s\n" % uuid.uuid4())
    if theSettings:
        fp.write("basemesh %s\n" % theSettings.baseMesh)
    for n in range(1,6):
        tag = getattr(scn, "MCTag%d" % n)
        if tag:
            fp.write("tag %s\n" % tag)
    fp.write("\n")


def writeProxy(context, hum, clo, data, matfile):
    from .main import theSettings, getBodyPartVerts

    scn = context.scene
    firstVert = 0
    (outpath, outfile) = mc.getFileName(clo, scn.MCProxyDir, "mhc2")
    fp = mc.openOutputFile(outfile)
    writeProxyHeader(fp, scn)
    fp.write("name %s\n" % clo.name.replace(" ","_"))
    fp.write("obj_file %s.obj\n" % mc.goodName(clo.name))

    vnums = getBodyPartVerts(scn)
    hverts = hum.data.vertices
    if scn.MCUseShearing:
        if scn.MCUseBoundaryMirror:
            rvnums = {}
            for idx,pair in enumerate(vnums):
                vn1, vn2 = pair
                rvnums[idx] = (mirrorVert(vn1), mirrorVert(vn2))
            vn = vnums[0][0]
            if hverts[vn].co[0] > 0:
                lvnums = vnums
            else:
                lvnums = rvnums
                rvnums = vnums
            writeShear(fp, "l_shear_%s %d %d %.4f %.4f\n", lvnums, hverts, False)
            writeShear(fp, "r_shear_%s %d %d %.4f %.4f\n", rvnums, hverts, False)
        else:
            writeShear(fp, "shear_%s %d %d %.4f %.4f\n", vnums, hverts, False)
    else:
        writeShear(fp, "%s_scale %d %d %.4f\n", vnums, hverts, True)

    writeStuff(fp, clo, context, matfile)

    fp.write("verts %d\n" % (firstVert))

    if scn.MCSelfClothed:
        for n in range(theSettings.vertices["Penis"][0]):
            fp.write("%5d\n" % n)

    for (pv, exact, verts, wts, diff) in data:
        if exact:
            (bv, dist) = verts[0]
            fp.write("%5d\n" % bv.index)
        elif len(verts) == 3:
            fp.write("%5d %5d %5d %.5f %.5f %.5f %.5f %.5f %.5f\n" % (
                verts[0], verts[1], verts[2], wts[0], wts[1], wts[2], diff[0], diff[2], -diff[1]))
        elif len(verts) == 8:   # Rigid fit
            fp.write("%5d %5d %5d %5d %5d %5d %5d %5d %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f\n" % tuple(verts+wts))
        else:
            raise RuntimeError("Bug: Wrong number of verts %s" % verts)

    fp.write('\n')
    printDeleteVerts(fp, hum)
    printMhcloUvLayers(fp, clo, scn, True)
    fp.close()
    print("%s done" % outfile)


def writeShear(fp, string, vnums, hverts, useDistance):
    yzswitch = [("x",1), ("z",-1), ("y",1)]
    for idx in range(3):
        cname,sign = yzswitch[idx]
        n1,n2 = vnums[idx]
        if n1 >=0 and n2 >= 0:
            x1 = hverts[n1].co[idx]
            x2 = hverts[n2].co[idx]
            if useDistance:
                fp.write(string % (cname, n1, n2, abs(x1-x2)))
            else:
                fp.write(string % (cname, n1, n2, sign*x1, sign*x2))


def mirrorVert(vn):
    from maketarget.symmetry_map import Left2Right, Right2Left
    try:
        return Left2Right[vn]
    except KeyError:
        pass
    try:
        return Right2Left[vn]
    except KeyError:
        return vn


def printMhcloUvLayers(fp, clo, scn, hasObj, offset=0):
    me = clo.data
    if me.uv_textures:
        for layer,uvtex in enumerate(me.uv_textures):
            if hasObj and (layer == scn.MCTextureLayer):
                continue
            if scn.MCAllUVLayers or not hasObj:
                printLayer = layer
            else:
                printLayer = 1
                if layer != scn.MCMaskLayer:
                    continue
            (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList) = setupTexVerts(clo)
            texVerts = texVertsList[layer]
            uvFaceVerts = uvFaceVertsList[layer]
            nTexVerts = len(texVerts)
            fp.write("texVerts %d\n" % printLayer)
            for vtn in range(nTexVerts):
                vt = texVerts[vtn]
                fp.write("%.4f %.4f\n" % (vt[0], vt[1]))
            fp.write("texFaces %d\n" % printLayer)
            meFaces = getFaces(me)
            for f in meFaces:
                uvVerts = uvFaceVerts[f.index]
                uvLine = []
                for n,v in enumerate(f.vertices):
                    (vt, uv) = uvVerts[n]
                    uvLine.append("%d" % (vt+offset))
                    #fp.write("(%.3f %.3f) " % (uv[0], uv[1]))
                fp.write((" ".join(uvLine)) +"\n")


def reexportMhclo(context):
    clo = getProxy(context)
    scn = context.scene
    scn.objects.active = clo
    bpy.ops.object.mode_set(mode='OBJECT')
    (outpath, outfile) = mc.getFileName(clo, scn.MCProxyDir, "mhc2")
    matfile = materials.writeMaterial(clo, scn.MCProxyDir)

    lines = []
    print("Reading clothes file %s" % outfile)
    fp = open(outfile, "r")
    for line in fp:
        lines.append(line)
    fp.close()

    fp = mc.openOutputFile(outfile)
    doingStuff = False
    for line in lines:
        words = line.split()
        if len(words) == 0:
            fp.write(line)
        elif (words[0] == "#"):
            if words[1] in ["texVerts", "texFaces"]:
                break
            elif words[1] == "z_depth":
                writeStuff(fp, clo, context, matfile)
                doingStuff = True
            elif words[1] == "use_projection":
                doingStuff = False
            elif doingStuff:
                pass
            else:
                fp.write(line)
        elif not doingStuff:
            fp.write(line)
    printMhcloUvLayers(fp, clo, scn, True)
    fp.close()
    print("%s written" % outfile)
    return


def printDeleteVerts(fp, hum):
    kill = None
    for g in hum.vertex_groups:
        if g.name == "Delete":
            kill = g
            break
    if not kill:
        return

    killList = []
    for v in hum.data.vertices:
        for vg in v.groups:
            if vg.group == kill.index:
                killList.append(v.index)
    if not killList:
        return

    fp.write("delete_verts\n")
    n = 0
    vn0 = -100
    sequence = False
    for vn in killList:
        if vn != vn0+1:
            if sequence:
                fp.write("- %d " % vn0)
            n += 1
            if n % 10 == 0:
                fp.write("\n")
            sequence = False
            fp.write("%d " % vn)
        else:
            if vn0 < 0:
                fp.write("%d " % vn)
            sequence = True
        vn0 = vn
    if sequence:
        fp.write("- %d" % vn)
    fp.write("\n")

#
#   writeStuff(fp, clo, context, matfile):
#   From z_depth to use_projection
#

def writeStuff(fp, clo, context, matfile):
    scn = context.scene
    fp.write("z_depth %d\n" % scn.MCZDepth)

    for mod in clo.modifiers:
        if mod.type == 'SHRINKWRAP':
            fp.write("shrinkwrap %.3f\n" % (mod.offset))
        elif mod.type == 'SUBSURF':
            fp.write("subsurf %d %d\n" % (mod.levels, mod.render_levels))
        elif mod.type == 'SOLIDIFY':
            fp.write("solidify %.3f %.3f\n" % (mod.thickness, mod.offset))

    if matfile:
        fp.write("material %s\n" % matfile)


#
#   exportObjFile(context):
#

def exportObjFile(context):
    from .main import getProxy

    scn = context.scene
    ob = getProxy(context)
    deleteStrayVerts(context, ob)
    (objpath, objfile) = mc.getFileName(ob, scn.MCProxyDir, "obj")
    fp = mc.openOutputFile(objfile)
    fp.write(getHeader(scn))

    me = ob.data

    vlist = ["v %.4f %.4f %.4f" % (v.co[0], v.co[2], -v.co[1]) for v in ob.data.vertices]
    fp.write("\n".join(vlist) + "\n")

    if me.uv_textures:
        (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList) = setupTexVerts(ob)
        layer = scn.MCTextureLayer
        writeObjTextureData(fp, me, texVertsList[layer], uvFaceVertsList[layer])
    else:
        meFaces = getFaces(me)
        flist = []
        for f in meFaces:
            l = ["f"]
            for vn in f.vertices:
                l.append("%d" % (vn+1))
            flist.append(" ".join(l))
        fp.write("\n".join(flist))

    fp.close()
    print(objfile, "exported")

    npzfile = os.path.splitext(objfile)[0] + ".npz"
    try:
        os.remove(npzfile)
        print(npzfile, "removed")
    except FileNotFoundError:
        pass


def writeObjTextureData(fp, me, texVerts, uvFaceVerts):
    nTexVerts = len(texVerts)
    vlist = []
    for vtn in range(nTexVerts):
        vt = texVerts[vtn]
        vlist.append("vt %.4f %.4f" % (vt[0], vt[1]))
    fp.write("\n".join(vlist) + "\n")

    meFaces = getFaces(me)
    flist = []
    for f in meFaces:
        uvVerts = uvFaceVerts[f.index]
        l = ["f"]
        for n,v in enumerate(f.vertices):
            (vt, uv) = uvVerts[n]
            l.append("%d/%d" % (v+1, vt+1))
        flist.append(" ".join(l))
    fp.write("\n".join(flist))


def writeColor(fp, string1, string2, color, intensity):
    fp.write(
        "%s %.4f %.4f %.4f\n" % (string1, color[0], color[1], color[2]) +
        "%s %.4g\n" % (string2, intensity))

#
#   deleteStrayVerts(context, ob):
#

def deleteStrayVerts(context, ob):
    scn = context.scene
    scn.objects.active = ob
    bpy.ops.object.mode_set(mode='OBJECT')
    verts = ob.data.vertices
    onFaces = {}
    for v in verts:
        onFaces[v.index] = False
    faces = getFaces(ob.data)
    for f in faces:
        for vn in f.vertices:
            onFaces[vn] = True
    for v in verts:
        if not onFaces[v.index]:
            raise MHError("Mesh %s has stray vert %d" % (ob.name, v.index))
        return

#
#   setupTexVerts(ob):
#

def setupTexVerts(ob):
    me = ob.data
    vertEdges = {}
    vertFaces = {}
    for v in me.vertices:
        vertEdges[v.index] = []
        vertFaces[v.index] = []
    for e in me.edges:
        for vn in e.vertices:
            vertEdges[vn].append(e)
    meFaces = getFaces(me)
    for f in meFaces:
        for vn in f.vertices:
            vertFaces[vn].append(f)

    edgeFaces = {}
    for e in me.edges:
        edgeFaces[e.index] = []
    faceEdges = {}
    for f in meFaces:
        faceEdges[f.index] = []
    for f in meFaces:
        for vn in f.vertices:
            for e in vertEdges[vn]:
                v0 = e.vertices[0]
                v1 = e.vertices[1]
                if (v0 in f.vertices) and (v1 in f.vertices):
                    if f not in edgeFaces[e.index]:
                        edgeFaces[e.index].append(f)
                    if e not in faceEdges[f.index]:
                        faceEdges[f.index].append(e)

    faceNeighbors = {}
    for f in meFaces:
        faceNeighbors[f.index] = []
    for f in meFaces:
        for e in faceEdges[f.index]:
            for f1 in edgeFaces[e.index]:
                if f1 != f:
                    faceNeighbors[f.index].append((e,f1))

    uvFaceVertsList = []
    texVertsList = []
    for index,uvtex in enumerate(me.uv_textures):
        uvFaceVerts = {}
        uvFaceVertsList.append(uvFaceVerts)
        for f in meFaces:
            uvFaceVerts[f.index] = []
        vtn = 0
        texVerts = {}
        texVertsList.append(texVerts)

        uvloop = me.uv_layers[index]
        n = 0
        for f in me.polygons:
            for vn in f.vertices:
                uvv = uvloop.data[n]
                n += 1
                vtn = findTexVert(uvv.uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts, ob)
    return (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList)


def findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts, ob):
    for (e,f1) in faceNeighbors[f.index]:
        for (vtn1,uv1) in uvFaceVerts[f1.index]:
            vec = uv - uv1
            if vec.length < 1e-8:
                uvFaceVerts[f.index].append((vtn1,uv))
                return vtn
    uvFaceVerts[f.index].append((vtn,uv))
    texVerts[vtn] = uv
    return vtn+1


