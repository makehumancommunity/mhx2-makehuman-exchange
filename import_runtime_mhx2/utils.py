# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014-2018
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
from mathutils import Vector
from .error import MhxError

#-------------------------------------------------------------
#   Blender 2.8 compatibility
#-------------------------------------------------------------

if bpy.app.version < (2,80,0):

    HideViewport = "hide"
    DrawType = "draw_type"
    ShowXRay = "show_x_ray"

    def getCollection(context):
        return context.scene

    def getSceneObjects(context):
        return context.scene.objects

    def getSelected(ob):
        return ob.select

    def setSelected(ob, value):
        ob.select = value

    def setActiveObject(context, ob):
        scn = context.scene
        scn.objects.active = ob
        scn.update()

    def putOnHiddenLayer(ob, coll=None, hidden=None):
        ob.layers = 19*[False] + [True]

    def createHiddenCollection(context):
        return context.scene

    def inSceneLayer(context, ob):
        scn = context.scene
        for n in range(len(scn.layers)):
            if (ob.layers[n] and scn.layers[n]):
                return True
        return False

    def activateObject(context, ob):
        scn = context.scene
        for ob1 in scn.objects:
            ob1.select = False
        ob.select = True
        scn.objects.active = ob

    def Mult2(x, y):
        return x * y

    def Mult3(x, y, z):
        return x * y * z

    def Mult4(x, y, z, u):
        return x * y * z * u

    def splitLayout(layout, factor):
        return layout.split(factor)

    def deleteObject(context, ob):
        for scn in bpy.data.scenes:
            if ob in scn.objects.values():
                scn.objects.unlink(ob)
        if ob.users == 0:
            bpy.data.objects.remove(ob)
            del ob

else:

    HideViewport = "hide_viewport"
    DrawType = "display_type"
    ShowXRay = "show_in_front"

    def getCollection(context):
        return context.scene.collection

    def getSceneObjects(context):
        return context.view_layer.objects

    def getSelected(ob):
        return ob.select_get()

    def setSelected(ob, value):
        ob.select_set(value)

    def setActiveObject(context, ob):
        vly = context.view_layer
        vly.objects.active = ob
        vly.update()

    def putOnHiddenLayer(ob, coll=None, hidden=None):
        if coll:
            coll.objects.unlink(ob)
        if hidden:
            hidden.objects.link(ob)

    def createHiddenCollection(context):
        coll = bpy.data.collections.new(name="Hidden")
        context.scene.collection.children.link(coll)
        coll.hide_viewport = True
        coll.hide_render = True
        return coll

    def inSceneLayer(context, ob):
        coll = context.scene.collection
        return (ob in coll.objects.values())

    def activateObject(context, ob):
        scn = context.scene
        for ob1 in scn.collection.objects:
            ob1.select_set(False)
        ob.select_set(True)
        context.view_layer.objects.active = ob

    def printActive(name, context):
        coll = context.scene.collection
        print(name, context.object, coll)
        sel = [ob for ob in coll.objects if ob.select_get()]
        print("  ", sel)

    def Mult2(x, y):
        return x @ y

    def Mult3(x, y, z):
        return x @ y @ z

    def Mult4(x, y, z, u):
        return x @ y @ z @ u

    def splitLayout(layout, factor):
        return layout.split(factor=factor)

    def deleteObject(context, ob):
        for coll in bpy.data.collections:
            if ob in coll.objects.values():
                coll.objects.unlink(ob)
        if True or ob.users == 0:
            bpy.data.objects.remove(ob)
            del ob

#-------------------------------------------------------------
#
#-------------------------------------------------------------

def getOriginalName(ob):
    words = ob.name.rsplit(".",1)
    if len(words) == 1:
        return words[0]
    elif len(words[1]) == 3:    # .001
        try:
            int(words[1])
            return words[0]
        except ValueError:
            return ob.name
    else:
        return ob.name


def isBody(ob):
    name = getOriginalName(ob)
    return (name.split(":")[-1] in ["Body", "Base", "Proxy"])

def getRigName(ob):
    name = getOriginalName(ob)
    return name.split(":")[0]

def getProxyName(ob):
    name = getOriginalName(ob)
    return name.split(":")[1]

def getMaterialName(ob):
    name = getOriginalName(ob)
    return name.split(":")[2]

def getDeleteName(ob):
    return "Delete:" + getProxyName(ob)

def isDeleteVGroup(vgrp):
    return (vgrp.name[0:7] == "Delete:")

def getVGProxyName(string):
    return string.split(":",1)[1]

def getClothesName(clo):
    name = getOriginalName(clo)
    try:
        return name.split(":",1)[1]
    except IndexError:
        return None


def getArmature(ob):
    if ob.type == 'MESH':
        return ob.parent
    elif ob.type == 'ARMATURE':
        return ob


def zup(co):
    return Vector((co[0], -co[2], co[1]))

def zup2(co, s):
    return Vector((s[0]*co[0], -s[2]*co[2], s[1]*co[1]))


def multiply(list1, list2):
    [(list1[n] and list2[n]) for n in range(len(list1))]


def updateScene(context):
    scn = context.scene
    scn.frame_current = scn.frame_current

# ---------------------------------------------------------------------
#   Global variable that holds the loaded json struct for the
#   current human.
# ---------------------------------------------------------------------

def setMhHuman(human):
    global theMhHuman
    theMhHuman = human

def getMhHuman(ob=None):
    global theMhHuman
    try:
        theMhHuman
    except:
        raise MhxError("No saved human")
    if ob and theMhHuman["uuid"] != ob.MhxUuid:
        raise MhxError("Saved human:\n %s\ndoes not match current object:\n %s" % (theMhHuman["name"], ob.name))
    return theMhHuman

# ---------------------------------------------------------------------
#   Debug flags
# ---------------------------------------------------------------------

AutoWeight = False
