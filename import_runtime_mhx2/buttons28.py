# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014-2018
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
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

HairColorProperty = FloatVectorProperty(
    name = "Hair Color",
    subtype = "COLOR",
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.15, 0.03, 0.005, 1.0)
    )

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

    useMasks : EnumProperty(
        items = [('IGNORE', "Ignore", "Ignore masks"),
                 ('APPLY', "Apply", "Apply masks (delete vertices permanently)"),
                 ('MODIFIER', "Modifier", "Create mask modifier"),
                 ],
        name = "Masks",
        description = "How to deal with masks",
        default = 'MODIFIER')

    useHumanType : EnumProperty(
        items = [('BASE', "Base", "Base mesh"),
                 ('PROXY', "Proxy", "Exported topology (if exists)"),
                 ('BOTH', "Both", "Both base mesh and proxy mesh"),
                 ],
        name = "Import Human Type",
        description = "Human types to be imported",
        default = 'BOTH')
    mergeBodyParts : BoolProperty(name="Merge Body Parts", description="Merge body parts", default=False)
    mergeToProxy : BoolProperty(name="Merge To Proxy", description="Merge body parts to proxy mesh is such exists", default=False)
    mergeMaxType : EnumProperty(
        items = [('BODY', "Body", "Merge up to body"),
                 ('HAIR', "Hair", "Merge up to hair"),
                 ('CLOTHES', "Clothes", "Merge all"),
                 ],
        name = "Maximum Merge Type",
        description = "Maximum type to merge",
        default = 'BODY')

    rigTypes = []
    folder = os.path.dirname(__file__)
    for file in os.listdir(os.path.join(folder, "armature/data/rigs")):
        fname = os.path.splitext(file)[0]
        if fname == "mhx":
            mhx = ("MHX", "MHX", "An advanced control rig")
        elif fname == "exported_mhx":
            exp_mhx = ("EXPORTED_MHX", "Exported MHX", "MHX rig based on exported deform rig")
        elif fname == "rigify":
            rigify = ("RIGIFY", "Rigify", "Modified Rigify rig")
        elif fname == "exported_rigify":
            exp_rigify = ("EXPORTED_RIGIFY", "Exported Rigify", "Rigify rig based on exported deform rig")
        else:
            entry = (fname.upper(), fname.capitalize(), "%s-compatible rig" % fname.capitalize())
            rigTypes.append(entry)
    rigTypes = [('EXPORTED', "Exported", "Use rig in mhx2 file"),
                exp_mhx, exp_rigify, mhx, rigify] + rigTypes

    rigType : EnumProperty(
        items = rigTypes,
        name = "Rig Type",
        description = "Rig type",
        default = 'EXPORTED')

    genitalia : EnumProperty(
        items = [("NONE", "None", "None"),
                 ("PENIS", "Male", "Male genitalia"),
                 ("PENIS2", "Male 2", "Better male genitalia"),
                 ("VULVA", "Female", "Female genitalia"),
                 ("VULVA2", "Female 2", "Better female genitalia")],
        name = "Genitalia",
        description = "Genitalia",
        default = 'NONE')
    usePenisRig : BoolProperty(name="Penis Rig", description="Add a penis rig", default=False)

    hairlist = [("NONE", "None", "None")]
    folder = os.path.join(os.path.dirname(__file__), "data", "hm8", "hair")
    for file in os.listdir(folder):
        fname,ext = os.path.splitext(file)
        if ext == ".mxa":
            hairlist.append((file, fname, fname))

    hairType : EnumProperty(
        items = hairlist,
        name = "Hair",
        description = "Hair",
        default = "NONE")

    hairColor = HairColorProperty

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

