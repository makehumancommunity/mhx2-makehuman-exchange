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
    ('spine-23',            'l', ((0.5, 'spine-2'), (0.5, 'spine-3'))),

    ('pubis',               'vl', ((0.9, 4341), (0.1, 4250))),

    ('penis-1',             'vl', ((0.5, 15152), (0.5, 15169))),
    ('penis-2',             'vl', ((0.5, 15272), (0.5, 15274))),
    ('penis-3',             'vl', ((0.5, 15320), (0.5, 15326))),
    ('penis-4',             'v', 15319),

    ('l-scrotum-1',         'vl', ((0.5, 15216), (0.5, 15217))),
    ('r-scrotum-1',         'vl', ((0.5, 15238), (0.5, 15252))),
    ('l-scrotum-2',         'v', 15230),
    ('r-scrotum-2',         'v', 15231),

]


HeadsTails = {
    'hips' :               ('pelvis', 'spine-3'),
    'spine' :              ('spine-3', 'spine-23'),
    'spine-1' :            ('spine-23', 'spine-2'),
    'chest' :              ('spine-2', 'spine-1'),
    'chest-1' :            ('spine-1', 'neck'),
    'neck' :               ('neck', 'head'),
    'head' :               ('head', 'head-2'),

    'skull' :              ('head-2', ('head-2', (0,0.2,0))),

    'penis_1' :            ('penis-1', 'penis-2'),
    'penis_2' :            ('penis-2', 'penis-3'),
    'penis_3' :            ('penis-3', 'penis-4'),

    'scrotum.L' :          ('l-scrotum-1', 'l-scrotum-2'),
    'scrotum.R' :          ('r-scrotum-1', 'r-scrotum-2'),
}

Planes = {
}

Armature = {
    'hips' :               (0, None, F_DEF, L_UPSPNFK),
    'spine' :              (0, 'hips', F_DEF|F_CON, L_UPSPNFK),
    'spine-1' :            (0, 'spine', F_DEF|F_CON, L_UPSPNFK),
    'chest' :              (0, 'spine-1', F_DEF|F_CON, L_UPSPNFK),
    'chest-1' :            (0, 'chest', F_DEF|F_CON, L_UPSPNFK),
    'neck' :               (0, 'chest-1', F_DEF|F_CON, L_UPSPNFK),
    'head' :               (0, 'neck', F_DEF|F_CON, L_UPSPNFK),
}

# Terminators needed by OpenSim

TerminatorArmature = {
    'skull' :               (0, 'head', F_CON, L_HELP),
    'toe_end.L' :           (0, 'toe.L', F_CON, L_HELP),
    'toe_end.R' :           (0, 'toe.R', F_CON, L_HELP),
}

PenisArmature = {
    'penis_1' :             (0, 'hips', F_DEF|F_SCALE|F_NOLOCK, L_TWEAK),
    'penis_2' :             (0, 'penis_1', F_DEF|F_SCALE|F_CON, L_TWEAK),
    'penis_3' :             (0, 'penis_2', F_DEF|F_SCALE|F_CON, L_TWEAK),
    'scrotum.L' :           (0, 'hips', F_DEF|F_SCALE|F_NOLOCK, L_TWEAK),
    'scrotum.R' :           (0, 'hips', F_DEF|F_SCALE|F_NOLOCK, L_TWEAK),
}

RotationLimits = {
    'spine' :           (-30,30, -30,30, -30,30),
    'spine-1' :         (-30,30, -30,30, -30,30),
    'chest' :           (-20,20, 0,0, -20,20),
    'chest-1' :         (-20,20, 0,0, -20,20),
    'neck' :            (-45,45, -45,45, -60,60),
}

CustomShapes = {
    'root' :            'GZM_Root',
    'hips' :            'GZM_CrownHips',
    'spine' :           'GZM_CircleSpine',
    'spine-1' :         'GZM_CircleSpine',
    'chest' :           'GZM_CircleChest',
    'chest-1' :         'GZM_CircleChest',
    'neck' :            'GZM_Neck',
    'head' :            'GZM_Head',
}

Constraints = {}

