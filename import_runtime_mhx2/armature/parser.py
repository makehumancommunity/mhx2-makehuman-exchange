# ##### BEGIN GPL LICENSE BLOCK #####
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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) Thomas Larsson 2014


import os
import math
from mathutils import Vector

from collections import OrderedDict

from .flags import *
from .utils import *
from ..hm8 import *
from ..load_json import loadJsonRelative

from . import rig_joints
from . import rig_bones
from . import rig_muscle
from . import rig_face
from . import rig_control
from . import rig_merge
from . import rig_panel
from . import rig_rigify

#-------------------------------------------------------------------------------
#   Parser base class.
#-------------------------------------------------------------------------------

class Parser:

    def __init__(self, mhHuman, cfg):
        self.config = cfg

        self.defineJointLocations(mhHuman, cfg)

        self.bones = {}
        self.locations = {}
        self.terminals = {}
        self.origin = Vector([0,0,0])
        self.normals = {}
        self.headsTails = None
        self.parents = {}
        self.ikChains = {}
        self.loadedShapes = {}
        self.customShapes = {}
        self.gizmos = {}
        self.constraints = {}
        self.locationLimits = {}
        self.rotationLimits = {}
        self.drivers = []
        self.propDrivers = []
        self.lrPropDrivers = []
        self.boneDrivers = {}

        self.vertexGroupFiles = []
        self.vertexGroups = {}

        if cfg.useMhx:
            layers = L_MAIN|L_UPSPNFK|L_LARMFK|L_RARMFK|L_LLEGFK|L_RLEGFK|L_HEAD
            if cfg.useFingers:
                layers |= L_LHANDIK|L_RHANDIK
            else:
                layers |= L_LHANDFK|L_RHANDFK|L_LPALM|L_RPALM|L_TWEAK
            if cfg.useFacePanel:
                layers |= L_PANEL
        else:
            layers = L_MAIN
        self.visibleLayers = layers

        self.objectProps = [("MhxRig", cfg.rigType)]
        self.customProps = []
        self.bbones = {}
        self.poseInfo = {}
        self.master = None
        self.headName = 'head'
        self.root = "hips"

        if cfg.useMhx:
            self.boneGroups = [
                ('Spine', 'THEME01', L_UPSPNFK),
                ('ArmFK.L', 'THEME02', L_LARMFK),
                ('ArmFK.R', 'THEME03', L_RARMFK),
                ('ArmIK.L', 'THEME04', L_LARMIK),
                ('ArmIK.R', 'THEME05', L_RARMIK),
                ('LegFK.L', 'THEME06', L_LLEGFK),
                ('LegFK.R', 'THEME07', L_RLEGFK),
                ('LegIK.L', 'THEME14', L_LLEGIK),
                ('LegIK.R', 'THEME09', L_RLEGIK),
            ]
        else:
            self.boneGroups = []

        self.deformPrefix = ""
        if cfg.useDeformBones or cfg.useDeformNames:
            self.deformPrefix = "DEF-"

        if cfg.useMuscles:
            self.vertexGroupFiles += ["head", "muscles", "hand", "joints", "tights_muscles", "skirt_muscles", "genitalia_muscles"]
        else:
            self.vertexGroupFiles += ["head", "bones", "hand", "joints", "tights", "skirt", "genitalia"]

        if cfg.useMuscles:
            self.vertexGroupFiles += ["hair_muscles"]
        else:
            self.vertexGroupFiles += ["hair"]

        self.joints = (
            rig_joints.Joints +
            rig_bones.Joints +
            rig_face.Joints +
            rig_control.Joints
        )
        if cfg.useMuscles:
            self.joints += rig_muscle.Joints
        if cfg.useFacePanel:
            self.joints += rig_panel.Joints

        self.planes = mergeDicts([
            rig_bones.Planes,
            rig_face.Planes,
        ])
        self.planeJoints = rig_control.PlaneJoints

        self.headsTails = mergeDicts([
            rig_bones.HeadsTails,
            rig_face.HeadsTails,
            rig_control.HeadsTails,
            rig_control.RevFootHeadsTails,
        ])
        if cfg.useMuscles:
            addDict(rig_muscle.HeadsTails, self.headsTails)
        if cfg.useFacePanel:
            addDict(rig_panel.HeadsTails, self.headsTails)

        for bname in cfg.terminals.keys():
            parent,offset = cfg.terminals[bname]
            _head,tail = self.headsTails[parent]
            self.headsTails[bname] = (tail, (tail,offset))

        if cfg.useConstraints:
            self.setConstraints(rig_bones.Constraints)
            self.setConstraints(rig_face.Constraints)
            if cfg.useMuscles:
                self.setConstraints(rig_muscle.Constraints)

        if cfg.useLocks:
            addDict(rig_bones.RotationLimits, self.rotationLimits)
            addDict(rig_face.RotationLimits, self.rotationLimits)
            addDict(rig_face.LocationLimits, self.locationLimits)
            addDict(rig_control.RotationLimits, self.rotationLimits)
            if cfg.useMuscles:
                addDict(rig_muscle.RotationLimits, self.rotationLimits)
        if cfg.useFacePanel:
            addDict(rig_panel.RotationLimits, self.rotationLimits)
            addDict(rig_panel.LocationLimits, self.locationLimits)

        if cfg.useCustomShapes:
            addDict(rig_face.CustomShapes, self.customShapes)
            if cfg.useCustomShapes == 'ALL':
                addDict(rig_bones.CustomShapes, self.customShapes)
                addDict(rig_control.CustomShapes, self.customShapes)
                if cfg.useMuscles:
                    addDict(rig_muscle.CustomShapes, self.customShapes)
        if cfg.useFacePanel:
            addDict(rig_panel.CustomShapes, self.customShapes)

        if cfg.useFingers and cfg.useConstraints:
            self.setConstraints(rig_control.FingerConstraints)
            self.lrPropDrivers += rig_control.FingerPropLRDrivers

        if cfg.useMhx:
            # npieces,target,numAfter,followNext
            self.splitBones = {
                "forearm" :     (3, "hand", False, True),
                "shin" :        (3, "foot", False, False),
            }
        elif cfg.useRigify:
            self.joints += rig_rigify.Joints
            addDict(rig_rigify.HeadsTails, self.headsTails)

            self.splitBones = {
                "upper_arm" :   (2, "forearm", False, True),
                "forearm" :     (2, "hand", False, True),
                "thigh" :       (2, "shin", False, True),
                "shin" :        (2, "foot", False, True),

                "thumb.01" :    (2, "thumb.02", True, True),
                "f_index.01" :  (2, "f_index.02", True, True),
                "f_middle.01" : (2, "f_middle.02", True, True),
                "f_ring.01" :   (2, "f_ring.02", True, True),
                "f_pinky.01" :  (2, "f_pinky.02", True, True),
            }
        else:
            self.splitBones = {}


    def createBones(self):
        cfg = self.config

        self.addBones(rig_bones.Armature)
        if cfg.useTerminators:
            self.addBones(rig_bones.TerminatorArmature)
        self.addBones(rig_face.Armature)

        for bname in cfg.terminals.keys():
            pname,_offset = cfg.terminals[bname]
            parent = self.bones[pname]
            self.addBones({bname: (0, pname, 0, parent.layers)})

        if cfg.useMasterBone:
            self.master = 'master'
            self.addBones(rig_control.MasterArmature)

        if cfg.useReverseHip:
            hiphead, hiptail = self.headsTails["hips"]
            self.headsTails["root"] = (hiptail, (hiptail,(0,0,-2)))
            self.headsTails["hips"] = (hiptail, hiphead)
            self.customShapes["hips"] = "GZM_CircleHips"
            self.root = "root"
            root = self.bones["root"] = Bone(self, "root")
            root.type = "Null"
            root.fromInfo((0, None, F_WIR, L_MAIN))
            hips = self.bones["hips"]
            hips.parent = "root"
            hips.conn = False
            hips.lockLocation = (1,1,1)
            spine = self.bones["spine"]
            spine.parent = "root"
            spine.conn = False

        if cfg.useMuscles:
            self.addBones(rig_muscle.Armature)

        if cfg.useFacePanel:
            self.addBones(rig_panel.Armature)
            addDict(rig_panel.BoneDrivers, self.boneDrivers)

        if cfg.useRigify:
            self.addBones(rig_rigify.Armature)

        if cfg.useHeadControl:
            self.addBones(rig_control.HeadArmature)
            if cfg.useConstraints:
                self.setConstraints(rig_control.HeadConstraints)
                self.propDrivers += rig_control.HeadPropDrivers

        if cfg.useSockets and cfg.useConstraints:
            self.changeParents(rig_control.SocketParents)
            self.addBones(rig_control.SocketArmature)
            self.setConstraints(rig_control.SocketConstraints)
            self.lrPropDrivers += rig_control.SocketPropLRDrivers

        if cfg.useIkLegs and cfg.useConstraints:
            self.addBones(rig_control.RevFootArmature)
            self.setConstraints(rig_control.RevFootConstraints)
            self.addBones(rig_control.MarkerArmature)
            self.lrPropDrivers += rig_control.IkLegPropLRDrivers
            self.addIkChains(rig_bones.Armature, rig_control.IkLegChains)
            self.reparentMarkers(rig_control.LegMarkers)

        if cfg.useIkArms and cfg.useConstraints:
            self.addBones(rig_control.IkArmArmature)
            self.setConstraints(rig_control.IkArmConstraints)
            self.lrPropDrivers += rig_control.IkArmPropLRDrivers
            self.addIkChains(rig_bones.Armature, rig_control.IkArmChains)

        if cfg.useFingers and cfg.useConstraints:
            self.addBones(rig_control.FingerArmature)

        if cfg.useConstraints and cfg.useLocks:
            for bname,limits in self.rotationLimits.items():
                try:
                    bone = self.bones[bname]
                except KeyError:
                    continue
                minX,maxX, minY,maxY, minZ,maxZ = limits
                lockX,lockY,lockZ = bone.lockRotation
                if minX == maxX == 0:
                    lockX = 1
                if minY == maxY == 0:
                    lockY = 1
                if minZ == maxZ == 0:
                    lockZ = 1
                bone.lockRotation = lockX,lockY,lockZ
                if minX != None and cfg.useRotationLimits and bone.lockRotation != (1,1,1):
                    cns = ("LimitRot", C_LOCAL, 0.8, ["LimitRot", limits, (1,1,1)])
                    self.addConstraint(bname, cns)

            for bname,limits in self.locationLimits.items():
                try:
                    bone = self.bones[bname]
                except KeyError:
                    continue
                minX,maxX, minY,maxY, minZ,maxZ = limits
                cns = ("LimitLoc", C_LOCAL, 1, ["LimitLoc", limits, (1,1,1,1,1,1)])
                self.addConstraint(bname, cns)

        if cfg.useCorrectives:
            self.addCSysBones(rig_control.CoordinateSystems)

        if cfg.addConnectingBones:
            extras = []
            for bone in self.bones:
                if bone.parent:
                    head,_ = self.headsTails[bone.name]
                    _,ptail = self.headsTails[bone.parent]
                    if head != ptail:
                        connector = Bone(self, "_"+bone.name)
                        connector.layers = L_HELP
                        connector.parent = bone.parent
                        bone.parent = connector.name
                        extras.append(connector)
                        self.headsTails[connector.name] = (ptail, head)
            for bone in extras:
                self.bones[bone.name] = bone

        if cfg.useCustomShapes:
            addDict(loadJsonRelative("armature/data/mhx/gizmos-face.json"), self.gizmos)
            if cfg.useCustomShapes == 'ALL':
                addDict(loadJsonRelative("armature/data/mhx/gizmos.json"), self.gizmos)
        if cfg.useFacePanel:
            addDict(loadJsonRelative("armature/data/mhx/gizmos-panel.json"), self.gizmos)

        vgroups = self.readVertexGroupFiles(self.vertexGroupFiles)
        addDict(vgroups, self.vertexGroups)

        if cfg.merge:
            self.mergeBones(cfg.merge)
        else:
            if cfg.mergeSpine:
                self.mergeBones(rig_merge.SpineMergers)
            if cfg.mergeShoulders:
                self.mergeBones(rig_merge.ShoulderMergers)
            if cfg.mergeFingers:
                self.mergeBones(rig_merge.FingerMergers)
            if cfg.mergePalms:
                self.mergeBones(rig_merge.PalmMergers)
            if cfg.mergeHead:
                self.mergeBones(rig_merge.HeadMergers)

        if cfg.useDeformNames or cfg.useDeformBones:
            generic = mergeDicts([
                rig_bones.Armature,
                rig_face.Armature,
            ])
            if cfg.useDeformBones:
                self.addDeformBones(generic)
                self.renameDeformBones(rig_muscle.Armature, rig_muscle.CustomShapes)
                if cfg.useConstraints:
                    self.renameConstraints(rig_muscle.Constraints)
            custom = {}
            if cfg.useCustomShapes:
                if cfg.useCustomShapes == 'ALL':
                    if cfg.useMuscles:
                        addDict(rig_muscle.CustomShapes, custom)
            self.addDeformVertexGroups(vgroups, custom)
            #self.renameDeformVertexGroups(rig_muscle.Armature)

        if cfg.useSplitBones or cfg.useSplitNames:
            if cfg.useSplitBones:
                self.addSplitBones()
            self.addSplitVertexGroups(vgroups)


    def changeParents(self, newParents):
        for bname, parent in newParents.items():
            self.bones[bname].parent = parent


    def getRealBoneName(self, bname, raiseError=True):
        try:
            self.bones[bname]
            return bname
        except KeyError:
            pass

        altname = bname
        if bname[0:4] == "DEF-":
            altname = bname[4:]
        else:
            altname = "DEF-"+bname

        print("Missing bone %s. Trying %s" % (bname, altname))
        try:
            self.bones[altname]
            return altname
        except KeyError:
            pass

        if raiseError:
            print(str(self.bones.keys()))
            raise NameError("Missing %s and %s" % (bname, altname))
        else:
            return bname


    def setup(self):
        cfg = self.config

        self.setupJoints()
        self.setupNormals()
        self.setupPlaneJoints()
        self.createBones()

        for bone in self.bones.values():
            hname,tname = self.headsTails[bone.name]
            head = self.findLocation(hname)
            tail = self.findLocation(tname)
            bone.setBone(head, tail)

        for bone in self.bones.values():
            if isinstance(bone.roll, str):
                if bone.roll[0:5] != "Plane":
                    bone.roll = self.bones[bone.roll].roll
            elif isinstance(bone.roll, Bone):
                bone.roll = bone.roll.roll
            elif isinstance(bone.roll, tuple):
                bname,angle = bone.roll
                bone.roll = self.bones[bname].roll + angle

        # Rename vertex groups now.
        # Wait with bones until everything is built.

        for bname,nname in cfg.bones.items():
            vgroups = self.vertexGroups
            if bname in vgroups.keys():
                vgroups[nname] = vgroups[bname]
                del vgroups[bname]
            else:
                defname = self.deformPrefix + bname
                if defname in vgroups.keys():
                    vgroups[self.deformPrefix + nname] = vgroups[defname]
                    del vgroups[defname]


    def setupNormals(self):
        for plane,joints in self.planes.items():
            j1,j2,j3 = joints
            p1 = self.locations[j1]
            p2 = self.locations[j2]
            p3 = self.locations[j3]
            pvec = getUnitVector(p2-p1)
            yvec = getUnitVector(p3-p2)
            if pvec is None or yvec is None:
                self.normals[plane] = None
            else:
                self.normals[plane] = getUnitVector(yvec.cross(pvec))


    def defineJointLocations(self, mhHuman, cfg):
        self.scale = mhHuman["scale"]
        if cfg.useOffset:
            self.offset = Vector(mhHuman["offset"])
        else:
            self.offset = Vector((0,0,0))

        self.coord = dict(
            [(vn,self.scale*(Vector(co) + self.offset))
                for vn,co in enumerate(mhHuman["seed_mesh"]["vertices"])
            ])

        self.jointLocs = {}
        vn0 = FirstJointVert
        for name in JointNames:
            self.jointLocs[name] = self.calcBox(vn0)
            vn0 += 8
        self.jointLocs["ground"] = self.calcBox(NTotalVerts-8)


    def calcBox(self, vn0):
        vsum = Vector((0,0,0))
        for n in range(8):
            vsum += self.coord[vn0+n]
        return vsum/8


    def setupJoints (self):
        """
        Evaluate symbolic expressions for joint locations and store them in self.locations.
        Joint locations are specified symbolically in the *Joints list in the beginning of the
        rig_*.py files (e.g. ArmJoints in rig_arm.py).
        """

        cfg = self.config
        for (key, type, data) in self.joints:
            if type == 'j':
                loc = self.jointLocs[data]
                self.locations[key] = loc
                self.locations[data] = loc
            elif type == 'v':
                v = int(data)
                self.locations[key] = self.coord[v]
            elif type == 'x':
                self.locations[key] = Vector((float(data[0]), float(data[2]), -float(data[1])))
            elif type == 'vo':
                v = int(data[0])
                offset = Vector((float(data[1]), float(data[3]), -float(data[2])))
                self.locations[key] = (self.coord[v] + self.scale*offset)
            elif type == 'vl':
                ((k1, v1), (k2, v2)) = data
                loc1 = self.coord[int(v1)]
                loc2 = self.coord[int(v2)]
                self.locations[key] = (k1*loc1 + k2*loc2)
            elif type == 'f':
                (raw, head, tail, offs) = data
                rloc = self.locations[raw]
                hloc = self.locations[head]
                tloc = self.locations[tail]
                vec = tloc - hloc
                vraw = rloc - hloc
                x = vec.dot(vraw)/vec.dot(vec)
                self.locations[key] = hloc + x*vec + Vector(offs)
            elif type == 'b':
                self.locations[key] = self.locations[data]
            elif type == 'p':
                x = self.locations[data[0]]
                y = self.locations[data[1]]
                z = self.locations[data[2]]
                self.locations[key] = Vector((x[0],y[1],z[2]))
            elif type == 'vz':
                v = int(data[0])
                z = self.coord[v][2]
                loc = self.locations[data[1]]
                self.locations[key] = Vector((loc[0],loc[1],z))
            elif type == 'X':
                r = self.locations[data[0]]
                (x,y,z) = data[1]
                r1 = Vector([float(x), float(y), float(z)])
                self.locations[key] = r.cross(r1)
            elif type == 'l':
                ((k1, joint1), (k2, joint2)) = data
                self.locations[key] = k1*self.locations[joint1] + k2*self.locations[joint2]
            elif type == 'o':
                (joint, offsSym) = data
                if isinstance(offsSym, str):
                    offs = self.locations[offsSym]
                else:
                    offs = self.scale * Vector(offsSym)
                self.locations[key] = self.locations[joint] + offs
            else:
                raise NameError("Unknown %s" % type)
        return


    def setupPlaneJoints (self):
        cfg = self.config
        for key,data in self.planeJoints:
            p0,plane,dist = data
            x0 = self.locations[p0]
            p1,p2,p3 = self.planes[plane]
            vec = getUnitVector(self.locations[p3] - self.locations[p1])
            n = self.normals[plane]
            t = n.cross(vec)
            self.locations[key] = x0 + self.scale*dist*t


    def findLocation(self, joint):
        if isinstance(joint, str):
            return self.locations[joint]
        else:
            (first, second) = joint
            if isinstance(first, str):
                return self.locations[first] + Vector(second)
            else:
                w1,j1 = first
                w2,j2 = second
                return w1*self.locations[j1] + w2*self.locations[j2]


    def distance(self, joint1, joint2):
        vec = self.locations[joint2] - self.locations[joint1]
        return math.sqrt(vec.dot(vec))


    def prefixWeights(self, weights, prefix):
        pweights = {}
        for name in weights.keys():
            if name in self.heads:
                pweights[name] = weights[name]
            else:
                pweights[prefix+name] = weights[name]
        return pweights


    def sortBones(self, bone, hier):
        self.bones[bone.name] = bone
        subhier = []
        hier.append([bone, subhier])
        for child in bone.children:
            self.sortBones(child, subhier)


    def addBones(self, dict):
        for bname,info in dict.items():
            bone = self.bones[bname] = Bone(self, bname)
            bone.fromInfo(info)


    def getParent(self, bone):
        return bone.parent


    def reparentMarkers(self, markers):
        for suffix in [".L", ".R"]:
            for bname in markers:
                bone = self.bones[bname + ".marker" + suffix]
                words = bone.parent.rsplit(".", 1)
                bone.parent = words[0] + ".fk" + suffix


    def addIkChains(self, generic, ikChains):
        """
        Adds FK and IK versions of the bones in the chain, and add CopyTransform
        constraints to the original bone, which is moved to the L_HELP layer. E.g.
        shin.L => shin.fk.L, shin.ik.L, shin.L
        """

        cfg = self.config

        for bname in generic.keys():
            bone = self.bones[bname]
            headTail = self.headsTails[bname]
            base,ext = splitBoneName(bname)
            #bone.parent = self.getParent(bone)

            if base in ikChains.keys():
                pbase,pext = splitBoneName(bone.parent)
                value = ikChains[base]
                type = value[0]
                iklayer = L_HELP
                if type == "DownStream":
                    _,layer,cnsname = value
                    fkParent = getFkName(pbase,pext)
                elif type == "Upstream":
                    _,layer,cnsname = value
                    fkParent = ikParent = bone.parent
                elif type == "Leaf":
                    _, layer, iklayer, count, cnsname, target, pole, lang, rang = value
                    fkParent = getFkName(pbase,pext)
                    ikParent = getIkName(pbase,pext)
                else:
                    raise NameError("Unknown IKChain type %s" % type)

                if ext == ".R":
                    layer <<= 16

                fkName = getFkName(base,ext)
                self.headsTails[fkName] = headTail
                fkBone = self.bones[fkName] = Bone(self, fkName)
                fkBone.fromInfo((bname, fkParent, F_WIR, layer<<1, bone.poseFlags))

                customShape = self.customShapes[bone.name]
                self.customShapes[fkName] = customShape
                self.customShapes[bone.name] = None
                bone.layers = L_HELP

                if cfg.useLocks:
                    try:
                        limits = self.rotationLimits[bname]
                    except KeyError:
                        limits = None
                    if limits:
                        self.rotationLimits[fkName] = limits
                        del self.rotationLimits[bname]

                self.addConstraint(bname, copyTransform(fkName, cnsname+"FK"))

                if type == "DownStream":
                    continue

                ikName = getIkName(base,ext)
                self.headsTails[ikName] = headTail
                ikBone = self.bones[ikName] = Bone(self, ikName)
                ikBone.fromInfo((bname, ikParent, F_WIR, L_HELP, bone.poseFlags))

                self.customShapes[ikName] = customShape
                self.addConstraint(bname, copyTransform(ikName, cnsname+"IK", 0))

                if type == "Leaf":
                    words = bone.parent.rsplit(".", 1)
                    pbase = words[0]
                    if len(words) == 1:
                        pext = ""
                    else:
                        pext = "." + words[1]
                    fkBone.parent = pbase + ".fk" + pext
                    ikBone.parent = pbase + ".ik" + pext
                    ikBone.layers = iklayer
                    if iklayer == L_TWEAK:
                        ikBone.lockRotation = (0,0,1)
                        ikBone.layers = layer
                    bone.norot = True

                    ikTarget = target + ".ik" + ext
                    poleTarget = pole + ".ik" + ext
                    if ext == ".L":
                        poleAngle = lang
                    else:
                        poleAngle = rang

                    cns = ('IK', 0, 1, ['IK', ikTarget, count, (poleAngle, poleTarget), (True, False,False)])
                    self.addConstraint(ikName, cns)


    def addDeformBones(self, generic):
        """
        Add deform bones with CopyTransform constraints to the original bone.
        Deform bones start with self.deformPrefix, as in Rigify.
        Don't add deform bones for split forearms, becaues that is done elsewhere.
        """

        cfg = self.config

        for bname in generic.keys():
            try:
                bone = self.bones[bname]
            except KeyError:
                print("Warning: deform bone %s does not exist" % bname)
                continue
            if not bone.deform:
                print("Not deform: %s" % bname)
                continue

            base,ext = splitBoneName(bname)
            if not ((cfg.useSplitBones and
                     base in self.splitBones.keys())):
                headTail = self.headsTails[bname]
                bone.deform = False
                defParent = self.getDeformParent(bname)
                defName = self.deformPrefix+bname
                self.headsTails[defName] = headTail
                defBone = self.bones[defName] = Bone(self, defName)
                defBone.fromInfo((bone, defParent, F_DEF, L_DEF))
                self.addConstraint(defName, copyTransform(bone.name, bone.name))


    def getDeformParent(self, bname):
        cfg = self.config
        bone = self.bones[bname]
        bone.parent = self.getParent(bone)
        if bone.parent and cfg.useDeformBones:
            pbase, pext = splitBoneName(bone.parent)
            if pbase in self.splitBones.keys():
                npieces = self.splitBones[pbase][0]
                return self.deformPrefix + pbase + ".0" + str(npieces) + pext
            else:
                parbone = self.bones[bone.parent]
                if parbone.deform:
                    return self.deformPrefix + bone.parent
                else:
                    return bone.parent
        else:
            return bone.parent


    def addSplitBones(self):
        """
            Split selected bones into two or three parts for better deformation,
            and constrain them to copy the partially.
            E.g. forearm.L => DEF-forearm.01.L, DEF-forearm.02.L, DEF-forearm.03.L
        """
        cfg = self.config

        for base in self.splitBones.keys():
            for ext in [".L", ".R"]:
                npieces,target,numAfter,followNext = self.splitBones[base]
                defName1,defName2,defName3 = splitBonesNames(base, ext, self.deformPrefix, numAfter)
                bname = base + ext
                head,tail = self.headsTails[bname]
                defParent = self.getDeformParent(bname)
                bone = self.bones[bname]
                rotMode = bone.poseFlags & P_ROTMODE
                rotMode = P_YZX

                if npieces == 2:
                    self.headsTails[defName1] = (head, ((0.5,head),(0.5,tail)))
                    self.headsTails[defName2] = (((0.5,head),(0.5,tail)), tail)

                    defBone1 = self.bones[defName1] = Bone(self, defName1)
                    defBone1.fromInfo((bname, defParent, F_DEF+F_CON, L_DEF, rotMode))
                    self.addConstraint(defName1, ('IK', 0, 1, ['IK', target+ext, 1, None, (True, False,True)]))

                    defBone2 = self.bones[defName2] = Bone(self, defName2)
                    defBone2.fromInfo((bname, defBone1, F_DEF, L_DEF, rotMode))
                    self.addConstraint(defName2, ('CopyRot', C_LOCAL, 1, [target, target+ext, (0,1,0), (0,0,0), True]))

                elif npieces == 3:
                    self.headsTails[defName1] = (head, ((0.667,head),(0.333,tail)))
                    self.headsTails[defName2] = (((0.667,head),(0.333,tail)), ((0.333,head),(0.667,tail)))
                    self.headsTails[defName3] = (((0.333,head),(0.667,tail)), tail)

                    defBone1 = self.bones[defName1] = Bone(self, defName1)
                    defBone1.fromInfo((bname, defParent, F_DEF+F_CON, L_DEF, rotMode))
                    defBone2 = self.bones[defName2] = Bone(self, defName2)
                    defBone2.fromInfo((bname, defName1, F_DEF+F_CON, L_DEF, rotMode))
                    defBone3 = self.bones[defName3] = Bone(self, defName3)
                    defBone3.fromInfo((bname, defName2, F_DEF+F_CON, L_DEF, rotMode))

                    self.addConstraint(defName1, ('IK', 0, 1, ['IK', target+ext, 1, None, (True, False,True)]))
                    if followNext:
                        self.addConstraint(defName2, ('CopyRot', C_LOCAL, 0.5, [target, target+ext, (0,1,0), (0,0,0), True]))
                        self.addConstraint(defName3, ('CopyRot', C_LOCAL, 0.5, [target, target+ext, (0,1,0), (0,0,0), True]))
                    else:
                        self.addConstraint(defName2, ('CopyRot', 0, 0.5, [bname, bname, (1,1,1), (0,0,0), False]))
                        self.addConstraint(defName3, ('CopyRot', 0, 1.0, [bname, bname, (1,1,1), (0,0,0), False]))

                defName = self.deformPrefix + base + ext
                for bone in self.bones.values():
                    if bone.parent == defName:
                        bone.parent = defName1


    def renameDeformBones(self, muscles, custom):
        for bname in muscles.keys():
            if bname in custom.keys():
                continue
            try:
                bone = self.bones[bname]
            except KeyError:
                print("Warning: deform bone %s does not exist" % bname)
                continue
            if not bone.deform:
                continue
            defName = self.deformPrefix+bname
            self.headsTails[defName] = self.headsTails[bname]
            del self.headsTails[bname]
            bone = self.bones[defName] = self.bones[bname]
            bone.name = defName
            del self.bones[bname]
            parbone = self.bones[bone.parent]
            if parbone.deform and parbone.name[0:4] != self.deformPrefix:
                bone.parent = self.deformPrefix + bone.parent


    def renameConstraints(self, constraints):
        for bname in constraints.keys():
            try:
                self.constraints[bname]
            except KeyError:
                print("No attr %s" % bname)
                continue

            for cns in self.constraints[bname]:
                try:
                    self.bones[cns.subtar]
                    ignore = True
                except KeyError:
                    ignore = False
                if not ignore:
                    defTarget = self.deformPrefix + cns.subtar
                    try:
                        self.bones[defTarget]
                        cns.subtar = defTarget
                    except:
                        print("Bone %s constraint %s has neither target %s nor %s" % (bname, cns, cns.subtar, defTarget))

            defname = self.deformPrefix + bname
            self.constraints[defname] = self.constraints[bname]
            del self.constraints[bname]


    def addDeformVertexGroups(self, vgroups, custom):
        cfg = self.config
        useSplit = (cfg.useSplitBones or cfg.useSplitNames)
        for bname,vgroup in vgroups.items():
            base = splitBoneName(bname)[0]
            if useSplit and base in self.splitBones.keys():
                pass
            elif bname in custom.keys():
                pass
            elif bname[0:4] == "hair":
                pass
            else:
                defName = self.deformPrefix+bname
                self.vertexGroups[defName] = vgroup
                try:
                    del self.vertexGroups[bname]
                except:
                    pass


    def renameDeformVertexGroups(self, muscles, custom):
        cfg = self.config
        for bname in muscles.keys():
            try:
                self.vertexGroups[bname]
            except KeyError:
                continue
            self.vertexGroups[self.deformPrefix+bname] = self.vertexGroups[bname]
            del self.vertexGroups[bname]


    def readVertexGroupFiles(self, files):
        vgroups = OrderedDict()
        for file in files:
            try:
                folder,fname = file
            except:
                folder = "armature/data/vertexgroups/hm8"
                fname = file
            filepath = os.path.join(folder, "vgrp_"+fname+".json")
            print("Loading %s" % filepath)
            vglist = loadJsonRelative(filepath)
            for key,data in vglist:
                try:
                    vgroups[key] += data
                except KeyError:
                    vgroups[key] = data
            #readVertexGroups(filepath, vgroups, vgroups)
        return vgroups


    def addSplitVertexGroups(self, vgroups):
        for bname,vgroup in vgroups.items():
            base = splitBoneName(bname)[0]
            if base in self.splitBones.keys():
                self.splitVertexGroup(bname, vgroup)
                try:
                    del self.vertexGroups[bname]
                except KeyError:
                    print("No VG %s" % bname)


    def splitVertexGroup(self, bname, vgroup):
        """
        Splits a vertex group into two or three, with weights distributed
        linearly along the bone.
        """

        base,ext = splitBoneName(bname)
        npieces,target,numAfter,_followNext = self.splitBones[base]
        defName1,defName2,defName3 = splitBonesNames(base, ext, self.deformPrefix, numAfter)

        head,tail = self.headsTails[bname]
        vec = self.locations[tail] - self.locations[head]
        vec /= vec.dot(vec)
        orig = self.locations[head] + self.origin

        vgroup1 = []
        vgroup2 = []
        vgroup3 = []

        if npieces == 2:
            for vn,w in vgroup:
                y = self.coord[vn] - orig
                x = vec.dot(y)
                if x < 0:
                    vgroup1.append((vn,w))
                elif x < 0.5:
                    vgroup1.append((vn, (1-x)*w))
                    vgroup2.append((vn, x*w))
                else:
                    vgroup2.append((vn,w))
            self.vertexGroups[defName1] = vgroup1
            self.vertexGroups[defName2] = vgroup2
        elif npieces == 3:
            for vn,w in vgroup:
                y = self.coord[vn] - orig
                x = vec.dot(y)
                if x < 0:
                    vgroup1.append((vn,w))
                elif x < 0.5:
                    vgroup1.append((vn, (1-2*x)*w))
                    vgroup2.append((vn, (2*x)*w))
                elif x < 1:
                    vgroup2.append((vn, (2-2*x)*w))
                    vgroup3.append((vn, (2*x-1)*w))
                else:
                    vgroup3.append((vn,w))
            self.vertexGroups[defName1] = vgroup1
            self.vertexGroups[defName2] = vgroup2
            self.vertexGroups[defName3] = vgroup3


    def mergeBones(self, mergers):
        for bname, merged in mergers.items():
            if len(merged) == 2:
                head,tail = self.headsTails[bname]
                _,tail2 = self.headsTails[merged[1]]
                self.headsTails[bname] = head,tail2
            vgroup = self.vertexGroups[bname]
            for mbone in merged:
                if mbone != bname:
                    vgroup += self.vertexGroups[mbone]
                    del self.vertexGroups[mbone]
                    del self.bones[mbone]
                    for child in self.bones.values():
                        if child.parent == mbone:
                            child.parent = bname
            self.vertexGroups[bname] = mergeWeights(vgroup)


    def addCSysBones(self, csysList):
        """
        Add a local coordinate system consisting of six bones around the head
        of a given bone. Useful for setting up ROTATION_DIFF drivers for
        corrective shapekeys.
        Y axis: parallel to bone.
        X axis: main bend axis, normal to plane.
        Z axis: third axis.
        """

        for bname,ikTarget in csysList:
            bone = self.bones[bname]
            parent = self.getParent(bone)
            head,_ = self.headsTails[bname]

            self.addCSysBone(bname, "_X1", parent, head, (1,0,0), 0)
            self.addCSysBone(bname, "_X2", parent, head, (-1,0,0), 0)
            csysY1 = self.addCSysBone(bname, "_Y1", parent, head, (0,1,0), 90*D)
            csysY2 = self.addCSysBone(bname, "_Y2", parent, head, (0,-1,0), -90*D)
            self.addCSysBone(bname, "_Z1", parent, head, (0,0,1), 0)
            self.addCSysBone(bname, "_Z2", parent, head, (0,0,-1), 0)

            self.addConstraint(csysY1, ('IK', 0, 1, ['IK', ikTarget, 1, None, (True, False,False)]))
            self.addConstraint(csysY2, ('IK', 0, 1, ['IK', ikTarget, 1, None, (True, False,False)]))


    def addCSysBone(self, bname, infix, parent, head, offs, roll):
        csys = csysBoneName(bname, infix)
        bone = self.bones[csys] = Bone(self, csys)
        bone.fromInfo((roll, parent, 0, L_HELP2))
        self.headsTails[csys] = (head, (head,offs))
        return csys


    def fixCSysBones(self, csysList):
        """
        Rotate the coordinate system bones into place.
        """

        for bone in self.bones.values():
            bone.calcRestMatrix()

        for bname,ikTarget in csysList:
            bone = self.bones[bname]
            mat = bone.matrixRest

            self.fixCSysBone(self, bname, "_X1", mat, 0, (1,0,0), 90*D)
            self.fixCSysBone(self, bname, "_X2", mat, 0, (1,0,0), -90*D)
            self.fixCSysBone(self, bname, "_Y1", mat, 1, (0,1,0), 90*D)
            self.fixCSysBone(self, bname, "_Y2", mat, 1, (0,1,0), -90*D)
            self.fixCSysBone(self, bname, "_Z1", mat, 2, (0,0,1), 90*D)
            self.fixCSysBone(self, bname, "_Z2", mat, 2, (0,0,1), -90*D)


    def fixCSysBone(self, bname, infix, mat, index, axis, angle):
        csys = csysBoneName(bname, infix)
        bone = self.bones[csys]
        rot = tm.rotation_matrix(angle, axis)
        cmat = mat*rot
        bone.tail = bone.head + self.bones[bname].length * cmat[:3,1]
        normal = getUnitVector(mat[:3,index])
        bone.roll = computeRoll(bone.head, bone.tail, normal)


    def addConstraint(self, bname, cns):
        from . import constraints
        try:
            cnslist = self.constraints[bname]
        except KeyError:
            cnslist = self.constraints[bname] = []
        cnslist.append(constraints.addConstraint(cns))


    def setConstraints(self, constraints):
        for bname,clist in constraints.items():
            for cns in clist:
                self.addConstraint(bname, cns)


#-------------------------------------------------------------------------------
#   Bone class
#-------------------------------------------------------------------------------

class Bone:

    def __init__(self, parser, name):
        self.name = name
        self.parser = parser
        self.origName = name
        self.head = None
        self.tail = None
        self.roll = 0
        self.parent = None
        self.setFlags(0)
        self.poseFlags = 0
        self.layers = L_MAIN
        self.length = 0
        self.customShape = None
        self.children = []

        self.location = (0,0,0)
        self.lockLocation = (0,0,0)
        self.lockRotation = (0,0,0)
        self.lockScale = (1,1,1)
        self.ikDof = (1,1,1)
        #self.lock_rotation_w = False
        #self.lock_rotations_4d = False

        self.constraints = []
        self.drivers = []


    def __repr__(self):
        return "<Bone %s %s %s>" % (self.name, self.parent, self.children)


    def fromInfo(self, info):
        if len(info) == 5:
            self.roll, self.parent, flags, self.layers, self.poseFlags = info
        else:
            self.roll, self.parent, flags, self.layers = info
            self.poseFlags = 0
        if self.parent and not flags & F_NOLOCK:
            self.lockLocation = (1,1,1)
        if flags & F_LOCKY:
            self.lockRotation = (0,1,0)
        if flags & F_LOCKROT:
            self.lockRotation = (1,1,1)
        self.setFlags(flags)
        if self.roll == None:
            halt


    def setFlags(self, flags):
        self.flags = flags
        self.conn = (flags & F_CON != 0)
        self.deform = (flags & F_DEF != 0)
        self.restr = (flags & F_RES != 0)
        self.wire = (flags & F_WIR != 0)
        self.scale = (flags & F_SCALE != 0)


    def setBone(self, head, tail):
        self.head = head
        self.tail = tail
        vec = tail - head
        self.length = math.sqrt(vec.dot(vec))

        if isinstance(self.roll, str):
            if self.roll[0:5] == "Plane":
                normal = m2b(self.parser.normals[self.roll])
                self.roll = computeRoll(self.head, self.tail, normal, bone=self)
