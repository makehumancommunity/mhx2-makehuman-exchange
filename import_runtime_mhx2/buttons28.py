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

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

class Mhx2Import(ImportHelper):
    filename_ext = ".mhx2"
    filter_glob : StringProperty(default="*.mhx2", options={'HIDDEN'})
    filepath : StringProperty(subtype='FILE_PATH')

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
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for mhp file",
        maxlen= 1024, default= "")

class MhpExport(ExportHelper):
    filename_ext = ".mhp"
    filter_glob : StringProperty(default="*.mhp", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
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

