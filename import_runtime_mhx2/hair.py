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

import bpy
from mathutils import Vector
from .error import *
from .utils import *


def isHairStruct(struct):
    return ("particle_systems" in struct.keys())


def getHairCoords(mhHuman, mhGeo):
    from .proxy import fitProxy

    mhProxy = mhGeo["proxy"]
    offset = Vector(zup(mhHuman["offset"]))
    coords = []
    for mhSystem in mhGeo["particle_systems"]:
        pverts,scales = fitProxy(mhHuman, mhSystem["fitting"], mhProxy["bounding_box"])
        hlist = mhSystem["hairs"]
        nhairs = int(len(hlist))
        hlen = int(len(hlist[0]))
        coord = []
        for m in range(nhairs):
            coord.append( [Vector(zup(v)) + offset for v in pverts[m*hlen:(m+1)*hlen]] )
        coords.append(coord)
    return mhGeo,coords,scales

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def addHair(ob, struct, hcoords, scn, cfg=None):
    from .materials import buildBlenderMaterial, buildHairMaterial

    nsys = len(ob.particle_systems)
    for n in range(nsys):
        bpy.ops.object.particle_system_remove()
    #if nsys > 0:
    #    ob.data.materials.pop()

    if "blender_material" in struct.keys():
        mat = buildBlenderMaterial(struct["blender_material"])
    else:
        if cfg is None:
            color = scn.MhxHairColor
            useHairDynamics = scn.MhxUseHairDynamics
            useDeflector = scn.MhxUseDeflector
        else:
            color = cfg.hairColor
            useHairDynamics = cfg.useHairDynamics
            useDeflector = cfg.useDeflector
        mat = buildHairMaterial(color, scn)
    ob.data.materials.append(mat)

    for n,mhSystem in enumerate(struct["particle_systems"]):
        hcoord = hcoords[n]
        bpy.ops.object.particle_system_add()
        psys = ob.particle_systems.active
        psys.name = mhSystem["name"]
        for key,val in mhSystem["particles"].items():
            if hasattr(psys, key):
                setattr(psys, key, val)

        skull = ob.vertex_groups.new("Skull")
        for vn,w in [(879,1.0)]:
            skull.add([vn], w, 'REPLACE')
        psys.vertex_group_density = "Skull"

        pset = psys.settings
        if "settings" in mhSystem.keys():
            for key,val in mhSystem["settings"].items():
                try:
                    setattr(pset, key, val)
                except AttributeError:
                    pass
            pset.child_radius *= ob.MhxScale
        else:
            pset.type = 'HAIR'
            pset.use_strand_primitive = True
            pset.render_type = 'PATH'
            pset.child_type = 'SIMPLE'
            pset.child_radius = 0.1*ob.MhxScale

        pset.material = len(ob.data.materials)
        pset.path_start = 0
        pset.path_end = 1
        pset.count = int(len(hcoord))
        hlen = int(len(hcoord[0]))
        pset.hair_step = hlen-1

        if hasattr(pset, "cycles_curve_settings"):
            ccset = pset.cycles_curve_settings
        else:
            ccset = pset.cycles
        ccset.root_width = 1.0
        ccset.tip_width = 0
        ccset.radius_scale = 0.01*ob.MhxScale

        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        pedit = scn.tool_settings.particle_edit
        pedit.use_emitter_deflect = False
        pedit.use_preserve_length = False
        pedit.use_preserve_root = False
        ob.data.use_mirror_x = False
        pedit.select_mode = 'POINT'
        bpy.ops.transform.translate()

        for m,hair in enumerate(psys.particles):
            verts = hcoord[m]
            hair.location = verts[0]
            for n,v in enumerate(hair.hair_keys):
                v.co = verts[n]

        bpy.ops.object.mode_set(mode='OBJECT')

        if not useHairDynamics:
            psys.use_hair_dynamics = False
        else:
            psys.use_hair_dynamics = True
            cset = psys.cloth.settings
            cset.pin_stiffness = 1.0
            deflector = findDeflector(ob)
            print("DEFL", deflector)


#------------------------------------------------------------------------
#   Deflector
#------------------------------------------------------------------------

def makeDeflector(pair, rig, bname, cfg):
    _,ob = pair

    center = getCenter(ob)
    shiftOffset(ob, center)
    print(ob.matrix_basis)
    if rig:
        gmat = ob.matrix_basis.copy()
        ob.parent = rig
        ob.parent_type = 'BONE'
        ob.parent_bone = bname
        pb = rig.pose.bones[bname]
        print(ob.matrix_basis)
        print(pb.matrix)
        ob.matrix_basis = pb.matrix.inverted() * gmat
        print(ob.matrix_basis)

    ob.draw_type = 'WIRE'
    ob.field.type = 'FORCE'
    print("FIELD", ob.field, ob.field.type)
    ob.field.shape = 'SURFACE'
    ob.field.strength = 240.0
    ob.field.falloff_type = 'SPHERE'
    ob.field.z_direction = 'POSITIVE'
    ob.field.falloff_power = 2.0
    ob.field.use_max_distance = True
    ob.field.distance_max = 0.125*ob.MhxScale
    print("DONE")


def getCenter(ob):
    sum = Vector()
    for v in ob.data.vertices:
        sum += v.co
    return sum/len(ob.data.vertices)


def shiftOffset(ob, offset):
    for v in ob.data.vertices:
        v.co -= offset
    ob.location = offset


def findDeflector(human):
    rig = human.parent
    if rig:
        children = rig.children
    else:
        children = human.children
    for ob in children:
        if ob.field.type == 'FORCE':
            return ob
    print("No deflector mesh found")
    return None

