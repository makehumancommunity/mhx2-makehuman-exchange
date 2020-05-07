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
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

if "bpy" in locals():
    import importlib
    importlib.reload(flags)
    importlib.reload(utils)
    importlib.reload(rig_joints)
    #importlib.reload(rig_bones)
    importlib.reload(rig_spine)
    importlib.reload(rig_arm)
    importlib.reload(rig_leg)
    importlib.reload(rig_hand)
    #importlib.reload(rig_muscle)
    importlib.reload(rig_face)
    importlib.reload(rig_control)
    importlib.reload(rig_merge)
    importlib.reload(rig_panel)
    importlib.reload(rig_rigify)
    importlib.reload(parser)
    importlib.reload(constraints)
    importlib.reload(rigify)
    importlib.reload(build)
    importlib.reload(rerig)
else:
    from . import flags
    from . import utils
    from . import rig_joints
    #from . import rig_bones
    from . import rig_spine
    from . import rig_arm
    from . import rig_leg
    from . import rig_hand
    #from . import rig_muscle
    from . import rig_face
    from . import rig_control
    from . import rig_merge
    from . import rig_panel
    from . import rig_rigify
    from . import parser
    from . import constraints
    from . import rigify
    from . import build
    from . import rerig

import bpy
print("MHX2 armature loaded")
