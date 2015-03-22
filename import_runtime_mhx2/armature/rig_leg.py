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

from .flags import *
from .rig_joints import *

Joints = [
    ('l-toe-2',             'p', ('l-foot-2', 'l-foot-1', 'l-foot-2')),
    ('r-toe-2',             'p', ('r-foot-2', 'r-foot-1', 'r-foot-2')),
]


HeadsTails = {
    'thigh.L' :            ('l-upper-leg', 'l-knee'),
    'shin.L' :             ('l-knee', 'l-ankle'),
    'foot.L' :             ('l-ankle', 'l-foot-1'),
    'toe.L' :              ('l-foot-1', 'l-toe-2'),

    'thigh.R' :            ('r-upper-leg', 'r-knee'),
    'shin.R' :             ('r-knee', 'r-ankle'),
    'foot.R' :             ('r-ankle', 'r-foot-1'),
    'toe.R' :              ('r-foot-1', 'r-toe-2'),

    'toe_end.L' :          ('l-toe-2', ('l-toe-2', (0,0,0.2))),
    'toe_end.R' :          ('r-toe-2', ('r-toe-2', (0,0,0.2))),
}

Planes = {
    "PlaneLeg.L" :         ('l-upper-leg', 'l-knee-tip', 'l-ankle'),
    "PlaneFoot.L" :        ('l-ankle', 'l-toe-2', 'l-foot-1'),
    "PlaneLeg.R" :         ('r-upper-leg', 'r-knee-tip', 'r-ankle'),
    "PlaneFoot.R" :        ('r-ankle', 'r-toe-2', 'r-foot-1'),
}

Armature = {
    'thigh.L' :            ("PlaneLeg.L", 'hips', F_DEF, L_LLEGFK),
    'shin.L' :             ("PlaneLeg.L", 'thigh.L', F_DEF|F_CON, L_LLEGFK, P_YZX),
    'foot.L' :             ("PlaneFoot.L", 'shin.L', F_DEF|F_CON, L_LLEGFK, P_YZX),
    'toe.L' :              ("PlaneFoot.L", 'foot.L', F_DEF|F_CON, L_LLEGFK, P_YZX),

    'thigh.R' :            ("PlaneLeg.R", 'hips', F_DEF, L_RLEGFK),
    'shin.R' :             ("PlaneLeg.R", 'thigh.R', F_DEF|F_CON, L_RLEGFK, P_YZX),
    'foot.R' :             ("PlaneFoot.R", 'shin.R', F_DEF|F_CON, L_RLEGFK, P_YZX),
    'toe.R' :              ("PlaneFoot.R", 'foot.R', F_DEF|F_CON, L_RLEGFK, P_YZX),
}

RotationLimits = {
    'thigh.L' :         (-160,90, -45,45, -140,80),
    'thigh.R' :         (-160,90, -45,45, -80,140),
    'shin.L' :          (0,170, -40,40, 0,0),
    'shin.R' :          (0,170, -40,40, 0,0),
    'foot.L' :          (-90,45, -30,30, -30,30),
    'foot.R' :          (-90,45, -30,30, -30,30),
    'toe.L' :           (-20,60, 0,0, 0,0),
    'toe.R' :           (-20,60, 0,0, 0,0),

}

CustomShapes = {
    'thigh.L' :         'GZM_Circle025',
    'thigh.R' :         'GZM_Circle025',
    'shin.L' :          'GZM_Circle025',
    'shin.R' :          'GZM_Circle025',
    'foot.L' :          'GZM_Foot',
    'foot.R' :          'GZM_Foot',
    'toe.L' :           'GZM_Toe',
    'toe.R' :           'GZM_Toe',
}

Constraints = {}

