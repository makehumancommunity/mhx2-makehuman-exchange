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

from .objects import *
from .error import *
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
    pVertList = []
    for psys in pxy.particle_systems:
        pverts = []
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
                idx += 1
                n += 1
            m += 1
        pVertList.append(pverts)
    return pVertList


def buildHair(struct, context, pxy, data):
    from .write import buildFitting

    context.scene.objects.active = pxy
    systems = struct["particle_systems"] = []
    print("SYSTEMS", len(data))
    for n,psys in enumerate(pxy.particle_systems):
        pset = psys.settings
        system = OrderedDict()
        systems.append(system)
        system["name"] = psys.name

        buildFitting(system, data[n])

        particles = system["particles"] = OrderedDict()
        for key in dir(psys):
            if key[0:10] in ["invert_ver", "vertex_gro"]:
                particles[key] = getattr(psys,key)

        slist = dumpData(pset, exclude=["material_slot"])
        settings = system["settings"] = OrderedDict()
        for key,val in slist:
            settings[key] = val

        vlist = system["hairs"] = []
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
        plist = dumpData(pset, exclude=["material_slot"])

        ob["PSYS_name"] = psys.name
        for key in dir(psys):
            if key[0:10] in ["invert_ver", "vertex_gro"]:
                ob["PSYS_" + key] = getattr(psys,key)

        for key,attr in plist:
            if attr is not None:
                ob["PSET_" + key] = attr


class OBJECT_OT_Hair2MeshButton(bpy.types.Operator):
    bl_idname = "mhc2.hair_to_mesh"
    bl_label = "Hair To Mesh"

    def execute(self, context):
        try:
            hair2mesh(context)
            print("Hair converted to mesh")
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


def mesh2hair(context):
    scn = context.scene
    hairs = []
    human = None
    for ob in scn.objects:
        if ob.select and ob.type == 'MESH':
            if not ob.data.polygons:
                hairs.append(ob)
                scn.objects.active = ob
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            elif human is None:
                human = ob
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            else:
                raise MHError("Multiple non-edge meshes selected")

    if human:
        scn.objects.active = human
        print("Human:", human.name)
        npsyses = len(human.particle_systems)
        for n in range(npsyses):
            bpy.ops.object.particle_system_remove()
    else:
        raise MhError("No human selected")

    for ob in hairs:
        bpy.ops.object.particle_system_add()
        psys = human.particle_systems.active
        pset = psys.settings
        for key,val in ob.items():
            if key[0:5] == "PSYS_":
                try:
                    setattr(psys, key[5:], val)
                except :
                    print("Skip")
                    pass
            if key[0:5] == "PSET_":
                try:
                    setattr(pset, key[5:], val)
                except :
                    print("Skip")
                    pass

        nverts = len(ob.data.vertices)
        nedges = len(ob.data.edges)
        pset.count = nverts - nedges
        hlen = int(nverts/pset.count)
        pset.hair_step = hlen-1
        pset.path_end = 1.0
        print(nverts, nedges, pset.count, hlen)

        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        pedit = scn.tool_settings.particle_edit
        pedit.use_preserve_length = False
        pedit.use_preserve_root = False
        pedit.select_mode = 'POINT'
        bpy.ops.transform.translate()

        coords = [v.co for v in ob.data.vertices]
        for m,hair in enumerate(psys.particles):
            hair.location = coords[0]
            for n,v in enumerate(hair.hair_keys):
                v.co = coords[n]
            coords = coords[hlen:]

        bpy.ops.object.mode_set(mode='OBJECT')


class OBJECT_OT_Mesh2HairButton(bpy.types.Operator):
    bl_idname = "mhc2.mesh_to_hair"
    bl_label = "Mesh To Hair"

    def execute(self, context):
        try:
            mesh2hair(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}
