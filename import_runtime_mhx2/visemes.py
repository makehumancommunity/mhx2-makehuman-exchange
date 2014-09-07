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

import bpy
from bpy.props import *
from .utils import updateScene
from .drivers import getArmature

theVisemes = None
theMoho = None
theLayout = None
theFaceShapes = None

def loadVisemeData():
    global theVisemes, theMoho, theLayout, theFaceShapes
    from .load_json import loadJsonRelative
    if theMoho is None:
        struct = loadJsonRelative("data/hm8/faceshapes/faceshapes.json")
        theFaceShapes = struct["targets"].keys()
        struct = loadJsonRelative("data/hm8/faceshapes/visemes.json")
        theLayout = struct["layout"]
        theVisemes = struct["visemes"]
        theMoho = struct["moho"]

def getFaceShapes():
    global theFaceShapes
    loadVisemeData()
    return theFaceShapes

def getLayout():
    global theLayout
    loadVisemeData()
    return theLayout

def getVisemes():
    global theVisemes
    loadVisemeData()
    return theVisemes

def getMoho():
    global theMoho
    loadVisemeData()
    return theMoho



def setViseme(vis, rig):
    for key in getFaceShapes():
        rig["Mhs"+key] = 0.0
    for key,value in getVisemes()[vis]:
        rig["Mhs"+key] = value


class VIEW3D_OT_SetVisemeButton(bpy.types.Operator):
    bl_idname = "mhx2.set_viseme"
    bl_label = "X"
    bl_description = "Set viseme"
    bl_options = {'UNDO'}

    viseme = StringProperty()

    def execute(self, context):
        rig = getArmature(context.object)
        if rig:
            setViseme(self.viseme, rig)
            updateScene(context)
        return{'FINISHED'}


def openFile(context, filepath):
    (path, fileName) = os.path.split(filepath)
    (name, ext) = os.path.splitext(fileName)
    return open(filepath, "rU")

def readMoho(rig, scn, filepath, offs):
    rig = getArmature(context.object)
    if rig:
    context.scene.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    fp = openFile(context, filepath)
    for line in fp:
        words= line.split()
        if len(words) < 2:
            pass
        else:
            t = int(words[0]) + offs
            vis = theMoho[words[1]]
            setViseme(context, vis, True, t)
    fp.close()
    setInterpolation(rig)
    updatePose(context)
    print("Moho file %s loaded" % filepath)


class VIEW3D_OT_LoadMohoButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx2.load_moho"
    bl_label = "Load Moho"
    bl_description = "Load Moho (.dat) file"
    bl_options = {'UNDO'}

    filename_ext = ".dat"
    filter_glob = StringProperty(default="*.dat", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        rig = getArmature(context.object)
        if rig:
            loadMoho(context, self.filepath, 1.0)
        return{'FINISHED'}
