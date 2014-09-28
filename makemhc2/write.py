#
#    MakeMhc2 - Utility for making mhc2 meshes.
#    Like MakeClothes but slightly newer
#    Copyright (C) Thomas Larsson 2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import bpy
from mathutils import Vector
import os
import sys
from collections import OrderedDict

from makeclothes import mc
from .error import MHError, handleMHError, addWarning
from .objects import *
from .hair import *
from .save_json import saveJson


def buildMhc2(context, hum, pxy, data):
    from .main import theSettings, getBodyPartVerts
    scn = context.scene
    struct = OrderedDict()

    if scn.MHCAuthor == "Unknown":
        addWarning("Author unknown")
    astruct = struct["file_info"] = OrderedDict()
    astruct["author"] = scn.MHCAuthor
    astruct["license"] = scn.MHCLicense
    astruct["homepage"] = scn.MHCHomePage

    pstruct = struct["proxy"] = OrderedDict()
    pstruct["name"] = pxy.name.replace(" ","_")
    pstruct["type"] = scn.MHCType

    from makeclothes import uuid4
    pstruct["uuid"] = str(uuid4.uuid4())

    if theSettings:
        pstruct["base_mesh"] = theSettings.baseMesh
    pstruct["tags"] = [getattr(scn, "MHCTag%d" % n) for n in range(1,6)]

    bbox = pstruct["bounding_box"] = OrderedDict()
    vnums = getBodyPartVerts(scn)
    hverts = hum.data.vertices
    yzswitch = [("x",1), ("z",-1), ("y",1)]
    for idx in range(3):
        cname,sign = yzswitch[idx]
        n1,n2 = vnums[idx]
        if n1 >=0 and n2 >= 0:
            x1 = hverts[n1].co[idx]
            x2 = hverts[n2].co[idx]
            bbox[cname] = (n1, n2, abs(x1-x2))

    if isHair(pxy):
        buildHair(struct, context, pxy)
    else:
        buildMesh(struct, context, pxy)

    fitting = pstruct["fitting"] = []
    for (pv, exact, verts, wts, diff) in data:
        if exact:
            (bv, dist) = verts[0]
            fitting.append((Vector((bv.index,0,0)), Vector((1,0,0)), Vector((0,0,0))))
        elif len(verts) == 3:
            fitting.append([Vector(verts),Vector(wts),Vector(diff)])

    killList = getKillList(hum)
    if killList:
        deletes = pstruct["delete_verts"] = len(hum.data.vertices)*[False]
        for vn in killList:
            deletes[vn] = True

    if isHair(pxy):
        folder = os.path.join(scn.MHCDir, "hair")
    else:
        folder = os.path.join(scn.MHCDir, "clothes")
    (outpath, filepath) = mc.getFileName(pxy, folder, "mhc2")
    saveJson(struct, filepath)
    print("Saved", filepath)


def buildMesh(struct, context, pxy):
    scn = context.scene
    deleteStrayVerts(context, pxy)
    mstruct = struct["mesh"] = OrderedDict()
    mstruct["vertices"] = [((v.co[0], v.co[2], -v.co[1])) for v in pxy.data.vertices]
    mstruct["faces"] = [tuple(f.vertices) for f in pxy.data.polygons]
    if pxy.data.uv_textures:
        (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList) = setupTexVerts(pxy)
        layer = scn.MHCTextureLayer
        uvcoord = texVertsList[layer]
        mstruct["uv_coordinates"] = [tuple(uvcoord[n]) for n in range(len(uvcoord))]
        uvfaces = uvFaceVertsList[layer]
        uvstruct = mstruct["uv_faces"] = []
        for f in pxy.data.polygons:
            uvface = uvfaces[f.index]
            uvstruct.append(tuple([uvface[n][0] for n in range(len(f.vertices))]))


#
#    writeMhc2(context, hum, pxy, data, matfile):
#

def getHeader(scn):
    if scn.MHCAuthor == "Unknown":
        addWarning("Author unknown")
    return (
        "# Exported from MakeMhc2 (TM)\n" +
        "# author %s\n" % scn.MHCAuthor +
        "# license %s\n" % scn.MHCLicense +
        "# homepage %s\n" % scn.MHCHomePage)


def writeMhc2Header(fp, scn):
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
        tag = getattr(scn, "MHCTag%d" % n)
        if tag:
            fp.write("tag %s\n" % tag)
    fp.write("\n")


def writeMhc2(context, hum, pxy, data, matfile):
    from .main import theSettings, getBodyPartVerts

    scn = context.scene
    firstVert = 0
    (outpath, outfile) = mc.getFileName(pxy, scn.MHCDir, "mhclo")
    fp = mc.openOutputFile(outfile)
    writeMhc2Header(fp, scn)
    fp.write("name %s\n" % pxy.name.replace(" ","_"))
    fp.write("obj_file %s.obj\n" % mc.goodName(pxy.name))

    vnums = getBodyPartVerts(scn)
    hverts = hum.data.vertices
    if scn.MHCUseShearing:
        if scn.MHCUseBoundaryMirror:
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

    writeStuff(fp, pxy, context, matfile)

    fp.write("verts %d\n" % (firstVert))

    if scn.MHCSelfClothed:
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
    printMhcloUvLayers(fp, pxy, scn, True)
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


def printMhcloUvLayers(fp, pxy, scn, hasObj, offset=0):
    me = pxy.data
    if me.uv_textures:
        for layer,uvtex in enumerate(me.uv_textures):
            if hasObj and (layer == scn.MHCTextureLayer):
                continue
            if scn.MHCAllUVLayers or not hasObj:
                printLayer = layer
            else:
                printLayer = 1
                if layer != scn.MHCMaskLayer:
                    continue
            (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList) = setupTexVerts(pxy)
            texVerts = texVertsList[layer]
            uvFaceVerts = uvFaceVertsList[layer]
            nTexVerts = len(texVerts)
            fp.write("texVerts %d\n" % printLayer)
            for vtn in range(nTexVerts):
                vt = texVerts[vtn]
                fp.write("%.4f %.4f\n" % (vt[0], vt[1]))
            fp.write("texFaces %d\n" % printLayer)
            for f in me.polygons:
                uvVerts = uvFaceVerts[f.index]
                uvLine = []
                for n,v in enumerate(f.vertices):
                    (vt, uv) = uvVerts[n]
                    uvLine.append("%d" % (vt+offset))
                    #fp.write("(%.3f %.3f) " % (uv[0], uv[1]))
                fp.write((" ".join(uvLine)) +"\n")


def reexportMhclo(context):
    pxy = getMhc2(context)
    scn = context.scene
    scn.objects.active = pxy
    bpy.ops.object.mode_set(mode='OBJECT')
    (outpath, outfile) = mc.getFileName(pxy, scn.MHCDir, "mhc2")
    matfile = materials.writeMaterial(pxy, scn.MHCDir)

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
                writeStuff(fp, pxy, context, matfile)
                doingStuff = True
            elif words[1] == "use_projection":
                doingStuff = False
            elif doingStuff:
                pass
            else:
                fp.write(line)
        elif not doingStuff:
            fp.write(line)
    printMhcloUvLayers(fp, pxy, scn, True)
    fp.close()
    print("%s written" % outfile)
    return


def getKillList(hum):
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
    return killList


def printDeleteVerts(fp, hum):
    killList = getKillList(hum)
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
#   writeStuff(fp, pxy, context, matfile):
#   From z_depth to use_projection
#

def writeStuff(fp, pxy, context, matfile):
    scn = context.scene
    fp.write("z_depth %d\n" % scn.MHCZDepth)

    for mod in pxy.modifiers:
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
    from .main import getMhc2

    scn = context.scene
    ob = getMhc2(context)
    deleteStrayVerts(context, ob)
    (objpath, objfile) = mc.getFileName(ob, scn.MHCDir, "obj")
    fp = mc.openOutputFile(objfile)
    fp.write(getHeader(scn))

    vlist = ["v %.4f %.4f %.4f" % (v.co[0], v.co[2], -v.co[1]) for v in ob.data.vertices]
    fp.write("\n".join(vlist) + "\n")

    if ob.data.uv_textures:
        (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList) = setupTexVerts(ob)
        layer = scn.MHCTextureLayer
        writeObjTextureData(fp, ob.data, texVertsList[layer], uvFaceVertsList[layer])
    else:
        flist = []
        for f in ob.data.polygons:
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

    flist = []
    for f in me.polygons:
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
    for f in ob.data.polygons:
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
    nverts = len(me.vertices)
    nedges = len(me.edges)
    nfaces = len(me.polygons)

    vertEdges = dict([(n,[]) for n in range(nverts)])
    vertFaces = dict([(n,[]) for n in range(nverts)])
    for e in me.edges:
        for vn in e.vertices:
            vertEdges[vn].append(e)
    for f in me.polygons:
        for vn in f.vertices:
            vertFaces[vn].append(f)

    edgeFaces = dict([(n,[]) for n in range(nedges)])
    faceEdges = dict([(n,[]) for n in range(nfaces)])
    for f in me.polygons:
        for vn in f.vertices:
            for e in vertEdges[vn]:
                v0 = e.vertices[0]
                v1 = e.vertices[1]
                if (v0 in f.vertices) and (v1 in f.vertices):
                    if f not in edgeFaces[e.index]:
                        edgeFaces[e.index].append(f)
                    if e not in faceEdges[f.index]:
                        faceEdges[f.index].append(e)

    faceNeighbors = dict([(n,[]) for n in range(nfaces)])
    for f in me.polygons:
        for e in faceEdges[f.index]:
            for f1 in edgeFaces[e.index]:
                if f1 != f:
                    faceNeighbors[f.index].append((e,f1))

    uvFaceVertsList = []
    texVertsList = []
    for index,uvtex in enumerate(me.uv_textures):
        uvFaceVerts = dict([(n,[]) for n in range(nfaces)])
        uvFaceVertsList.append(uvFaceVerts)
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
            if vec.length < 1e-5:
                uvFaceVerts[f.index].append((vtn1,uv))
                return vtn
    uvFaceVerts[f.index].append((vtn,uv))
    texVerts[vtn] = uv
    return vtn+1


