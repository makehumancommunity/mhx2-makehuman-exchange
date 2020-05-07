# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
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
from bpy.props import *

HairColorProperty = FloatVectorProperty(
    name = "Hair Color",
    subtype = "COLOR",
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.15, 0.03, 0.005, 1.0)
    )

UseMaskProperty = EnumProperty(
    items = [
        ('IGNORE', "Ignore", "Ignore masks"),
        ('APPLY', "Apply", "Apply masks (delete vertices permanently)"),
        ('MODIFIER', "Modifier", "Create mask modifier"),
    ],
    name = "Masks",
    description = "How to deal with masks",
    default = 'MODIFIER')

UseHumanTypeProperty = EnumProperty(
    items = [
        ('BASE', "Base", "Base mesh"),
        ('PROXY', "Proxy", "Exported topology (if exists)"),
        ('BOTH', "Both", "Both base mesh and proxy mesh"),
    ],
    name = "Import Human Type",
    description = "Human types to be imported",
    default = 'BOTH')

MergeMaxTypeProperty = EnumProperty(
    items = [
        ('BODY', "Body", "Merge up to body"),
        ('HAIR', "Hair", "Merge up to hair"),
        ('CLOTHES', "Clothes", "Merge all"),
    ],
    name = "Maximum Merge Type",
    description = "Maximum type to merge",
    default = 'BODY')

def getRigTypeItems():
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
    return rigTypes

RigTypeProperty = EnumProperty(
    items = getRigTypeItems(),
    name = "Rig Type",
    description = "Rig type",
    default = 'EXPORTED')

GenitaliaProperty = EnumProperty(
    items = [
        ("NONE", "None", "None"),
        ("PENIS", "Male", "Male genitalia"),
        ("PENIS2", "Male 2", "Better male genitalia"),
        ("VULVA", "Female", "Female genitalia"),
        ("VULVA2", "Female 2", "Better female genitalia")
    ],
    name = "Genitalia",
    description = "Genitalia",
    default = 'NONE')

def getHairItems():
    hairItems = [("NONE", "None", "None")]
    folder = os.path.join(os.path.dirname(__file__), "data", "hm8", "hair")
    for file in os.listdir(folder):
        fname,ext = os.path.splitext(file)
        if ext == ".mxa":
            hairItems.append((file, fname, fname))
    return hairItems

HairTypeProperty = EnumProperty(
    items = getHairItems(),
    name = "Hair",
    description = "Hair",
    default = "NONE")
