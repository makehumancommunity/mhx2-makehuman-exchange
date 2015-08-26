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
from collections import OrderedDict

Joints = [
    ('ground',          'j', 'ground'),

    # Spine
    ('pelvis',          'j', 'pelvis'),
    ('neck',            'b', 'neck_head'),
    ('head',            'b', 'head_head'),
    ('head-2',          'b', 'head_tail'),

    # Head

    ('r-eye',           'b', 'eye.L_head'),
    ('l-eye',           'b', 'eye.R_head'),
    ('r-eye-target',        'j', 'r-eye-target'),
    ('l-eye-target',        'j', 'l-eye-target'),

    # Legs
    ('l-upper-leg',         'b', 'thigh.L_head'),
    ('l-knee-raw',          'b', 'shin.L_head'),
    ('l-ankle',             'b', 'foot.L_head'),
    ('l-foot-1',            'b', 'foot.L_tail'),
    ('l-foot-2',            'b', 'toe.L_tail'),

    ('r-upper-leg',         'b', 'thigh.R_head'),
    ('r-knee-raw',          'b', 'shin.R_head'),
    ('r-ankle',             'b', 'foot.R_head'),
    ('r-foot-1',            'b', 'foot.R_tail'),
    ('r-foot-2',            'b', 'toe.R_tail'),

    # Arms
    ('l-clavicle',          'b', 'clavicle.L_head'),
    ('l-shoulder',          'b', 'shoulder01.L_head'),
    ('l-upper-arm',         'b', 'upper_arm.L_head'),
    ('l-elbow',             'b', 'forearm.L_head'),
    ('l-elbow-tip',         'j', 'l-elbow'),
    ('l-hand',              'b', 'hand.L_head'),

    ('r-clavicle',          'b', 'clavicle.R_head'),
    ('r-shoulder',          'b', 'shoulder01.R_head'),
    ('r-upper-arm',         'b', 'upper_arm.R_head'),
    ('r-elbow',             'b', 'forearm.R_head'),
    ('r-elbow-tip',         'j', 'r-elbow'),
    ('r-hand',              'b', 'hand.R_head'),

    # Fingers
    ('l-finger-1-1',        'b', 'thumb.01.L_head'),
    ('l-finger-1-2',        'b', 'thumb.02.L_head'),
    ('l-finger-1-3',        'b', 'thumb.03.L_head'),
    ('l-finger-1-4',        'b', 'thumb.03.L_tail'),
    ('l-finger-2-1',        'b', 'f_index.01.L_head'),
    ('l-finger-2-2',        'b', 'f_index.02.L_head'),
    ('l-finger-2-3',        'b', 'f_index.03.L_head'),
    ('l-finger-2-4',        'b', 'f_index.03.L_tail'),
    ('l-finger-3-1',        'b', 'f_middle.01.L_head'),
    ('l-finger-3-2',        'b', 'f_middle.02.L_head'),
    ('l-finger-3-3',        'b', 'f_middle.03.L_head'),
    ('l-finger-3-4',        'b', 'f_middle.03.L_tail'),
    ('l-finger-4-1',        'b', 'f_ring.01.L_head'),
    ('l-finger-4-2',        'b', 'f_ring.02.L_head'),
    ('l-finger-4-3',        'b', 'f_ring.03.L_head'),
    ('l-finger-4-4',        'b', 'f_ring.03.L_tail'),
    ('l-finger-5-1',        'b', 'f_pinky.01.L_head'),
    ('l-finger-5-2',        'b', 'f_pinky.02.L_head'),
    ('l-finger-5-3',        'b', 'f_pinky.03.L_head'),
    ('l-finger-5-4',        'b', 'f_pinky.03.L_tail'),

    ('r-finger-1-1',        'b', 'thumb.01.R_head'),
    ('r-finger-1-2',        'b', 'thumb.02.R_head'),
    ('r-finger-1-3',        'b', 'thumb.03.R_head'),
    ('r-finger-1-4',        'b', 'thumb.03.R_tail'),
    ('r-finger-2-1',        'b', 'f_index.01.R_head'),
    ('r-finger-2-2',        'b', 'f_index.02.R_head'),
    ('r-finger-2-3',        'b', 'f_index.03.R_head'),
    ('r-finger-2-4',        'b', 'f_index.03.R_tail'),
    ('r-finger-3-1',        'b', 'f_middle.01.R_head'),
    ('r-finger-3-2',        'b', 'f_middle.02.R_head'),
    ('r-finger-3-3',        'b', 'f_middle.03.R_head'),
    ('r-finger-3-4',        'b', 'f_middle.03.R_tail'),
    ('r-finger-4-1',        'b', 'f_ring.01.R_head'),
    ('r-finger-4-2',        'b', 'f_ring.02.R_head'),
    ('r-finger-4-3',        'b', 'f_ring.03.R_head'),
    ('r-finger-4-4',        'b', 'f_ring.03.R_tail'),
    ('r-finger-5-1',        'b', 'f_pinky.01.R_head'),
    ('r-finger-5-2',        'b', 'f_pinky.02.R_head'),
    ('r-finger-5-3',        'b', 'f_pinky.03.R_head'),
    ('r-finger-5-4',        'b', 'f_pinky.03.R_tail'),

]

Renames = {
    "root" :        None,
    "spine05" :     "hips",
    "spine04" :     "spine",
    "spine03" :     "spine-1",
    "spine02" :     "chest",
    "spine01" :     "chest-1",
    "neck01" :      "neck",
    "neck02" :      ("neck-1",1),
    "neck03" :      ("neck-1",2),

    "head" :        "head",
    "jaw" :         "jaw",
    "eye.L" :       "eye.L",
    "breast.L" :    "breast.L",
    "eye.R" :       "eye.R",
    "breast.R" :    "breast.R",

    "pelvis.L" :     "pelvis.L",
    "upperleg01.L" : ("thigh.L",1),
    "upperleg02.L" : ("thigh.L",2),
    "lowerleg01.L" : ("shin.L",1),
    "lowerleg02.L" : ("shin.L",2),
    "foot.L" :       "foot.L",
    "toe1-1.L" :     "toe.L",

    "pelvis.R" :     "pelvis.R",
    "upperleg01.R" : ("thigh.R",1),
    "upperleg02.R" : ("thigh.R",2),
    "lowerleg01.R" : ("shin.R",1),
    "lowerleg02.R" : ("shin.R",2),
    "foot.R" :       "foot.R",
    "toe1-1.R" :     "toe.R",

    "clavicle.L" :      "clavicle.L",
    "upperarm01.L" :    ("upper_arm.L",1),
    "upperarm02.L" :    ("upper_arm.L",2),
    "lowerarm01.L" :    ("forearm.L",1),
    "lowerarm02.L" :    ("forearm.L",2),
    "wrist.L" :         "hand.L",

    "clavicle.R" :      "clavicle.R",
    "upperarm01.R" :    ("upper_arm.R",1),
    "upperarm02.R" :    ("upper_arm.R",2),
    "lowerarm01.R" :    ("forearm.R",1),
    "lowerarm02.R" :    ("forearm.R",2),
    "wrist.R" :         "hand.R",

    #"tongue00" :     "",
    #"tongue01" :     "",
    #"tongue02" :     "",
    #"tongue03" :     "",
    #"tongue04" :     "",
    #"tongue05.L" :     "",
    #"tongue06.L" :     "",
    #"tongue07.L" :     "",

    "metacarpal1.L" :     "palm_index.L",
    "metacarpal2.L" :     "palm_middle.L",
    "metacarpal3.L" :     "palm_ring.L",
    "metacarpal4.L" :     "palm_pinky.L",

    "metacarpal1.R" :     "palm_index.R",
    "metacarpal2.R" :     "palm_middle.R",
    "metacarpal3.R" :     "palm_ring.R",
    "metacarpal4.R" :     "palm_pinky.R",

    "finger1-1.L" :     "thumb.01.L",
    "finger1-2.L" :     "thumb.02.L",
    "finger1-3.L" :     "thumb.03.L",
    "finger2-1.L" :     "f_index.01.L",
    "finger2-2.L" :     "f_index.02.L",
    "finger2-3.L" :     "f_index.03.L",
    "finger3-1.L" :     "f_middle.01.L",
    "finger3-2.L" :     "f_middle.02.L",
    "finger3-3.L" :     "f_middle.03.L",
    "finger4-1.L" :     "f_ring.01.L",
    "finger4-2.L" :     "f_ring.02.L",
    "finger4-3.L" :     "f_ring.03.L",
    "finger5-1.L" :     "f_pinky.01.L",
    "finger5-2.L" :     "f_pinky.02.L",
    "finger5-3.L" :     "f_pinky.03.L",

    "finger1-1.R" :     "thumb.01.R",
    "finger1-2.R" :     "thumb.02.R",
    "finger1-3.R" :     "thumb.03.R",
    "finger2-1.R" :     "f_index.01.R",
    "finger2-2.R" :     "f_index.02.R",
    "finger2-3.R" :     "f_index.03.R",
    "finger3-1.R" :     "f_middle.01.R",
    "finger3-2.R" :     "f_middle.02.R",
    "finger3-3.R" :     "f_middle.03.R",
    "finger4-1.R" :     "f_ring.01.R",
    "finger4-2.R" :     "f_ring.02.R",
    "finger4-3.R" :     "f_ring.03.R",
    "finger5-1.R" :     "f_pinky.01.R",
    "finger5-2.R" :     "f_pinky.02.R",
    "finger5-3.R" :     "f_pinky.03.R",
}

def getNewName(bname):
    try:
        nname = Renames[bname]
        known = True
    except KeyError:
        nname = bname
        known = False
    print(bname, nname)
    if isinstance(nname,tuple):
        nname,idx = nname
    else:
        idx = 0
    return nname,known,idx


HeadsTails = {
    "clavicle.L" :      ("l-clavicle", "upper_arm.L_head"),
    "clavicle.R" :      ("r-clavicle", "upper_arm.R_head"),
    "eye_parent.L" :    "eye.L",
    "eye_parent.R" :    "eye.R",
}

Parents = {
    "pelvis.L" :    "hips",
    "pelvis.R" :    "hips",
    "upperarm.L" :  "clavicle.L",
    "upperarm.R" :  "clavicle.R",
}    

Constraints = {
    "shoulder01.L" : [
        ("IK", 0, 1, ["clavicle.L", "clavicle.L", 1, None, (1,1,1), False])
        ],

    "shoulder01.R" : [
        ("IK", 0, 1, ["clavicle.R", "clavicle.R", 1, None, (1,1,1), False])
        ],
}

def getJoints(mhSkel, oldAmt):
    from .utils import addDict

    joints = []
    headsTails = {}
    deformAmt = {}
    amt = OrderedDict()
    for mhBone in mhSkel["bones"]:
        bname = mhBone["name"]
        nname,known,idx = getNewName(bname)
        if nname is None:
            continue
        if idx == 0:
            joints += [
                (nname+"_head", "a", mhBone["head"]),
                (nname+"_tail", "a", mhBone["tail"]),
                ]
        elif idx == 1:
            joints.append((nname+"_head", "a", mhBone["head"]))
        elif idx == 2:
            joints.append((nname+"_tail", "a", mhBone["tail"]))
            continue

        if nname not in headsTails.keys():
            headsTails[nname] = (nname+"_head", nname+"_tail")

        roll = mhBone["roll"]
        if nname in Parents.keys():
            parent = Parents[nname]
        elif "parent" in mhBone.keys():
            parent,_,_ = getNewName(mhBone["parent"])
        else:
            parent = None
        if known:
            roll,_parent,flags,layers = oldAmt[nname][0:4]
        else:
            flags = F_DEF
            layers = L_DEF|L_TWEAK
        amt[nname] = deformAmt[nname] = (roll,parent,flags,layers)

    #print(joints)
    #print(headsTails.items())
    #print(amt.items())

    joints += Joints
    addDict(HeadsTails, headsTails)

    return joints, headsTails, amt, deformAmt


def getArmature(mhSkel):
    from ..geometries import getScaleOffset
    scale,offset = getScaleOffset(mhSkel, cfg, True)
    pass


def getVertexGroups(mhHuman):
    from .utils import mergeWeights

    weights = mhHuman["seed_mesh"]["weights"]
    vgroups = OrderedDict()
    for bname, weight in weights.items():
        nname,known,idx = getNewName(bname)
        if nname is None:
            continue
        if nname in vgroups.keys():
            vgroups[nname] = mergeWeights(vgroups[nname] + weight)
        else:
            vgroups[nname] = weight
    return vgroups
