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

from mathutils import Vector
from .error import MhxError

def isBody(ob):
    return (ob.name.split(":")[-1] == "Body")

def getRigName(ob):
    return ob.name.split(":")[0]

def getProxyName(ob):
    return ob.name.split(":")[1]

def getMaterialName(ob):
    return ob.name.split(":")[2]

def getDeleteName(ob):
    return "Delete:" + getProxyName(ob)

def isDeleteVGroup(vgrp):
    return (vgrp.name[0:7] == "Delete:")

def getVGProxyName(string):
    return string.split(":",1)[1]

def getClothesName(clo):
    cloname = clo.name.rsplit(".",1)[0]
    try:
        return cloname.split(":",1)[1]
    except IndexError:
        return None


def zup(co):
    return Vector((co[0], -co[2], co[1]))

def zup2(co, s):
    return Vector((s[0]*co[0], -s[2]*co[2], s[1]*co[1]))


def multiply(list1, list2):
    [(list1[n] and list2[n]) for n in range(len(list1))]


def updateScene(context):
    scn = context.scene
    scn.frame_current = scn.frame_current


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

