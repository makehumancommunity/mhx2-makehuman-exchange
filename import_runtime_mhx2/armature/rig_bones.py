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

    ('l-toe-2',             'p', ('l-foot-2', 'l-foot-1', 'l-foot-2')),
    ('r-toe-2',             'p', ('r-foot-2', 'r-foot-1', 'r-foot-2')),

    ('l-wrist-top',         'v', 10548),
    ('l-hand-end',          'v', 9944),
    ('r-wrist-top',         'v', 3883),
    ('r-hand-end',          'v', 3276),

    ('l-palm-02',           'vl', ((0.5, 9906), (0.5, 10500))),
    ('l-palm-03',           'vl', ((0.5, 9895), (0.5, 10497))),
    ('l-palm-04',           'vl', ((0.5, 9897), (0.5, 10495))),
    ('l-palm-05',           'vl', ((0.5, 9894), (0.5, 10494))),

    ('r-palm-02',           'vl', ((0.5, 3238), (0.5, 3834))),
    ('r-palm-03',           'vl', ((0.5, 3227), (0.5, 3831))),
    ('r-palm-04',           'vl', ((0.5, 3226), (0.5, 3829))),
    ('r-palm-05',           'vl', ((0.5, 3232), (0.5, 3828))),

    ('l-elbow-tip',         'v', 10058),
    ('l-knee-tip',          'v', 11223),
    ('r-elbow-tip',         'v', 3390),
    ('r-knee-tip',          'v', 4605),

    ('l-elbow',             'n', ('l-elbow-raw', 'l-shoulder', 'l-elbow-tip', 'l-hand')),
    ('l-knee',              'n', ('l-knee-raw', 'l-upper-leg', 'l-knee-tip', 'l-ankle')),
    ('r-elbow',             'n', ('r-elbow-raw', 'r-shoulder', 'r-elbow-tip', 'r-hand')),
    ('r-knee',              'n', ('r-knee-raw', 'r-upper-leg', 'r-knee-tip', 'r-ankle')),

    ('l-plane-hand-1',      'v', 10164),
    ('l-plane-hand-2',      'v', 10576),
    ('l-plane-hand-3',      'v', 9779),

    ('r-plane-hand-1',      'v', 3496),
    ('r-plane-hand-2',      'v', 3911),
    ('r-plane-hand-3',      'v', 3111),

    ('l-plane-thumb-1',     'v', 10291),
    ('l-plane-thumb-2',     'v', 9401),
    ('l-plane-thumb-3',     'v', 9365),

    ('l-plane-index-1',     'v', 9773),
    ('l-plane-index-2',     'v', 8638),
    ('l-plane-index-3',     'v', 8694),

    ('l-plane-middle-1',     'v', 9779),
    ('l-plane-middle-2',     'v', 8798),
    ('l-plane-middle-3',     'v', 8886),

    ('l-plane-ring-1',     'v', 9785),
    ('l-plane-ring-2',     'v', 9022),
    ('l-plane-ring-3',     'v', 9078),

    ('l-plane-pinky-1',     'v', 9793),
    ('l-plane-pinky-2',     'v', 9219),
    ('l-plane-pinky-3',     'v', 9270),

    ('r-plane-thumb-1',     'v', 3623),
    ('r-plane-thumb-2',     'v', 2725),
    ('r-plane-thumb-3',     'v', 2697),

    ('r-plane-index-1',     'v', 3105),
    ('r-plane-index-2',     'v', 1970),
    ('r-plane-index-3',     'v', 2026),

    ('r-plane-middle-1',     'v', 3111),
    ('r-plane-middle-2',     'v', 2130),
    ('r-plane-middle-3',     'v', 2218),

    ('r-plane-ring-1',     'v', 3117),
    ('r-plane-ring-2',     'v', 2354),
    ('r-plane-ring-3',     'v', 2410),

    ('r-plane-pinky-1',     'v', 3125),
    ('r-plane-pinky-2',     'v', 2551),
    ('r-plane-pinky-3',     'v', 2602),

    #('l-plane-foot',        'o', ('l-ankle', (0,-1,0))),
    #('r-plane-foot',        'o', ('r-ankle', (0,-1,0))),
    #('l-plane-toe',         'o', ('l-foot-1', (0,-1,0))),
    #('r-plane-toe',         'o', ('r-foot-1', (0,-1,0))),

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

    'deltoid.L' :          ('l-scapula', 'l-shoulder'),
    'deltoid.R' :          ('r-scapula', 'r-shoulder'),

    'clavicle.L' :         ('l-clavicle', 'l-scapula'),
    'upper_arm.L' :        ('l-shoulder', 'l-elbow'),
    'forearm.L' :          ('l-elbow', 'l-hand'),
    'hand.L' :             ('l-hand', 'l-hand-end'),

    'clavicle.R' :         ('r-clavicle', 'r-scapula'),
    'upper_arm.R' :        ('r-shoulder', 'r-elbow'),
    'forearm.R' :          ('r-elbow', 'r-hand'),
    'hand.R' :             ('r-hand', 'r-hand-end'),

    'thumb.01.L' :         ('l-finger-1-1', 'l-finger-1-2'),
    'thumb.02.L' :         ('l-finger-1-2', 'l-finger-1-3'),
    'thumb.03.L' :         ('l-finger-1-3', 'l-finger-1-4'),

    'thumb.01.R' :         ('r-finger-1-1', 'r-finger-1-2'),
    'thumb.02.R' :         ('r-finger-1-2', 'r-finger-1-3'),
    'thumb.03.R' :         ('r-finger-1-3', 'r-finger-1-4'),

    'palm_index.L' :       ('l-palm-02', 'l-finger-2-1'),
    'f_index.01.L' :       ('l-finger-2-1', 'l-finger-2-2'),
    'f_index.02.L' :       ('l-finger-2-2', 'l-finger-2-3'),
    'f_index.03.L' :       ('l-finger-2-3', 'l-finger-2-4'),

    'palm_index.R' :       ('r-palm-02', 'r-finger-2-1'),
    'f_index.01.R' :       ('r-finger-2-1', 'r-finger-2-2'),
    'f_index.02.R' :       ('r-finger-2-2', 'r-finger-2-3'),
    'f_index.03.R' :       ('r-finger-2-3', 'r-finger-2-4'),

    'palm_middle.L' :      ('l-palm-03', 'l-finger-3-1'),
    'f_middle.01.L' :      ('l-finger-3-1', 'l-finger-3-2'),
    'f_middle.02.L' :      ('l-finger-3-2', 'l-finger-3-3'),
    'f_middle.03.L' :      ('l-finger-3-3', 'l-finger-3-4'),

    'palm_middle.R' :      ('r-palm-03', 'r-finger-3-1'),
    'f_middle.01.R' :      ('r-finger-3-1', 'r-finger-3-2'),
    'f_middle.02.R' :      ('r-finger-3-2', 'r-finger-3-3'),
    'f_middle.03.R' :      ('r-finger-3-3', 'r-finger-3-4'),

    'palm_ring.L' :        ('l-palm-04', 'l-finger-4-1'),
    'f_ring.01.L' :        ('l-finger-4-1', 'l-finger-4-2'),
    'f_ring.02.L' :        ('l-finger-4-2', 'l-finger-4-3'),
    'f_ring.03.L' :        ('l-finger-4-3', 'l-finger-4-4'),

    'palm_ring.R' :        ('r-palm-04', 'r-finger-4-1'),
    'f_ring.01.R' :        ('r-finger-4-1', 'r-finger-4-2'),
    'f_ring.02.R' :        ('r-finger-4-2', 'r-finger-4-3'),
    'f_ring.03.R' :        ('r-finger-4-3', 'r-finger-4-4'),

    'palm_pinky.L' :       ('l-palm-05', 'l-finger-5-1'),
    'f_pinky.01.L' :       ('l-finger-5-1', 'l-finger-5-2'),
    'f_pinky.02.L' :       ('l-finger-5-2', 'l-finger-5-3'),
    'f_pinky.03.L' :       ('l-finger-5-3', 'l-finger-5-4'),

    'palm_pinky.R' :       ('r-palm-05', 'r-finger-5-1'),
    'f_pinky.01.R' :       ('r-finger-5-1', 'r-finger-5-2'),
    'f_pinky.02.R' :       ('r-finger-5-2', 'r-finger-5-3'),
    'f_pinky.03.R' :       ('r-finger-5-3', 'r-finger-5-4'),

    'thigh.L' :            ('l-upper-leg', 'l-knee'),
    'shin.L' :             ('l-knee', 'l-ankle'),
    'foot.L' :             ('l-ankle', 'l-foot-1'),
    'toe.L' :              ('l-foot-1', 'l-toe-2'),

    'thigh.R' :            ('r-upper-leg', 'r-knee'),
    'shin.R' :             ('r-knee', 'r-ankle'),
    'foot.R' :             ('r-ankle', 'r-foot-1'),
    'toe.R' :              ('r-foot-1', 'r-toe-2'),

    'skull' :              ('head-2', ('head-2', (0,0.2,0))),
    'toe_end.L' :          ('l-toe-2', ('l-toe-2', (0,0,0.2))),
    'toe_end.R' :          ('r-toe-2', ('r-toe-2', (0,0,0.2))),

    'penis_1' :            ('penis-1', 'penis-2'),
    'penis_2' :            ('penis-2', 'penis-3'),
    'penis_3' :            ('penis-3', 'penis-4'),

    'scrotum.L' :          ('l-scrotum-1', 'l-scrotum-2'),
    'scrotum.R' :          ('r-scrotum-1', 'r-scrotum-2'),
}

Planes = {
    "PlaneArm.L" :         ('l-shoulder', 'l-elbow-tip', 'l-hand'),
    "PlaneHand.L" :        ('l-plane-hand-1', 'l-plane-hand-2', 'l-plane-hand-3'),
    "PlaneLeg.L" :         ('l-upper-leg', 'l-knee-tip', 'l-ankle'),
    "PlaneFoot.L" :        ('l-ankle', 'l-toe-2', 'l-foot-1'),

    "PlaneThumb.L" :       ('l-plane-thumb-1', 'l-plane-thumb-2', 'l-plane-thumb-3'),
    "PlaneIndex.L" :       ('l-plane-index-1', 'l-plane-index-2', 'l-plane-index-3'),
    "PlaneMiddle.L" :      ('l-plane-middle-1', 'l-plane-middle-2', 'l-plane-middle-3'),
    "PlaneRing.L" :        ('l-plane-ring-1', 'l-plane-ring-2', 'l-plane-ring-3'),
    "PlanePinky.L" :       ('l-plane-pinky-1', 'l-plane-pinky-2', 'l-plane-pinky-3'),

    "PlaneArm.R" :         ('r-shoulder', 'r-elbow-tip', 'r-hand'),
    "PlaneHand.R" :        ('r-plane-hand-1', 'r-plane-hand-2', 'r-plane-hand-3'),
    "PlaneLeg.R" :         ('r-upper-leg', 'r-knee-tip', 'r-ankle'),
    "PlaneFoot.R" :        ('r-ankle', 'r-toe-2', 'r-foot-1'),

    "PlaneThumb.R" :       ('r-plane-thumb-1', 'r-plane-thumb-2', 'r-plane-thumb-3'),
    "PlaneIndex.R" :       ('r-plane-index-1', 'r-plane-index-2', 'r-plane-index-3'),
    "PlaneMiddle.R" :      ('r-plane-middle-1', 'r-plane-middle-2', 'r-plane-middle-3'),
    "PlaneRing.R" :        ('r-plane-ring-1', 'r-plane-ring-2', 'r-plane-ring-3'),
    "PlanePinky.R" :       ('r-plane-pinky-1', 'r-plane-pinky-2', 'r-plane-pinky-3'),
}

Armature = {
    'hips' :               (0, None, F_DEF, L_UPSPNFK),
    'spine' :              (0, 'hips', F_DEF|F_CON, L_UPSPNFK),
    'spine-1' :            (0, 'spine', F_DEF|F_CON, L_UPSPNFK),
    'chest' :              (0, 'spine-1', F_DEF|F_CON, L_UPSPNFK),
    'chest-1' :            (0, 'chest', F_DEF|F_CON, L_UPSPNFK),
    'neck' :               (0, 'chest-1', F_DEF|F_CON, L_UPSPNFK),
    'head' :               (0, 'neck', F_DEF|F_CON, L_UPSPNFK),

    'clavicle.L' :         ("PlaneYNeg", 'chest-1', F_DEF, L_UPSPNFK|L_LARMFK|L_LARMIK),
    'deltoid.L' :          ("PlaneYNeg", 'clavicle.L', F_DEF, L_LARMFK|L_LARMIK),
    'upper_arm.L' :        ("PlaneArm.L", 'deltoid.L', F_DEF, L_LARMFK),
    'forearm.L' :          ("PlaneArm.L", 'upper_arm.L', F_DEF|F_CON, L_LARMFK, P_YZX),
    'hand.L' :             ("PlaneHand.L", 'forearm.L', F_DEF|F_CON, L_LARMFK, P_YZX),

    'clavicle.R' :         ("PlaneYPos", 'chest-1', F_DEF, L_UPSPNFK|L_RARMFK|L_RARMIK),
    'deltoid.R' :          ("PlaneYPos", 'clavicle.R', F_DEF, L_RARMFK|L_RARMIK),
    'upper_arm.R' :        ("PlaneArm.R", 'deltoid.R', F_DEF, L_RARMFK),
    'forearm.R' :          ("PlaneArm.R", 'upper_arm.R', F_DEF|F_CON, L_RARMFK, P_YZX),
    'hand.R' :             ("PlaneHand.R", 'forearm.R', F_DEF|F_CON, L_RARMFK, P_YZX),

    'thumb.01.L' :         ("PlaneThumb.L", 'hand.L', F_DEF, L_LPALM, P_YZX),
    'thumb.02.L' :         ("PlaneThumb.L", 'thumb.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'thumb.03.L' :         ("PlaneThumb.L", 'thumb.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'thumb.01.R' :         ("PlaneThumb.R", 'hand.R', F_DEF, L_RPALM, P_YZX),
    'thumb.02.R' :         ("PlaneThumb.R", 'thumb.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'thumb.03.R' :         ("PlaneThumb.R", 'thumb.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_index.L' :       ("PlaneIndex.L", 'hand.L', F_DEF, L_LPALM),
    'f_index.01.L' :       ("PlaneIndex.L", 'palm_index.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_index.02.L' :       ("PlaneIndex.L", 'f_index.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_index.03.L' :       ("PlaneIndex.L", 'f_index.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_index.R' :       ("PlaneIndex.R", 'hand.R', F_DEF, L_RPALM),
    'f_index.01.R' :       ("PlaneIndex.R", 'palm_index.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_index.02.R' :       ("PlaneIndex.R", 'f_index.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_index.03.R' :       ("PlaneIndex.R", 'f_index.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_middle.L' :      ("PlaneMiddle.L", 'hand.L', F_DEF, L_LPALM),
    'f_middle.01.L' :      ("PlaneMiddle.L", 'palm_middle.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_middle.02.L' :      ("PlaneMiddle.L", 'f_middle.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_middle.03.L' :      ("PlaneMiddle.L", 'f_middle.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_middle.R' :      ("PlaneMiddle.R", 'hand.R', F_DEF, L_RPALM),
    'f_middle.01.R' :      ("PlaneMiddle.R", 'palm_middle.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_middle.02.R' :      ("PlaneMiddle.R", 'f_middle.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_middle.03.R' :      ("PlaneMiddle.R", 'f_middle.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_ring.L' :        ("PlaneRing.L", 'hand.L', F_DEF, L_LPALM),
    'f_ring.01.L' :        ("PlaneRing.L", 'palm_ring.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_ring.02.L' :        ("PlaneRing.L", 'f_ring.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_ring.03.L' :        ("PlaneRing.L", 'f_ring.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_ring.R' :        ("PlaneRing.R", 'hand.R', F_DEF, L_RPALM),
    'f_ring.01.R' :        ("PlaneRing.R", 'palm_ring.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_ring.02.R' :        ("PlaneRing.R", 'f_ring.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_ring.03.R' :        ("PlaneRing.R", 'f_ring.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_pinky.L' :       ("PlanePinky.L", 'hand.L', F_DEF, L_LPALM),
    'f_pinky.01.L' :       ("PlanePinky.L", 'palm_pinky.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_pinky.02.L' :       ("PlanePinky.L", 'f_pinky.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_pinky.03.L' :       ("PlanePinky.L", 'f_pinky.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_pinky.R' :       ("PlanePinky.R", 'hand.R', F_DEF, L_RPALM),
    'f_pinky.01.R' :       ("PlanePinky.R", 'palm_pinky.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_pinky.02.R' :       ("PlanePinky.R", 'f_pinky.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_pinky.03.R' :       ("PlanePinky.R", 'f_pinky.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'thigh.L' :            ("PlaneLeg.L", 'hips', F_DEF, L_LLEGFK),
    'shin.L' :             ("PlaneLeg.L", 'thigh.L', F_DEF|F_CON, L_LLEGFK, P_YZX),
    'foot.L' :             ("PlaneFoot.L", 'shin.L', F_DEF|F_CON, L_LLEGFK, P_YZX),
    'toe.L' :              ("PlaneFoot.L", 'foot.L', F_DEF|F_CON, L_LLEGFK, P_YZX),

    'thigh.R' :            ("PlaneLeg.R", 'hips', F_DEF, L_RLEGFK),
    'shin.R' :             ("PlaneLeg.R", 'thigh.R', F_DEF|F_CON, L_RLEGFK, P_YZX),
    'foot.R' :             ("PlaneFoot.R", 'shin.R', F_DEF|F_CON, L_RLEGFK, P_YZX),
    'toe.R' :              ("PlaneFoot.R", 'foot.R', F_DEF|F_CON, L_RLEGFK, P_YZX),
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

    'thigh.L' :         (-160,90, -45,45, -140,80),
    'thigh.R' :         (-160,90, -45,45, -80,140),
    'shin.L' :          (0,170, -40,40, 0,0),
    'shin.R' :          (0,170, -40,40, 0,0),
    'foot.L' :          (-90,45, -30,30, -30,30),
    'foot.R' :          (-90,45, -30,30, -30,30),
    'toe.L' :           (-20,60, 0,0, 0,0),
    'toe.R' :           (-20,60, 0,0, 0,0),

    'clavicle.L' :      (-16,50, -70,70,  -45,45),
    'clavicle.L' :      (-16,50,  -70,70,  -45,45),
    'upper_arm.L' :     (-45,135, -60,60, -135,135),
    'upper_arm.R' :     (-45,135, -60,60, -135,135),
    'forearm.L' :       (-45,130, 0,0, 0,0),
    'forearm.R' :       (-45,130, 0,0, 0,0),
    'hand.L' :          (-90,70, -90,90, -20,20),
    'hand.R' :          (-90,70, -90,90, -20,20),

    'thumb.03.L' :      (None,None, 0,0, 0,0),
    'f_index.02.L' :    (None,None, 0,0, 0,0),
    'f_index.03.L' :    (None,None, 0,0, 0,0),
    'f_middle.02.L' :   (None,None, 0,0, 0,0),
    'f_middle.03.L' :   (None,None, 0,0, 0,0),
    'f_ring.02.L' :     (None,None, 0,0, 0,0),
    'f_ring.03.L' :     (None,None, 0,0, 0,0),
    'f_pinky.02.L' :    (None,None, 0,0, 0,0),
    'f_pinky.03.L' :    (None,None, 0,0, 0,0),

    'thumb.03.R' :      (None,None, 0,0, 0,0),
    'f_index.02.R' :    (None,None, 0,0, 0,0),
    'f_index.03.R' :    (None,None, 0,0, 0,0),
    'f_middle.02.R' :   (None,None, 0,0, 0,0),
    'f_middle.03.R' :   (None,None, 0,0, 0,0),
    'f_ring.02.R' :     (None,None, 0,0, 0,0),
    'f_ring.03.R' :     (None,None, 0,0, 0,0),
    'f_pinky.02.R' :    (None,None, 0,0, 0,0),
    'f_pinky.03.R' :    (None,None, 0,0, 0,0),
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

    'thigh.L' :         'GZM_Circle025',
    'thigh.R' :         'GZM_Circle025',
    'shin.L' :          'GZM_Circle025',
    'shin.R' :          'GZM_Circle025',
    'foot.L' :          'GZM_Foot',
    'foot.R' :          'GZM_Foot',
    'toe.L' :           'GZM_Toe',
    'toe.R' :           'GZM_Toe',

    'clavicle.L' :      'GZM_Shoulder',
    'clavicle.R' :      'GZM_Shoulder',
    'deltoid.L' :       'GZM_Shoulder',
    'deltoid.R' :       'GZM_Shoulder',
    'upper_arm.L' :     'GZM_Circle025',
    'upper_arm.R' :     'GZM_Circle025',
    'forearm.L' :       'GZM_Circle025',
    'forearm.R' :       'GZM_Circle025',
    'hand.L' :          'GZM_Hand',
    'hand.R' :          'GZM_Hand',
}

Constraints = {}

