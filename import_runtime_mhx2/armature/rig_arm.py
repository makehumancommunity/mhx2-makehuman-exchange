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
    ('sternum',             'v', 1528),
    ('l-clav-1',            'l', ((0.75, 'l-clavicle'), (0.25, 'l-scapula'))),
    ('l-clav-2',            'l', ((0.5, 'l-clavicle'), (0.5, 'l-scapula'))),
    ('l-clav-3',            'l', ((0.25, 'l-clavicle'), (0.75, 'l-scapula'))),
    ('l-scap-ik-pole',      'o', ('sternum', (0,2.0,0))),

    ('l-shoulder-bend',     'vl', ((0.6, 10421), (0.4, 8238))),
    ('l-shoulder-1',        'l', ((0.8, 'l-shoulder'), (0.2, 'l-elbow'))),
    ('l-shoulder-2',        'l', ((0.6, 'l-shoulder'), (0.4, 'l-elbow'))),

    ('l-scapula-1',         'v', 8256),
    ('l-scapula-2',         'v', 8238),

    ('l-elbow-tip',         'v', 10058),
    ('l-knee-tip',          'v', 11223),
    ('r-elbow-tip',         'v', 3390),
    ('r-knee-tip',          'v', 4605),

    ('l-elbow',             'n', ('l-elbow-raw', 'l-shoulder', 'l-elbow-tip', 'l-hand')),
    ('l-knee',              'n', ('l-knee-raw', 'l-upper-leg', 'l-knee-tip', 'l-ankle')),
    ('r-elbow',             'n', ('r-elbow-raw', 'r-shoulder', 'r-elbow-tip', 'r-hand')),
    ('r-knee',              'n', ('r-knee-raw', 'r-upper-leg', 'r-knee-tip', 'r-ankle')),

    ('l-wrist-top',         'v', 10548),
    ('l-hand-end',          'v', 9944),
    ('r-wrist-top',         'v', 3883),
    ('r-hand-end',          'v', 3276),


]


HeadsTails = {
    'sternum' :             ('neck', 'sternum'),
    'clavicle.L' :          ('l-clavicle', 'l-clav-1'),
    'clav_segA.L' :         ('l-clavicle', 'l-clav-1'),
    'clav_segB.L' :         ('l-clav-1', 'l-clav-2'),
    'clav_segC.L' :         ('l-clav-2', 'l-clav-3'),
    'clav_segD.L' :         ('l-clav-3', 'l-scapula'),

    'mch_scapLength.L' :    ('l-clavicle', 'l-scapula'),
    'mch_scapIk.L' :        ('l-clavicle', 'l-scapula'),
    'mch_scapFollowFk.L' :  ('l-clavicle', 'l-scapula'),
    'mch_scapIkPole.L' :    ('l-scap-ik-pole', ('l-scap-ik-pole', (0,0,-0.2))),
    'mch_scapIkTrg.L' :     ('l-scapula', ('l-scapula', (0.2,0,0))),
    'loc_scapPos.L' :       ('l-scapula', ('l-scapula', (0,0.2,0))),
    'loc_scapAim.L' :       ('l-scapula', ('l-scapula', (-0.2,0,0))),
    'loc_scapUp.L' :        (('l-scapula', (0,2.0,0)), ('l-scapula', (0,2.2,0))),
    'scapula.L' :           ('l-scapula-1', 'l-scapula-2'),

    'loc_shoulder.L' :      ('l-shoulder', ('l-shoulder', (0,0.2,0))),
    'mch_bShoulderBend.L' : (('l-shoulder-bend', (-0.4,0,0)), 'l-shoulder-bend'),
    'bShoulder.L' :         ('l-shoulder-bend', 'l-shoulder-1'),
    'mch_shoulderIk.L' :    ('l-shoulder-1', 'l-shoulder-2'),

    'upper_arm.L' :         ('l-shoulder', 'l-elbow'),
    'forearm.L' :           ('l-elbow', 'l-hand'),
    'hand.L' :              ('l-hand', 'l-hand-end'),

    'upper_arm.R' :         ('r-shoulder', 'r-elbow'),
    'forearm.R' :           ('r-elbow', 'r-hand'),
    'hand.R' :              ('r-hand', 'r-hand-end'),


}

Planes = {
    "PlaneArm.L" :         ('l-shoulder', 'l-elbow-tip', 'l-hand'),
    "PlaneHand.L" :        ('l-plane-hand-1', 'l-plane-hand-2', 'l-plane-hand-3'),
    "PlaneArm.R" :         ('r-shoulder', 'r-elbow-tip', 'r-hand'),
    "PlaneHand.R" :        ('r-plane-hand-1', 'r-plane-hand-2', 'r-plane-hand-3'),
}

Armature = {
    'sternum' :             (0, 'chest-1', F_DEF|F_CON, L_UPSPNFK),
    'clavicle.L' :          (0, 'sternum', 0, L_LARMFK|L_LARMIK),
    'clav_segA.L' :         (0, 'clavicle.L', F_DEF, L_DEF),
    'clav_segB.L' :         (0, 'clav_segA.L', F_DEF|F_CON, L_DEF),
    'clav_segC.L' :         (0, 'clav_segB.L', F_DEF|F_CON, L_DEF),
    'clav_segD.L' :         (0, 'clav_segC.L', F_DEF|F_CON, L_DEF),

    'mch_scapFollowFk.L' :  (0, 'sternum', 0, L_HELP),
    'mch_scapLength.L' :    (0, 'sternum', 0, L_HELP),
    'mch_scapIk.L' :        (0, 'clavicle.L', 0, L_HELP),
    'mch_scapIkPole.L' :    (0, 'clav_segA.L', 0, L_HELP),
    'mch_scapIkTrg.L' :     (0, 'clav_segD.L', 0, L_HELP),
    'loc_scapPos.L' :       (0, 'clavicle.L', 0, L_HELP),
    'loc_scapAim.L' :       (0, 'loc_scapPos.L', 0, L_HELP),
    'loc_scapUp.L' :        (0, 'loc_scapPos.L', 0, L_HELP),
    'scapula.L' :           (0, 'loc_scapAim.L', F_DEF, L_DEF),

    'loc_shoulder.L' :      (0, 'clav_segD.L', 0, L_HELP),
    'mch_bShoulderBend.L' : (0, 'loc_shoulder.L', 0, L_HELP),
    'bShoulder.L' :         (0, 'mch_bShoulderBend.L', F_DEF|F_CON, L_DEF),
    'upper_arm.L' :         ("PlaneArm.L", 'loc_shoulder.L', F_DEF, L_LARMFK),
    'mch_shoulderIk.L' :    (0, 'upper_arm.L', 0, L_HELP),
    'forearm.L' :           ("PlaneArm.L", 'upper_arm.L', F_DEF|F_CON, L_LARMFK, P_YZX),
    'hand.L' :              ("PlaneHand.L", 'forearm.L', F_DEF|F_CON, L_LARMFK, P_YZX),

    'upper_arm.R' :        ("PlaneArm.R", None, F_DEF, L_RARMFK),
    'forearm.R' :          ("PlaneArm.R", 'upper_arm.R', F_DEF|F_CON, L_RARMFK, P_YZX),
    'hand.R' :             ("PlaneHand.R", 'forearm.R', F_DEF|F_CON, L_RARMFK, P_YZX),

}


RotationLimits = {
}

CustomShapes = {
    'clavicle.L' :      'GZM_Shoulder',
    'clavicle.R' :      'GZM_Shoulder',
    'upper_arm.L' :     'GZM_Circle025',
    'upper_arm.R' :     'GZM_Circle025',
    'forearm.L' :       'GZM_Circle025',
    'forearm.R' :       'GZM_Circle025',
    'hand.L' :          'GZM_Hand',
    'hand.R' :          'GZM_Hand',
}
CustomShapes = {}

Constraints = {}

