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
# Coding Standards: See http://www.makehuman.org/node/165

"""
Abstract


"""

import bpy
from bpy.props import *
from .drivers import *

#------------------------------------------------------------------------
#    Setup: Add and remove hide drivers
#------------------------------------------------------------------------

class VIEW3D_OT_MhxAddHidersButton(bpy.types.Operator):
    bl_idname = "mhdat.add_hide_drivers"
    bl_label = "Add Visibility Drivers"
    bl_description = "Control visibility with rig property. For file linking."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and
                not rig.MhxVisibilityDrivers
               )

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        initRnaProperties(rig)
        for ob in meshes:
            addHideDriver(ob, rig)
            ob.MhxVisibilityDrivers = True
        rig.MhxVisibilityDrivers = True
        return{'FINISHED'}


def addHideDriver(clo, rig):
    cloname = clo.name.rsplit(".",1)[0]
    prop = "Mhh%s" % cloname
    rig[prop] = True
    rig["_RNA_UI"][prop] = {
        "type" : 'BOOLEAN',
        "min" : 0, "max" : 1,
        "description" : "Show %s" % clo.name}
    addDriver(rig, clo, "hide", prop, expr = "not(x)")
    addDriver(rig, clo, "hide_render", prop, expr = "not(x)")
    mod = getMaskModifier(cloname, rig)
    if mod:
        addDriver(rig, mod, "show_viewport", prop, expr = "x")
        addDriver(rig, mod, "show_render", prop, expr = "x")


def getMaskModifier(cloname, rig):
    try:
        cloname = cloname.split(":",1)[1]
    except IndexError:
        return None
    for ob in rig.children:
        for mod in ob.modifiers:
            if mod.type == 'MASK':
                try:
                    modname = mod.name.split(":",1)[1]
                except IndexError:
                    continue
                if modname == cloname:
                    return mod
    return None


class VIEW3D_OT_MhxRemoveHidersButton(bpy.types.Operator):
    bl_idname = "mhdat.remove_hide_drivers"
    bl_label = "Remove Visibility Drivers"
    bl_description = "Remove ability to control visibility from rig property"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxVisibilityDrivers)

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        for ob in meshes:
            removeHideDrivers(ob, rig)
            ob.MhxVisibilityDrivers = False
        if context.object == rig:
            rig.MhxVisibilityDrivers = False
        return{'FINISHED'}


def removeHideDrivers(clo, rig):
    deleteRigProperty(rig, "Mhh%s" % clo.name)
    clo.driver_remove("hide")
    clo.driver_remove("hide_render")
    mod = getMaskModifier(clo, rig)
    if mod:
        mod.driver_remove("show_viewport")
        mod.driver_remove("show_render")



