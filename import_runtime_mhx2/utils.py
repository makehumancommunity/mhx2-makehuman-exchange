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
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) Thomas Larsson 2014
# Coding Standards: See http://www.makehuman.org/node/165

"""
Abstract


"""

from mathutils import Vector

def isBody(ob):
    return (ob.name.split(":")[-1] == "Body")

def getRigName(ob):
    return ob.name.split(":")[0]

def getProxyName(ob):
    return ob.name.split(":")[1]

def getMaterialName(ob):
    return ob.name.split(":")[2]

def getDeleteName(ob):
    return "Delete:" + getProxyName(ob)

def isDeleteVGroup(vgrp):
    return (vgrp.name[0:7] == "Delete:")

def getVGProxyName(string):
    return string.split(":",1)[1]


def zup(co):
    return Vector((co[0], -co[2], co[1]))

def zup2(co, s):
    return Vector((s[0]*co[0], -s[2]*co[2], s[1]*co[1]))


def multiply(list1, list2):
    [(list1[n] and list2[n]) for n in range(len(list1))]