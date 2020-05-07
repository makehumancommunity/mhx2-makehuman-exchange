# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:         Thomas Larsson
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

import os
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .import_props import *

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

class Mhx2Import(ImportHelper):
    filename_ext = ".mhx2"
    filter_glob : StringProperty(default="*.mhx2", options={'HIDDEN'})
    filepath : StringProperty(subtype='FILE_PATH')

    useHelpers : BoolProperty(name="Helper Geometry", description="Keep helper geometry", default=False)
    useOffset : BoolProperty(name="Offset", description="Add offset for feet on ground", default=True)
    useOverride : BoolProperty(name="Override Exported Data", description="Override rig and mesh definitions in mhx2 file", default=False)

    useCustomShapes : BoolProperty(name="Custom Shapes", description="Custom bone shapes", default=True)
    useFaceShapes : BoolProperty(name="Face Shapes", description="Face shapes", default=False)
    useFaceShapeDrivers : BoolProperty(name="Face Shape Drivers", description="Drive face shapes with rig properties", default=False)
    useFaceRigDrivers : BoolProperty(name="Face Rig Drivers", description="Drive face rig with rig properties", default=True)
    useFacePanel : BoolProperty(name="Face Panel", description="Face panel", default=False)
    useRig : BoolProperty(name="Add Rig", description="Add rig", default=True)
    finalizeRigify : BoolProperty(name="Finalize Rigify", description="If off, only load metarig. Press Finalize Rigify to complete rigification later", default=True)
    useRotationLimits : BoolProperty(name="Rotation Limits", description="Use rotation limits for MHX rig", default=True)
    useDeflector : BoolProperty(name="Add Deflector", description="Add deflector", default=False)
    useHairDynamics : BoolProperty(name="Hair Dynamics", description="Add dynamics to hair", default=False)
    useHairOnProxy : BoolProperty(name="Hair On Proxy", description="Add hair to proxy rather than base human", default=False)
    useConservativeMasks : BoolProperty(name="Conservative Masks", description="Only delete faces with two delete-verts", default=True)

    useSubsurf : BoolProperty(name="Subsurface", description="Add a subsurf modifier to all meshes", default=False)
    subsurfLevels : IntProperty(name="Levels", description="Subsurface levels (viewport)", default=0)
    subsurfRenderLevels : IntProperty(name=" Render Levels", description="Subsurface levels (render)", default=1)

    useMasks : UseMaskProperty
    useHumanType : UseHumanTypeProperty

    mergeBodyParts : BoolProperty(name="Merge Body Parts", description="Merge body parts", default=False)
    mergeToProxy : BoolProperty(name="Merge To Proxy", description="Merge body parts to proxy mesh is such exists", default=False)
    mergeMaxType : MergeMaxTypeProperty

    rigType : RigTypeProperty
    genitalia : GenitaliaProperty
    usePenisRig : BoolProperty(name="Penis Rig", description="Add a penis rig", default=False)
    hairType : HairTypeProperty
    hairColor : HairColorProperty

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

class DatImport(ImportHelper):
    filename_ext = ".dat"
    filter_glob : StringProperty(default="*.dat", options={'HIDDEN'})
    filepath : StringProperty(subtype='FILE_PATH')

class MxaImport(ImportHelper):
    filename_ext = ".mxa"
    filter_glob : StringProperty(default="*.mxa", options={'HIDDEN'})
    filepath : StringProperty(name="File Path", description="Filepath used for loading the hair file", maxlen=1024, default="")

class MhpImport(ImportHelper):
    filename_ext = ".mhp"
    filter_glob : StringProperty(default="*.mhp", options={'HIDDEN'})
    filepath : StringProperty(
    name="File Path",
    description="File path used for mhp file",
    maxlen= 1024, default= "")

class MhpExport(ExportHelper):
    filename_ext = ".mhp"
    filter_glob : StringProperty(default="*.mhp", options={'HIDDEN'})
    filepath : StringProperty(
    name="File Path",
    description="File path used for mhp file",
    maxlen= 1024, default= "")

class BvhImport(ImportHelper):
    filename_ext = ".bvh"
    filter_glob : StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath : StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")



class UnitsString:
    units : StringProperty()

class StringString:
    string : StringProperty()

class KeyString:
    key : StringProperty()

class PrefixString:
    prefix : StringProperty()

class DataString:
    data : StringProperty()

class ToggleString:
    toggle : StringProperty()

class VisemeString:
    viseme : StringProperty()

class FilenameString:
    filename : StringProperty()

class UseHeadBool:
    useHead : BoolProperty(name="Head animation", description="Include head and eye movements", default=True)

