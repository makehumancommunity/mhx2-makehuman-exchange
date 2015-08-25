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

#   ("l-gluteus-1",         "vl", ((0.1, 10955), (0.9, 10859))),

Renames = {
    "root" :        "hips",
    "spine05" :     "spine",
    "spine04" :     "spine-1",
    "spine03" :     "chest",
    "spine02" :     "chest-1",
    #"spine01" :     "",
    "neck01" :      "neck",
    "neck02" :      "neck-1",
    #"neck03" :      "",

    "head" :        "head",
    "jaw" :         "jaw",
    "eye.L" :       "eye.L",
    "breast.L" :    "breast.L",
    "eye.R" :       "eye.R",
    "breast.R" :    "breast.R",
    
    #"pelvis.L" :     "",
    "upperleg01.L" : "thigh.L",
    #"upperleg02.L" : "thigh.L",
    "lowerleg01.L" : "shin.L",
    #"lowerleg02.L" : "shin.L",
    "foot.L" :       "foot.L",
    "toe1-1.L" :     "toe.L",

    #"pelvis.R" :     "",
    "upperleg01.R" : "thigh.R",
    #"upperleg02.R" : "thigh.R",
    "lowerleg01.R" : "shin.R",
    #"lowerleg02.R" : "shin.R",
    "foot.R" :       "foot.R",
    "toe1-1.R" :     "toe.R",

    "clavicle.L" :      "clavicle.L",
    "shoulder01.L" :    "upper_arm.L",
    #"upperarm01.L" :    "upper_arm.L",
    "lowerarm01.L" :    "forearm.L",
    #"lowerarm02.L" :    "forearm.L",
    "wrist.L" :         "hand.L",

    "clavicle.R" :      "clavicle.R",
    "shoulder01.R" :    "upper_arm.R",
    #"upperarm01.R" :    "upper_arm.R",
    "lowerarm01.R" :    "forearm.R",
    #"lowerarm02.R" :    "forearm.R",
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

def getJoints(mhSkel, oldAmt):
    joints = []
    headsTails = {}
    amt = {}
    for mhBone in mhSkel["bones"]:
        bname = mhBone["name"]
        try: 
            nname = Renames[bname]
            known = True
        except KeyError:
            nname = bname
            known = False
        print(bname, nname)

        joints += [
            (nname+"_head", "a", mhBone["head"]),
            (nname+"_tail", "a", mhBone["tail"]),
            ]
            
        headsTails[nname] = (nname+"_head", nname+"_tail")
        
        roll = mhBone["roll"]
        if "parent" in mhBone.keys():
            parent = mhBone["parent"]
        else:
            parent = None
        if known:            
            roll,_parent,flags,layers = oldAmt[nname][0:4]
        else:
            flags = F_DEF
            layers = L_DEF
        amt[nname] = (roll,parent,flags,layers)            

    #print(joints)
    #print(headsTails.items())
    #print(amt.items())
    return joints, headsTails, amt
    

Planes = {
    "PlaneArm.L" :         ('l-upper-arm', 'l-elbow-tip', 'l-hand'),
    "PlaneHand.L" :        ('l-plane-hand-1', 'l-plane-hand-2', 'l-plane-hand-3'),
    "PlaneArm.R" :         ('r-shoulder', 'r-elbow-tip', 'r-hand'),
    "PlaneHand.R" :        ('r-plane-hand-1', 'r-plane-hand-2', 'r-plane-hand-3'),

    "PlaneEye.L" :         ('l-eye', 'l-eye-end', 'l-eye-top'),
    "PlaneEye.R" :         ('r-eye', 'r-eye-end', 'r-eye-top'),

    "PlaneLeg.L" :         ("thigh.L_head", "shin.L_head", "shin.L_tail"),
    "PlaneFoot.L" :        ("foot.L_head", "toe.L_head", "toe.L_tail"),
    "PlaneLeg.R" :         ("thigh.R_head", "shin.R_head", "shin.R_tail"),
    "PlaneFoot.R" :        ("foot.R_head", "toe.R_head", "toe.R_tail"),
    "PlaneThumb.L" :       ('l-plane-thumb-1', 'l-plane-thumb-2', 'l-plane-thumb-3'),
    "PlaneIndex.L" :       ('l-plane-index-1', 'l-plane-index-2', 'l-plane-index-3'),
    "PlaneMiddle.L" :      ('l-plane-middle-1', 'l-plane-middle-2', 'l-plane-middle-3'),
    "PlaneRing.L" :        ('l-plane-ring-1', 'l-plane-ring-2', 'l-plane-ring-3'),
    "PlanePinky.L" :       ('l-plane-pinky-1', 'l-plane-pinky-2', 'l-plane-pinky-3'),

    "PlaneThumb.R" :       ('r-plane-thumb-1', 'r-plane-thumb-2', 'r-plane-thumb-3'),
    "PlaneIndex.R" :       ('r-plane-index-1', 'r-plane-index-2', 'r-plane-index-3'),
    "PlaneMiddle.R" :      ('r-plane-middle-1', 'r-plane-middle-2', 'r-plane-middle-3'),
    "PlaneRing.R" :        ('r-plane-ring-1', 'r-plane-ring-2', 'r-plane-ring-3'),
    "PlanePinky.R" :       ('r-plane-pinky-1', 'r-plane-pinky-2', 'r-plane-pinky-3'),
}

    
def getPlanes(mhSkel):
    return Planes


def getArmature(mhSkel):
    from ..geometries import getScaleOffset
    scale,offset = getScaleOffset(mhSkel, cfg, True)
    pass


def getVertexGroups(mhHuman):
    pass