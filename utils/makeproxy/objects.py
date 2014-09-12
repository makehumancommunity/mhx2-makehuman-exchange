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

"""

from makeclothes import mc

#
#   Global variables
#

Epsilon = 1e-4

theSettings = mc.settings["hm08"]

#
#   BMesh
#


def getFaces(me):
    global BMeshAware
    try:
        BMeshAware = True
        return me.polygons
    except:
        BMeshAware = False
        return me.faces


#
#   isProxy(ob):
#   getHuman(context):
#   getProxy(context):
#   getObjectPair(context):
#

def isProxy(ob):
    return ((ob.type == 'MESH') and not isOkHuman(ob))


def isOkHuman(ob):
    if not ob.MhHuman:
        return False
    if not theSettings:
        return True
    nverts = len(ob.data.vertices)
    if nverts in getLastVertices():
        return True
    else:
        ob.MhHuman = False
        return False


def getLastVertices():
    vlist = [ vs[1] for vs in theSettings.vertices.values()]
    vlist.append(theSettings.nTotalVerts)
    vlist.sort()
    return vlist


def getHuman(context):
    for ob in context.scene.objects:
        if ob.select and isOkHuman(ob):
            return ob
    raise MHError("No human selected")


def getProxy(context):
    for ob in context.scene.objects:
        if ob.select and isProxy(ob):
            return ob
    for ob in context.scene.objects:
        if ob.select and ob.type == 'MESH' and not isOkHuman(ob):
            return ob
    raise MHError("No clothing selected")


def getObjectPair(context):
    human = None
    clothing = None
    scn = context.scene
    for ob in scn.objects:
        if ob.select:
            if isOkHuman(ob):
                if human:
                    raise MHError("Two humans selected: %s and %s" % (human.name, ob.name))
                else:
                    human = ob
            elif ob.type == 'MESH':
                if clothing:
                    raise MHError("Two pieces of clothing selected: %s and %s" % (clothing.name, ob.name))
                else:
                    clothing = ob
    if not human:
        raise MHError("No human selected")
    if not clothing:
        raise MHError("No clothing selected")
    return (human, clothing)

