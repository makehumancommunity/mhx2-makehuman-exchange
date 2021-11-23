# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script Copyright (C) Thomas Larsson 2014 - 2020
#  Script Copyright (C) MakeHuman Community 2020
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
from .drivers import *


#------------------------------------------------------------------------
#    Setup: Add and remove groups
#------------------------------------------------------------------------

class MHX_OT_MhxAddCollections(bpy.types.Operator):
    bl_idname = "mhx2.add_collections"
    bl_label = "Add Collections"
    bl_description = "Add meshes to rig group. For file linking."
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        if rig:
            addCollection(rig, rig.name)
            for ob in meshes:
                addCollection(ob, rig.name)
        return{'FINISHED'}


def addCollection(ob, cname):
    collection = None
    for col in ob.collections:
        if col.name = cname:
            collection = col
            break
    if not collection:
        collection = ob.collections.new(cname)

#----------------------------------------------------------
#   Initialize
#----------------------------------------------------------

classes = [
    MHX_OT_MhxAddCollections,
]

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)
