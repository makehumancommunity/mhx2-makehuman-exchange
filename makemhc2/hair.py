#
#    MakeMhc2 - Utility for making mhc2 meshes.
#    Like MakeClothes but slightly newer
#    Copyright (C) Thomas Larsson 2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import bpy
from collections import OrderedDict

from .materials import dumpBlenderMaterial, dumpData

class VertexGroup:
    def __init__(self, name):
        self.name = name

class ParticleVertex:
    def __init__(self, co, idx):
        self.co = co
        self.index = idx
        self.groups = [ParticleGroup()]

class ParticleGroup:
    def __init__(self):
        self.group = 0


def getHairVerts(pxy):
    pverts = []
    psys = pxy.particle_systems.active
    pset = psys.settings
    idx = 0
    m = 0
    for hair in psys.particles:
        n = 0
        #pverts.append(ParticleVertex(hair.location, idx))
        #idx += 1
        for hv in hair.hair_keys:
            co = psys.co_hair(pxy, m, n)
            pverts.append(ParticleVertex(hv.co, idx))
            print(m,n,idx,co,hv.co)
            idx += 1
            n += 1
        m += 1
    return pverts


def buildHair(struct, context, pxy):
    context.scene.objects.active = pxy
    print(pxy, context.object)
    psys = pxy.particle_systems.active
    pset = psys.settings

    #mat = pxy.data.materials[pset.material-1]
    #struct["blender_material"] = dumpBlenderMaterial(mat)

    #slist = dumpData(psys)
    pstruct = struct["particles"] = OrderedDict()

    #slist = dumpData(pset, exclude=["material_slot"])
    sstruct = pstruct["settings"] = OrderedDict()

    vlist = pstruct["hairs"] = []
    for hair in psys.particles:
        vlist.append([hv.co for hv in hair.hair_keys])


def hair2mesh(context):
    for psys in context.object.particle_systems:
        verts = []
        edges = []
        m = 0
        for hair in psys.particles:
            npoints = len(hair.hair_keys)
            verts += [hv.co for hv in hair.hair_keys]
            edges += [(n,n+1) for n in range(m, m+npoints-1)]
            m += npoints

        pset = psys.settings
        me = bpy.data.meshes.new(pset.name)
        me.from_pydata(verts, edges, [])
        ob = bpy.data.objects.new(pset.name, me)
        context.scene.objects.link(ob)

        for aname in dir(pset):
            attr = getattr(pset, aname)
            if isinstance(attr, (int, float, str, bool)):
                ob["PSET_" + aname] = attr


class OBJECT_OT_Hair2MeshButton(bpy.types.Operator):
    bl_idname = "mhc2.hair_to_mesh"
    bl_label = "Hair To Mesh"

    def execute(self, context):
        hair2mesh(context)
        print("Hair converted to mesh")
        return{'FINISHED'}

class OBJECT_OT_Mesh2HairButton(bpy.types.Operator):
    bl_idname = "mhc2.mesh_to_hair"
    bl_label = "Mesh To Hair"

    def execute(self, context):
        mesh2hair(context)
        return{'FINISHED'}
