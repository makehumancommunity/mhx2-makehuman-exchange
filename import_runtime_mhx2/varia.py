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
from .drivers import *


#------------------------------------------------------------------------
#    Setup: Add and remove groups
#------------------------------------------------------------------------

class MHX_OT_MhxAddGroups(bpy.types.Operator):
    bl_idname = "mhx2.add_groups"
    bl_label = "Add Groups"
    bl_description = "Add meshes to rig group. For file linking."
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        if rig:
            addGroup(rig, rig.name)
            for ob in meshes:
                addGroup(ob, rig.name)
        return{'FINISHED'}


def addGroup(ob, gname):
    group = None
    for grp in ob.groups:
        if grp.name = gname:
            group = grp
            break
    if not group:
        group = ob.groups.new(gname)

#----------------------------------------------------------
#   Initialize
#----------------------------------------------------------

classes = [
    MHX_OT_MhxAddGroups,
]

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)