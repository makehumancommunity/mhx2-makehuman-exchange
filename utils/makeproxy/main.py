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

Abstract
--------
Utility for making clothes to MHX2 characters.

"""

import bpy
import os
import math
import random
import ast
from bpy.props import *
from mathutils import Vector

from maketarget.utils import getMHBlenderDirectory
from .error import MHError, handleMHError, addWarning
from makeclothes import mc
from .objects import *
from . import materials


def selectHelpers(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    n0 = theSettings.vertices["Penis"][0]
    n1 = theSettings.nTotalVerts
    for n in range(n0,n1):
        ob.data.vertices[n].select = True
    bpy.ops.object.mode_set(mode='EDIT')

#
#   snapSelectedVerts(context):
#

def snapSelectedVerts(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    selected = []
    for v in ob.data.vertices:
        if v.select:
            selected.append(v)
    bpy.ops.object.mode_set(mode='EDIT')
    for v in selected:
        v.select = True
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.translate(
            snap=True,
            snap_target='CLOSEST',
            snap_point=(0, 0, 0),
            snap_align=False,
            snap_normal=(0, 0, 0))
    return

#
#    selectVerts(verts, ob):
#

def selectVerts(verts, ob):
    for v in ob.data.vertices:
        v.select = False
    for v in verts:
        v.select = True
    return

#
#
#

def loadHuman(context):
    from maketarget import mt, import_obj, utils
    from maketarget.maketarget import afterImport, newTarget, applyTargets

    scn = context.scene
    bodytype = scn.MCBodyType
    if bodytype[:2] == "h-":
        bodytype = bodytype[2:]
        helpers = True
    else:
        helpers = False

    if helpers:
        basepath = mt.baseMhcloFile
        import_obj.importBaseMhclo(context, basepath)
        afterImport(context, basepath, False, True)
    else:
        basepath = mt.baseObjFile
        import_obj.importBaseObj(context, basepath)
        afterImport(context, basepath, True, False)

    if bodytype == 'None':
        newTarget(context)
        found = True
    else:
        trgpath = os.path.join(os.path.dirname(__file__), "../makeclothes/targets", bodytype + ".target")
        try:
            utils.loadTarget(trgpath, context)
            found = True
        except FileNotFoundError:
            found = False
    if not found:
        raise MHError("Target \"%s\" not found.\nPath \"%s\" does not seem to be the path to the MakeHuman program" % (trgpath, scn.MhProgramPath))
    applyTargets(context)
    ob = context.object
    ob.name = "Human"
    ob.MhHuman = True
    if helpers:
        autoVertexGroups(ob, 'Helpers', 'Tights')
    else:
        autoVertexGroups(ob, 'Body', None)
    clearSelection()


#
#    findProxy(context, hum, pxy):
#

def findProxy(context, hum, pxy):
    """
    This is where the association between clothes and human verts is made.
    """

    scn = context.scene
    humanGroup,pExactIndex = findVertexGroups(hum, pxy)
    bestVerts,vfaces = findBestVerts(scn, humanGroup, pExactIndex, hum, pxy)
    bestFaces = findBestFaces(scn, bestVerts, vfaces, hum, pxy)
    return bestFaces


def findVertexGroups(hum, pxy):
    # Associate groups
    humanGroup = {}
    pExactIndex = None
    for pgrp in pxy.vertex_groups:
        for bgrp in hum.vertex_groups:
            if pgrp.name == bgrp.name:
                bverts = []
                humanGroup[pgrp.index] = (bgrp, bverts)
                for bv in hum.data.vertices:
                    for bg in bv.groups:
                        if bg.group == bgrp.index:
                            bverts.append(bv)
            if pgrp.name == "Exact":
                pExactIndex = pgrp.index

    return humanGroup,pExactIndex


def getVGroupIndices(pv, pxy, humanGroup, pExactIndex):
    # Check that there is a single clothes vertex group, except perhaps
    # for the Exact group.
    forceExact = False
    if len(pv.groups) == 0:
        pindex = -1
    elif len(pv.groups) == 1:
        pindex = pv.groups[0].group
        if pindex == pExactIndex:
            pindex = -1
    elif len(pv.groups) == 2:
        pindex = pv.groups[0].group
        pindex1 = pv.groups[1].group
        if pindex == pExactIndex:
            forceExact = True
            pindex = pindex1
        elif pindex1 == pExactIndex:
            forceExact = True
    else:
        pindex = -1

    if pindex < 0:
        selectVerts([pv], pxy)
        raise MHError("Proxy %s vert %d not member of any group" % (pxy.name, pv.index))

    # Check that human group exists
    try:
        bg,_bverts = humanGroup[pindex]
        bindex = bg.index
    except KeyError:
        gname = pxy.vertex_groups[pindex].name
        raise MHError("Did not find vertex group %s in hum.data mesh" % gname)

    return pindex, bindex, forceExact


def isRigidVGroup(vgrp):
    return (len(vgrp.name) > 0 and vgrp.name[0] == '*')


class BestVert:
    def __init__(self, pv, bindex, exact, mverts, faces, useMid):
        self.pv = pv
        self.bindex = bindex
        self.exact = exact
        self.mverts = mverts
        self.faces = faces
        self.useMid = useMid


def findBestVerts(scn, humanGroup, pExactIndex, hum, pxy):
    # Associate verts

    bestVerts = []
    for pv in pxy.data.vertices:
        pindex,bindex,forceExact = getVGroupIndices(pv, pxy, humanGroup, pExactIndex)
        bg,bverts = humanGroup[pindex]

        if isRigidVGroup(bg):
            bv = bverts[0]
            vec = pv.co - bv.co
            mverts = [(bv, vec.length)]
            bestVerts.append(BestVert(pv, bindex, False, mverts, [], False))
            continue

        # Find a small number of human verts closest to the clothes vert
        mverts = []
        for n in range(scn.MCListLength):
            mverts.append((None, 1e6))

        exact = False
        for bv in bverts:
            if exact:
                break

            vec = pv.co - bv.co
            n = 0
            for (mv,mdist) in mverts:
                if vec.length < Epsilon:
                    mverts[0] = (bv, -1)
                    exact = True
                    break
                if vec.length < mdist:
                    for k in range(n+1, scn.MCListLength):
                        j = scn.MCListLength-k+n
                        mverts[j] = mverts[j-1]
                    mverts[n] = (bv, vec.length)
                    break
                n += 1

        (mv, mindist) = mverts[0]
        bg,_bverts = humanGroup[pindex]
        gname = bg.name
        if mv:
            if pv.index % 100 == 0:
                print(pv.index, mv.index, mindist, gname, pindex, bindex)
        else:
            msg = (
            "Failed to find vert %d in group %s.\n" % (pv.index, gname) +
            "Proxy index %d, Human index %d\n" % (pindex, bindex) +
            "Vertex coordinates (%.4f %.4f %.4f)\n" % (pv.co[0], pv.co[1], pv.co[2])
            )
            selectVerts([pv], pxy)
            raise MHError(msg)
        if mindist > 50:
            msg = (
            "Vertex %d is %f dm away from closest body vertex in group %s.\n" % (pv.index, mindist, gname) +
            "Max allowed value is 5dm. Check human and clothes scales.\n" +
            "Vertex coordinates (%.4f %.4f %.4f)\n" % (pv.co[0], pv.co[1], pv.co[2])
            )
            selectVerts([pv], pxy)
            raise MHError(msg)

        if gname[0:3] != "Mid" and gname[-2:] != "_M":
            bindex = -1
        if forceExact:
            exact = True
            mverts = [mverts[0]]
        bestVerts.append(BestVert(pv, bindex, exact, mverts, [], True))

    print("Setting up face table")

    vfaces = {}
    rigid = {}
    for vn in range(len(hum.data.vertices)):
        vfaces[vn] = []
        rigid[vn] = False

    #
    for idx in humanGroup.keys():
        bg,bverts = humanGroup[idx]
        if isRigidVGroup(bg):
            print("RIGID", bg.name)
            if len(bverts) != 3:
                raise MHError("Human vertex group \"%s\"\nmust contain exactly three vertices" % humanGroup[idx].name)
            v0,v1,v2 = bverts
            vn0,vn1,vn2 = v0.index, v1.index, v2.index
            t = (vn0,vn1,vn2)
            vfaces[vn0] = vfaces[vn1] = vfaces[vn2] = [t]
            rigid[vn0] = rigid[vn1] = rigid[vn2] = True

    baseFaces = getFaces(hum.data)
    for f in baseFaces:
        vn0,vn1,vn2,vn3 = f.vertices
        if not (rigid[vn0] or rigid[vn1] or rigid[vn2] or rigid[vn3]):
            t0 = [vn0,vn1,vn2]
            t1 = [vn1,vn2,vn3]
            t2 = [vn2,vn3,vn0]
            t3 = [vn3,vn0,vn1]
            vfaces[vn0].extend( [t0,t2,t3] )
            vfaces[vn1].extend( [t0,t1,t3] )
            vfaces[vn2].extend( [t0,t1,t2] )
            vfaces[vn3].extend( [t1,t2,t3] )

    return bestVerts, vfaces


def findBestFaces(scn, bestVerts, vfaces, hum, pxy):
    print("Finding weights")
    for bestVert in bestVerts:
        pv = bestVert.pv
        if bestVert.exact:
            continue
        for (bv,mdist) in bestVert.mverts:
            if bv:
                for f in vfaces[bv.index]:
                    v0 = hum.data.vertices[f[0]]
                    v1 = hum.data.vertices[f[1]]
                    v2 = hum.data.vertices[f[2]]
                    if bestVert.useMid and (bestVert.bindex >= 0) and (pv.co[0] < 0.01) and (pv.co[0] > -0.01):
                        wts = midWeights(pv, bestVert.bindex, v0, v1, v2, hum, pxy)
                    else:
                        wts = cornerWeights(pv, v0, v1, v2, hum, pxy)
                    bestVert.faces.append((f, wts))

    print("Finding best weights")
    alwaysOutside = False
    minOffset = 0.0
    useProjection = False

    bestFaces = []
    badVerts = []
    for bestVert in bestVerts:
        pv = bestVert.pv
        #print(pv.index)
        pv.select = False
        if bestVert.exact:
            bestFaces.append((pv, True, bestVert.mverts, 0, 0))
            continue
        minmax = -1e6
        for (fverts, wts) in bestVert.faces:
            w = minWeight(wts)
            if w > minmax:
                minmax = w
                bWts = wts
                bVerts = fverts
        if False and minmax < scn.MCThreshold:
            badVerts.append(pv.index)
            pv.select = True
            (mv, mdist) = bestVert.mverts[0]
            bVerts = [mv.index,0,1]
            bWts = (1,0,0)

        v0 = hum.data.vertices[bVerts[0]]
        v1 = hum.data.vertices[bVerts[1]]
        v2 = hum.data.vertices[bVerts[2]]

        est = bWts[0]*v0.co + bWts[1]*v1.co + bWts[2]*v2.co
        diff = pv.co - est
        bestFaces.append((pv, False, bVerts, bWts, diff))

    return bestFaces


#
#    minWeight(wts)
#

def minWeight(wts):
    best = 1e6
    for w in wts:
        if w < best:
            best = w
    return best

#
#    cornerWeights(pv, v0, v1, v2, hum, pxy):
#
#    px = w0*x0 + w1*x1 + w2*x2
#    py = w0*y0 + w1*y1 + w2*y2
#    pz = w0*z0 + w1*z1 + w2*z2
#
#    w2 = 1-w0-w1
#
#    w0*(x0-x2) + w1*(x1-x2) = px-x2
#    w0*(y0-y2) + w1*(y1-y2) = py-y2
#
#    a00*w0 + a01*w1 = b0
#    a10*w0 + a11*w1 = b1
#
#    det = a00*a11 - a01*a10
#
#    det*w0 = a11*b0 - a01*b1
#    det*w1 = -a10*b0 + a00*b1
#

def cornerWeights(pv, v0, v1, v2, hum, pxy):
    r0 = v0.co
    r1 = v1.co
    r2 = v2.co
    u01 = r1-r0
    u02 = r2-r0
    n = u01.cross(u02)
    n.normalize()

    u = pv.co-r0
    r = r0 + u - n*u.dot(n)

    """
    a00 = r0[0]-r2[0]
    a01 = r1[0]-r2[0]
    a10 = r0[1]-r2[1]
    a11 = r1[1]-r2[1]
    b0 = r[0]-r2[0]
    b1 = r[1]-r2[1]
    """

    e0 = u01
    e0.normalize()
    e1 = n.cross(e0)
    e1.normalize()

    u20 = r0-r2
    u21 = r1-r2
    ur2 = r-r2

    a00 = u20.dot(e0)
    a01 = u21.dot(e0)
    a10 = u20.dot(e1)
    a11 = u21.dot(e1)
    b0 = ur2.dot(e0)
    b1 = ur2.dot(e1)

    det = a00*a11 - a01*a10
    if abs(det) < 1e-20:
        print("Proxy vert %d mapped to degenerate triangle (det = %g) with corners" % (pv.index, det))
        print("r0 ( %.6f  %.6f  %.6f )" % (r0[0], r0[1], r0[2]))
        print("r1 ( %.6f  %.6f  %.6f )" % (r1[0], r1[1], r1[2]))
        print("r2 ( %.6f  %.6f  %.6f )" % (r2[0], r2[1], r2[2]))
        print("A [ %.6f %.6f ]\n  [ %.6f %.6f ]" % (a00,a01,a10,a11))
        selectVerts([pv], pxy)
        selectVerts([v0, v1, v2], hum)
        raise MHError("Singular matrix in cornerWeights")

    w0 = (a11*b0 - a01*b1)/det
    w1 = (-a10*b0 + a00*b1)/det

    return (w0, w1, 1-w0-w1)

#
#   midWeights(pv, bindex, v0, v1, v2, hum, pxy):
#

def midWeights(pv, bindex, v0, v1, v2, hum, pxy):
    print("Mid", pv.index, bindex)
    pv.select = True
    if isInGroup(v0, bindex):
        v0.select = True
        if isInGroup(v1, bindex):
            v1.select = True
            return midWeight(pv, v0.co, v1.co)
        elif isInGroup(v2, bindex):
            (w1, w0, w2) = midWeight(pv, v0.co, v2.co)
            v2.select = True
            return (w0, w1, w2)
    elif isInGroup(v1, bindex) and isInGroup(v2, bindex):
        (w1, w2, w0) = midWeight(pv, v1.co, v2.co)
        v1.select = True
        v2.select = True
        return (w0, w1, w2)
    print("  Failed mid")
    return cornerWeights(pv, v0, v1, v2, hum, pxy)


def isInGroup(v, bindex):
    for g in v.groups:
        if g.group == bindex:
            return True
    return False


def midWeight(pv, r0, r1):
    u01 = r1-r0
    d01 = u01.length
    u = pv.co-r0
    s = u.dot(u01)
    w = s/(d01*d01)
    return (1-w, w, 0)

#
#   storeData(pxy, hum, data):
#   restoreData(context):
#

def storeData(pxy, hum, data):
    outfile = settingsFile("stored")
    fp = mc.openOutputFile(outfile)
    fp.write("%s\n" % pxy.name)
    fp.write("%s\n" % hum.name)
    for (pv, exact, verts, wts, diff) in data:
        if exact:
            bv,n = verts[0]
            fp.write("%d %d %d\n" % (pv.index, exact, bv.index))
        else:
            fp.write("%d %d\n" % (pv.index, exact))
            fp.write("%s\n" % list(verts))
            fp.write("(%s,%s,%s)\n" % wts)
            fp.write("(%s,%s,%s)\n" % (diff[0],diff[1],diff[2]))
    fp.close()
    return

def parse(string):
    return ast.literal_eval(string)

def restoreData(context):
    (hum, pxy) = getObjectPair(context)
    fname = settingsFile("stored")
    fp = mc.openInputFile(fname)
    status = 0
    data = []
    for line in fp:
        #print(line)
        words = line.split()
        if status == 0:
            pname = line.rstrip()
            if pname != pxy.name:
                raise MHError(
                "Restore error: stored data for %s does not match selected object %s\n" % (pname, pxy.name) +
                "Make clothes for %s first\n" % pxy.name)
            status = 10
        elif status == 10:
            bname = line.rstrip()
            if bname != hum.name:
                raise MHError(
                "Restore error: stored human %s does not match selected human %s\n" % (bname, hum.name) +
                "Make clothes for %s first\n" % pxy.name)
            status = 1
        elif status == 1:
            pv = pxy.data.vertices[int(words[0])]
            exact = int(words[1])
            if exact:
                bv = hum.data.vertices[int(words[2])]
                data.append((pv, exact, ((bv,-1),0,1), 0, 0))
                status = 1
            else:
                status = 2
        elif status == 2:
            verts = parse(line)
            if exact:
                data.append((pv, exact, verts, 0, 0))
                status = 1
            else:
                status = 3
        elif status == 3:
            wts = parse(line)
            status = 4
        elif status == 4:
            diff = Vector( parse(line) )
            data.append((pv, exact, verts, wts, diff))
            status = 1
    hum = context.scene.objects[bname]
    return (hum, data)

#
#    makeProxy(context, doFindProxy):
#

def makeProxy(context, doFindProxy):
    from makeclothes.project import saveClosest
    from .write import writeProxy

    (hum, pxy) = getObjectPair(context)
    scn = context.scene
    checkNoTriangles(scn, pxy)
    checkObjectOK(hum, context, False)
    autoVertexGroupsIfNecessary(hum, 'Selected')
    #checkAndUnVertexDiamonds(context, hum)
    checkObjectOK(pxy, context, True)
    autoVertexGroupsIfNecessary(pxy)
    checkSingleVertexGroups(pxy, scn)
    saveClosest({})
    matfile = materials.writeMaterial(pxy, scn.MCProxyDir)
    if doFindProxy:
        data = findProxy(context, hum, pxy)
        storeData(pxy, hum, data)
    else:
        (hum, data) = restoreData(context)
    writeProxy(context, hum, pxy, data, matfile)


def checkNoTriangles(scn, ob):
    strayVerts = {}
    nPoles = {}
    for vn in range(len(ob.data.vertices)):
        strayVerts[vn] = True
        nPoles[vn] = 0

    for f in ob.data.polygons:
        if len(f.vertices) != 4:
            msg = "Object %s\ncan not be used for clothes creation\nbecause it has non-quad faces.\n" % (ob.name)
            raise MHError(msg)
        for vn in f.vertices:
            strayVerts[vn] = False
            nPoles[vn] += 1

    stray = [vn for vn in strayVerts.keys() if strayVerts[vn]]
    if len(stray) > 0:
        highlightVerts(scn, ob, stray)
        msg = "Object %s\ncan not be used for clothes creation\nbecause it has stray verts:\n  %s" % (ob.name, stray)
        raise MHError(msg)

    excess = [vn for vn in nPoles.keys() if nPoles[vn] > 8]
    if len(excess) > 0:
        highlightVerts(scn, ob, excess)
        msg = "Object %s\ncan not be used for clothes creation\nbecause it has verts with more than 8 poles:\n  %s" % (ob.name, excess)
        raise MHError(msg)


def highlightVerts(scn, ob, verts):
    bpy.ops.object.mode_set(mode='OBJECT')
    scn.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for vn in verts:
        print(vn)
        ob.data.vertices[vn].select = True
    bpy.ops.object.mode_set(mode='EDIT')


def checkObjectOK(ob, context, isProxy):
    old = context.object
    scn = context.scene
    scn.objects.active = ob
    word = None
    err = False
    line2 = "Apply, create or delete before proceeding.\n"

    if ob.location.length > Epsilon:
        word = "object translation"
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    eu = ob.rotation_euler

    if abs(eu.x) + abs(eu.y) + abs(eu.z) > Epsilon:
        word = "object rotation"
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    vec = ob.scale - Vector((1,1,1))

    if vec.length > Epsilon:
        word = "object scaling"
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if ob.constraints:
        word = "constraints"
        err = True

    for mod in ob.modifiers:
        if (mod.type in ['CHILD_OF', 'ARMATURE']) and mod.show_viewport:
            word = "an enabled %s modifier" % mod.type
            mod.show_viewport = False

    if ob.data.shape_keys:
        word = "shape_keys"
        err = True

    if ob.parent:
        word = "parent"
        ob.parent = None

    if isProxy:
        try:
            ob.data.uv_layers[scn.MCTextureLayer]
        except:
            word = "no UV maps"
            err = True

        if len(ob.data.uv_textures) > 1:
            word = "%d UV maps. Must be exactly one." % len(ob.data.uv_textures)
            err = True

        if len(ob.data.materials) >= 2:
            word = "%d materials. Must be at most one." % len(ob.data.materials)
            err = True

        #if not materials.checkObjectHasDiffuseTexture(ob):
        #    word = "no diffuse image texture"
        #    line2 = "Create texture or delete material before proceeding.\n"
        #    err = True

    if word:
        msg = "Object %s\ncan not be used for clothes creation because\nit has %s.\n" % (ob.name, word)
        if err:
            msg +=  line2
            raise MHError(msg)
        else:
            print(msg)
            print("Fixed automatically")
    context.scene.objects.active = old
    return

#
#   checkSingleVertexGroups(pxy, scn):
#

def checkSingleVertexGroups(pxy, scn):
    for v in pxy.data.vertices:
        n = 0
        for g in v.groups:
            #print("Key", g.group, g.weight)
            n += 1
        if n != 1:
            for g in v.groups:
                for vg in pxy.vertex_groups:
                    if vg.index == g.group:
                        if vg.name == "Exact":
                            n -= 1
                        else:
                            print("  ", vg.name)
            if n != 1:
                vn = v.index
                scn.objects.active = pxy
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                v = pxy.data.vertices[vn]
                v.select = True
                bpy.ops.object.mode_set(mode='EDIT')
                raise MHError("Vertex %d in %s belongs to %d groups. Must be exactly one" % (vn, pxy.name, n))


def writeFaces(pxy, fp):
    fp.write("faces\n")
    meFaces = getFaces(pxy.data)
    for f in meFaces:
        for v in f.vertices:
            fp.write(" %d" % (v+1))
        fp.write("\n")


def writeVertexGroups(pxy, fp):
    for vg in pxy.vertex_groups:
        fp.write("weights %s\n" % vg.name)
        for v in pxy.data.vertices:
            for g in v.groups:
                if g.group == vg.index and g.weight > 1e-4:
                    fp.write(" %d %.4g \n" % (v.index, g.weight))

#
#    writePrio(data, prio, pad, fp):
#    writeDir(data, exclude, pad, fp):
#

def writePrio(data, prio, pad, fp):
    for ext in prio:
        writeExt(ext, data, [], pad, 0, fp)

def writeDir(data, exclude, pad, fp):
    for ext in dir(data):
        writeExt(ext, data, exclude, pad, 0, fp)

def writeQuoted(arg, fp):
    typ = type(arg)
    if typ == int or typ == float or typ == bool:
        fp.write("%s" % arg)
    elif typ == str:
        fp.write("'%s'"% stringQuote(arg))
    elif len(arg) > 1:
        c = '['
        for elt in arg:
            fp.write(c)
            writeQuoted(elt, fp)
            c = ','
        fp.write("]")
    else:
        raise MHError("Unknown property %s %s" % (arg, typ))
        fp.write('%s' % arg)

def stringQuote(string):
    s = ""
    for c in string:
        if c == '\\':
            s += "\\\\"
        elif c == '\"':
            s += "\\\""
        elif c == '\'':
            s += "\\\'"
        else:
            s += c
    return s


#
#    writeExt(ext, data, exclude, pad, depth, fp):
#

def writeExt(ext, data, exclude, pad, depth, fp):
    if hasattr(data, ext):
        writeValue(ext, getattr(data, ext), exclude, pad, depth, fp)

#
#    writeValue(ext, arg, exclude, pad, depth, fp):
#

excludeList = [
    'bl_rna', 'fake_user', 'id_data', 'rna_type', 'name', 'tag', 'users', 'type'
]

def writeValue(ext, arg, exclude, pad, depth, fp):
    if (len(str(arg)) == 0 or
        arg == None or
        arg == [] or
        ext[0] == '_' or
        ext in excludeList or
        ext in exclude):
        return

    if ext == 'end':
        print("RENAME end", arg)
        ext = '\\ end'

    typ = type(arg)
    if typ == int:
        fp.write("%s%s %d ;\n" % (pad, ext, arg))
    elif typ == float:
        fp.write("%s%s %.3f ;\n" % (pad, ext, arg))
    elif typ == bool:
        fp.write("%s%s %s ;\n" % (pad, ext, arg))
    elif typ == str:
        fp.write("%s%s '%s' ;\n" % (pad, ext, stringQuote(arg.replace(' ','_'))))
    elif typ == list:
        fp.write("%s%s List\n" % (pad, ext))
        n = 0
        for elt in arg:
            writeValue("[%d]" % n, elt, [], pad+"  ", depth+1, fp)
            n += 1
        fp.write("%send List\n" % pad)
    elif typ == Vector:
        c = '('
        fp.write("%s%s " % (pad, ext))
        for elt in arg:
            fp.write("%s%.3f" % (c,elt))
            c = ','
        fp.write(") ;\n")
    else:
        try:
            r = arg[0]
            g = arg[1]
            b = arg[2]
        except:
            return
        if (type(r) == float) and (type(g) == float) and (type(b) == float):
            fp.write("%s%s (%.4f,%.4f,%.4f) ;\n" % (pad, ext, r, g, b))
            print(ext, arg)
    return

###################################################################################
#
#   Boundary parts
#
###################################################################################

def examineBoundary(ob, scn):
    verts = ob.data.vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    vnums = getBodyPartVerts(scn)
    for m,n in vnums:
        verts[m].select = True
        verts[n].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    return


def getBodyPartVerts(scn):
    if scn.MCBodyPart == 'Custom':
        return (
            (scn.MCCustomX1, scn.MCCustomX2),
            (scn.MCCustomY1, scn.MCCustomY2),
            (scn.MCCustomZ1, scn.MCCustomZ2)
            )
    else:
        return theSettings.bodyPartVerts[scn.MCBodyPart]

###################################################################################
#
#   Z depth
#
###################################################################################

#
#   getZDepthItems():
#   setZDepth(scn):
#

ZDepth = {
    "Body" : 0,
    "Underwear and lingerie" : 20,
    "Socks and stockings" : 30,
    "Shirt and trousers" : 40,
    "Sweater" : 50,
    "Indoor jacket" : 60,
    "Shoes and boots" : 70,
    "Coat" : 80,
    "Backpack" : 100,
    }

MinZDepth = 31
MaxZDepth = 69

def setZDepthItems():
    global ZDepthItems
    zlist = sorted(list(ZDepth.items()), key=lambda z: z[1])
    ZDepthItems = []
    for (name, val) in zlist:
        ZDepthItems.append((name,name,name))
    return

def setZDepth(scn):
    scn.MCZDepth = 50 + int((ZDepth[scn.MCZDepthName]-50)/2.6)
    return


###################################################################################
#
#   Utilities
#
###################################################################################
#
#    printVertNums(context):
#

def printVertNums(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Verts in ", ob)
    for v in ob.data.vertices:
        if v.select:
            print(v.index)
    print("End verts")
    bpy.ops.object.mode_set(mode='EDIT')

#
#   deleteHelpers(context):
#

def deleteHelpers(context):
    if theSettings is None:
        return
    ob = context.object
    scn = context.scene
    #if not ob.MhHuman:
    #    return
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    nmax = theSettings.vertices[scn.MCKeepVertsUntil][1]
    for v in ob.data.vertices:
        if v.index >= nmax:
            v.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Vertices deleted")
    return

#
#   autoVertexGroups(ob):
#

def autoVertexGroupsIfNecessary(ob, type='Selected', htype='Tights'):
    if len(ob.vertex_groups) == 0:
        print("Found no vertex groups for %s." % ob)
        autoVertexGroups(ob, type, htype)


def autoVertexGroups(ob, type, htype):
    if ob.vertex_groups:
        bpy.ops.object.vertex_group_remove(all=True)

    mid = ob.vertex_groups.new("Mid")
    left = ob.vertex_groups.new("Left")
    right = ob.vertex_groups.new("Right")
    if isOkHuman(ob):
        ob.vertex_groups.new("Delete")
        verts = getHumanVerts(ob.data, type, htype)
    else:
        verts = ob.data.vertices
    for v in verts.values():
        vn = v.index
        if v.co[0] > 0.01:
            left.add([vn], 1.0, 'REPLACE')
        elif v.co[0] < -0.01:
            right.add([vn], 1.0, 'REPLACE')
        else:
            mid.add([vn], 1.0, 'REPLACE')
            if (ob.MhHuman and
                (theSettings is None or vn < theSettings.nTotalVerts)):
                left.add([vn], 1.0, 'REPLACE')
                right.add([vn], 1.0, 'REPLACE')
    if ob.MhHuman:
        print("Vertex groups auto assigned to human %s, part %s." % (ob, type.lower()))
    else:
        print("Vertex groups auto assigned to clothing %s" % ob)


def getHumanVerts(me, type, htype):
    if type == 'Selected':
        verts = {}
        for v in me.vertices:
            if v.select:
                verts[v.index] = v
    elif type == 'Helpers':
        verts = getHelperVerts(me, htype)
    elif type == 'Body':
        verts = {}
        addBodyVerts(me, verts)
    elif type == 'All':
        verts = getHelperVerts(me, 'All')
        addBodyVerts(me, verts)
    else:
        raise RuntimeError("Bug getHumanVerts %s %s" % (type, htype))
    return verts


def getHelperVerts(me, htype):
    verts = {}
    vnums = theSettings.vertices
    if htype == 'All':
        checkEnoughVerts(me, htype, theSettings.clothesVerts[0])
        for vn in range(theSettings.clothesVerts[0], theSettings.clothesVerts[1]):
            verts[vn] = me.vertices[vn]
    elif htype in vnums.keys():
        checkEnoughVerts(me, htype, vnums[htype][0])
        for vn in range(vnums[htype][0], vnums[htype][1]):
            verts[vn] = me.vertices[vn]
    elif htype == 'Coat':
        checkEnoughVerts(me, htype, vnums["Tights"][0])
        zmax = -1e6
        for vn in theSettings.topOfSkirt:
            zn = me.vertices[vn].co[2]
            if zn > zmax:
                zmax = zn
        for vn in range(vnums["Skirt"][0], vnums["Skirt"][1]):
            verts[vn] = me.vertices[vn]
        for vn in range(vnums["Tights"][0], vnums["Tights"][1]):
            zn = me.vertices[vn].co[2]
            if zn > zmax:
                verts[vn] = me.vertices[vn]
    else:
        raise MHError("Unknown helper type %s" % htype)

    return verts


def checkEnoughVerts(me, htype, first):
    if len(me.vertices) < first:
        raise MHError("Mesh has too few vertices for selecting %s" % (htype))


def addBodyVerts(me, verts):
    meFaces = getFaces(me)
    for f in meFaces:
        if len(f.vertices) < 4:
            continue
        for vn in f.vertices:
            if vn < theSettings.nBodyVerts:
                verts[vn] = me.vertices[vn]
    return


def selectHumanPart(ob, btype, htype):
    if isOkHuman(ob):
        clearSelection()
        verts = getHumanVerts(ob.data, btype, htype)
        for v in verts.values():
            v.select = True
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        raise MHError("Object %s is not a human" % ob.name)


#
#   checkAndVertexDiamonds(context, ob):
#

def clearSelection():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def checkAndUnVertexDiamonds(context, ob):
    print("Unvertex diamonds in %s" % ob)
    scn = context.scene
    bpy.ops.object.mode_set(mode='OBJECT')
    scn.objects.active = ob
    clearSelection()
    me = ob.data
    nverts = len(me.vertices)

    if not isOkHuman(ob):
        vertlines = ""
        for n in getLastVertices():
            vertlines += ("\n  %d" % n)
        raise MHError(
            "Base object %s has %d vertices. \n" % (ob, nverts) +
            "The number of verts in an %s MH human must be one of:" % theSettings.baseMesh +
            vertlines)

    joints = theSettings.vertices["Joints"]
    if nverts <= joints[0]:
        return
    for vn in range(joints[0], joints[1]):
        me.vertices[vn].select = True
    lastHair = theSettings.vertices["Hair"][1]
    if nverts > lastHair:
        for vn in range(lastHair, theSettings.nTotalVerts):
            me.vertices[vn].select = True

    bpy.ops.object.mode_set(mode='EDIT')
    for gn in range(len(ob.vertex_groups)):
        ob.vertex_groups.active_index = gn
        bpy.ops.object.vertex_group_remove_from()
    bpy.ops.object.mode_set(mode='OBJECT')
    return


#
#   readDefaultSettings(context):
#   saveDefaultSettings(context):
#

def settingsFile(name):
    outdir = os.path.join(getMHBlenderDirectory(), "settings")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return os.path.join(outdir, "make_clothes.%s" % name)


def readDefaultSettings(context):
    fname = settingsFile("settings")
    try:
        fp = open(fname, "rU")
    except FileNotFoundError:
        print("Did not find %s. Using default settings" % fname)
        return

    scn = context.scene
    for line in fp:
        words = line.split()
        if len(words) < 3:
            continue
        prop = words[0]
        type = words[1]
        if type == "int":
            scn[prop] = int(words[2])
        elif type == "float":
            scn[prop] = float(words[2])
        elif type == "str":
            string = words[2]
            for word in words[3:]:
                string += " " + word
            scn[prop] = string
    fp.close()
    return


def saveDefaultSettings(context):
    fname = settingsFile("settings")
    fp = mc.openOutputFile(fname)
    scn = context.scene
    for (prop, value) in scn.items():
        if prop[0:2] == "MC":
            if type(value) == int:
                fp.write("%s int %s\n" % (prop, value))
            elif type(value) == float:
                fp.write("%s float %.4f\n" % (prop, value))
            elif type(value) == str:
                fp.write("%s str %s\n" % (prop, value))
    fp.close()
    return

#
#   Test clothese
#

def testMhcloFile(context, filepath):
    from maketarget.proxy import CProxy
    from maketarget.import_obj import importObj

    hum = context.object
    if not isOkHuman(hum):
        raise MHError("%s is not a human mesh" % hum.name)

    pxy = CProxy()
    pxy.read(filepath)
    pxy = importObj(pxy.obj_file, context, addBasisKey=False)
    pxy.update(hum.data.vertices, pxy.data.vertices)


class VIEW3D_OT_TestProxyButton(bpy.types.Operator):
    bl_idname = "mhpxy.test_clothes"
    bl_label = "Test Proxy"
    bl_description = "Load a mhc2 file to object"
    bl_options = {'UNDO'}

    filename_ext = ".mhc2"
    filter_glob = StringProperty(default="*.mhc2", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for mhc2 file",
        maxlen= 1024, default= "")

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            testMhcloFile(context, self.properties.filepath)
        except MHError:
            handleMHError(context)
        print("%s loaded" % self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#
#   init():
#

MCIsInited = False

def init():
    global MCIsInited
    import maketarget
    if not maketarget.maketarget.MTIsInited:
        maketarget.maketarget.init()

    bpy.types.Scene.MCBodyType = EnumProperty(
        items = [('None', 'Base Mesh', 'None'),
                 ('caucasian-male-young', 'Average Male', 'caucasian-male-young'),
                 ('caucasian-female-young', 'Average Female', 'caucasian-female-young'),
                 ('caucasian-male-child', 'Average Child', 'caucasian-male-child'),
                 ('caucasian-male-baby', 'Average Baby', 'caucasian-male-baby'),

                 ('h-None', 'Base Mesh  With Helpers', 'None'),
                 ('h-caucasian-male-young', 'Average Male With Helpers', 'caucasian-male-young'),
                 ('h-caucasian-female-young', 'Average Female With Helpers', 'caucasian-female-young'),
                 ('h-caucasian-male-child', 'Average Child With Helpers', 'caucasian-male-child'),
                 ('h-caucasian-male-baby', 'Average Baby With Helpers', 'caucasian-male-baby'),
                 ],
        description = "Body Type To Load",
    default='None')

    bpy.types.Scene.MCUseShearing = BoolProperty(
        name="Use Shearing",
        description="Allow bounding box to be sheared",
        default=False)

    bpy.types.Scene.MCUseBoundaryMirror = BoolProperty(
        name="Mirror Bounding Box",
        description="Mirror the bounding box for Left/Right vertex groups",
        default=False)


    bpy.types.Scene.MCMaskLayer = IntProperty(
        name="Mask UV layer",
        description="UV layer for mask, starting with 0",
        default=0)

    bpy.types.Scene.MCTextureLayer = IntProperty(
        name="Texture UV layer",
        description="UV layer for textures, starting with 0",
        default=0)

    bpy.types.Scene.MCAllUVLayers = BoolProperty(
        name="All UV layers",
        description="Include all UV layers in export",
        default=False)

    bpy.types.Scene.MCThreshold = FloatProperty(
        name="Threshold",
        description="Minimal allowed value of normal-vector dot product",
        min=-1.0, max=0.0,
        default=-0.2)

    bpy.types.Scene.MCListLength = IntProperty(
        name="List length",
        description="Max number of verts considered",
        default=4)

    bpy.types.Scene.MCUseInternal = BoolProperty(
        name="Use Internal",
        description="Access internal settings",
        default=False)

    bpy.types.Scene.MCLogging = BoolProperty(
        name="Log",
        description="Write a log file for debugging",
        default=False)

    bpy.types.Scene.MCMHVersion = EnumProperty(
        items = [("hm08", "hm08", "hm08"), ("None", "None", "None")],
        name="MakeHuman mesh version",
        description="The human is the MakeHuman base mesh",
        default="hm08")

    bpy.types.Scene.MCSelfClothed = BoolProperty(default=False)

    enums = []
    for name in theSettings.vertices.keys():
        enums.append((name,name,name))

    bpy.types.Scene.MCKeepVertsUntil = EnumProperty(
        items = enums,
        name="Keep verts untils",
        description="Last clothing to keep vertices for",
        default="Tights")

    bpy.types.Scene.MCScaleUniform = BoolProperty(
        name="Uniform Scaling",
        description="Scale offset uniformly in the XYZ directions",
        default=False)

    bpy.types.Scene.MCScaleCorrect = FloatProperty(
        name="Scale Correction",
        default=1.0,
        min=0.5, max=1.5)

    bpy.types.Scene.MCBodyPart = EnumProperty(
        name = "Body Part",
        items = [('Head', 'Head', 'Head'),
                 ('Torso', 'Torso', 'Torso'),
                 ('Arm', 'Arm', 'Arm'),
                 ('Hand', 'Hand', 'Hand'),
                 ('Leg', 'Leg', 'Leg'),
                 ('Foot', 'Foot', 'Foot'),
                 ('Eye', 'Eye', 'Eye'),
                 ('Genital', 'Genital', 'Genital'),
                 ('Teeth', 'Teeth', 'Teeth'),
                 ('Body', 'Body', 'Body'),
                 ('Custom', 'Custom', 'Custom'),
                 ],
        default='Head')

    x,y,z = theSettings.bodyPartVerts['Body']

    bpy.types.Scene.MCCustomX1 = IntProperty(name="X1", default=x[0])
    bpy.types.Scene.MCCustomX2 = IntProperty(name="X2", default=x[1])
    bpy.types.Scene.MCCustomY1 = IntProperty(name="Y1", default=y[0])
    bpy.types.Scene.MCCustomY2 = IntProperty(name="Y2", default=y[1])
    bpy.types.Scene.MCCustomZ1 = IntProperty(name="Z1", default=z[0])
    bpy.types.Scene.MCCustomZ2 = IntProperty(name="Z2", default=z[1])

    setZDepthItems()
    bpy.types.Scene.MCZDepthName = EnumProperty(
        name = "Proxy Type",
        items = ZDepthItems,
        default='Sweater')

    bpy.types.Scene.MCZDepth = IntProperty(
        name="Z depth",
        description="Location in the Z buffer",
        default=ZDepth['Sweater'],
        min = MinZDepth,
        max = MaxZDepth)

    bpy.types.Scene.MCAuthor = StringProperty(
        name="Author",
        default="Unknown",
        maxlen=32)

    bpy.types.Scene.MCLicense = StringProperty(
        name="License",
        default="AGPL3 (see also http://www.makehuman.org/doc/node/external_tools_license.html)",
        maxlen=256)

    bpy.types.Scene.MCHomePage = StringProperty(
        name="HomePage",
        default="http://www.makehuman.org/",
        maxlen=256)

    bpy.types.Scene.MCTag1 = StringProperty(
        name="Tag1",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag2 = StringProperty(
        name="Tag2",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag3 = StringProperty(
        name="Tag3",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag4 = StringProperty(
        name="Tag4",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag5 = StringProperty(
        name="Tag5",
        default="",
        maxlen=32)

    folder = os.path.dirname(__file__)
    proxyDir = os.path.join(folder, "../import_runtime_mhx2/data/hm8/")
    bpy.types.Scene.MCProxyDir = StringProperty(
        name="Proxy Directory",
        default=proxyDir,
        maxlen=32)

    MCIsInited = True

