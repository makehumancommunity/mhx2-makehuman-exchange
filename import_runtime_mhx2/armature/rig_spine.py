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
    ("neck",                "vl", ((0.3, 809), (0.7, 1491))),
    ('neck-1',              'vl', ((0.5, 825), (0.5, 7536))),

    ('l-serratus-2',        'v', 8110),
    ('r-serratus-2',        'v', 1422),
    ('l-serratus-1',        'l', ((0.3, 'r-serratus-2'), (0.7, 'l-serratus-2'))),
    ('r-serratus-1',        'l', ((0.3, 'l-serratus-2'), (0.7, 'r-serratus-2'))),

    ('l-breast-1',          'v', 8535),
    ('r-breast-1',          'v', 1863),
    ('l-breast-2',          'v', 8542),
    ('r-breast-2',          'v', 1870),
    ('l-breast',            'l', ((0.5, 'l-breast-1'), (0.5, 'l-breast-2'))),
    ('r-breast',            'l', ((0.5, 'r-breast-1'), (0.5, 'r-breast-2'))),
    ('l-nipple',            'v', 8462),
    ('r-nipple',            'v', 1790),

    ('l-pect',        'l', ((0.2, 'spine-1'), (0.8, 'l-nipple'))),
    ('r-pect',        'l', ((0.2, 'spine-1'), (0.8, 'r-nipple'))),
    ('l-pect-ik',           'l', ((-0.1, 'spine-1'), (1.1, 'l-nipple'))),
    ('r-pect-ik',           'l', ((-0.1, 'spine-1'), (1.1, 'r-nipple'))),

    ('pubis',               'v', 4372),
    ('pubis-1',             'v', 4259),
    ('pubis-2',             'v', 4370),

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
    'neck' :               ('neck', 'neck-1'),
    'neck-1' :             ('neck-1', 'head'),
    'head' :               ('head', 'head-2'),

    'serratus.L' :     ('l-serratus-1', 'l-serratus-2'),
    'serratus.R' :     ('r-serratus-1', 'r-serratus-2'),

    'pect.L' :         ('spine-1', 'l-pect'),
    'pect.R' :         ('spine-1', 'r-pect'),

    'pectIk.L' :           ('l-pect-ik', ('l-pect-ik', ysmall)),
    'pectIk.R' :           ('r-pect-ik', ('r-pect-ik', ysmall)),

    'skull' :              ('head-2', ('head-2', ysmall)),

    'pubis' :              ('pelvis', 'pubis'),

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
    'spine-1' :            (0, 'spine', F_DEF|F_CON, L_DEF),
    'chest' :              (0, 'spine-1', F_DEF|F_CON, L_UPSPNFK),
    'chest-1' :            (0, 'chest', F_DEF|F_CON, L_DEF),
    'neck' :               (0, 'chest-1', F_DEF|F_CON, L_UPSPNFK),
    'neck-1' :             (0, 'neck', F_DEF|F_CON, L_DEF),
    'head' :               (0, 'neck-1', F_DEF|F_CON, L_UPSPNFK),

    'serratus.L' :     (0, 'chest', F_DEF, L_DEF),
    'serratus.R' :     (0, 'chest', F_DEF, L_DEF),
    'pect.L' :         (0, 'chest', F_DEF, L_UPSPNFK),
    'pect.R' :         (0, 'chest', F_DEF, L_UPSPNFK),

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
    'chest' :           'GZM_CircleChest',
    'neck' :            'GZM_Neck',
    'head' :            'GZM_Head',
}

Constraints = {
    "spine-1" : [("CopyRot", C_LOCAL, 1, ["spine", "spine", (1,1,1), (0,0,0), False])],

    "chest-1" : [("CopyRot", C_LOCAL, 1, ["chest", "chest", (1,1,1), (0,0,0), False])],

    "neck-1" : [("CopyRot", C_LOCAL, 1, ["neck", "neck", (1,1,1), (0,0,0), False])],

    "serratus.L" : [
        ("IK", 0, 0.5, ["serratusIk.L", "serratusIk.L", 1, None, (1,0,1)])
        ],

    "serratus.R" : [
        ("IK", 0, 0.5, ["serratusIk.R", "serratusIk.R", 1, None, (1,0,1)])
        ],

    "pect.L" : [
        ("IK", 0, 0.5, ["pectIk.L", "pectIk.L", 1, None, (1,0,1)])
        ],

    "pect.R" : [
        ("IK", 0, 0.5, ["pectIk.R", "pectIk.R", 1, None, (1,0,1)])
        ],


}

