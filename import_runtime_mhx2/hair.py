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

    if "license" in struct.keys():
        mhLicense = struct["license"]
        if "author" in mhLicense.keys():
            ob.MhxHairAuthor = mhLicense["author"]
            ob.MhxHairLicense = mhLicense["license"]
            ob.MhxHairHomePage = mhLicense["homepage"]
        else:
            ob.MhxHairAuthor = ob.MhxHairLicense = ob.MhxHairHomePage = ""

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
            pset.kink_amplitude *= ob.MhxScale
            pset.roughness_2_size /= ob.MhxScale
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
            cset.mass = 0.05
            deflector = findDeflector(ob)
            print("DEFL", deflector)


#------------------------------------------------------------------------
#   Deflector
#------------------------------------------------------------------------

def makeDeflector(pair, rig, bnames, cfg):
    _,ob = pair

    shiftToCenter(ob)
    if rig:
        for bname in bnames:
            if bname in cfg.bones.keys():
                bname = cfg.bones[bname]
            if bname in rig.pose.bones.keys():
                ob.parent = rig
                ob.parent_type = 'BONE'
                ob.parent_bone = bname
                pb = rig.pose.bones[bname]
                ob.matrix_basis = pb.matrix.inverted()*ob.matrix_basis
                ob.matrix_basis.col[3] -= Vector((0,pb.bone.length,0,0))
                break

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


def shiftToCenter(ob):
    sum = Vector()
    for v in ob.data.vertices:
        sum += v.co
    offset = sum/len(ob.data.vertices)
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

#------------------------------------------------------------------------
#   Make particle hair from mesh hair
#------------------------------------------------------------------------

def particlifyHair(context):
    scn = context.scene
    human = None
    hair = None
    for ob in context.selected_objects:
        if ob.type == 'MESH':
            if isBody(ob):
                human = ob
            else:
                hair = ob
    if human is None or hair is None:
        print("Missing human or hair object")
        return
        
    reallySelect(human, scn)
    bpy.ops.object.mode_set(mode='OBJECT')        
    reallySelect(hair, scn)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    taken = dict([(n,False) for n in range(len(hair.data.edges))])

    vedges = dict([(n,[]) for n in range(len(hair.data.vertices))])
    for e in hair.data.edges:
        vn1,vn2 = e.vertices
        vedges[vn1].append(e.index)
        vedges[vn2].append(e.index)    
    
    efaces = dict([(n,[]) for n in range(len(hair.data.edges))])
    for f in hair.data.polygons:
        for vn1,vn2 in f.edge_keys:
            for en in vedges[vn1]:
                if en in vedges[vn2]:
                    efaces[en].append(f.index)
                    break
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
    rings = []
    for en in taken.keys():
        if taken[en]:
            continue
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        hair.data.edges[en].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        ring = []
        for en1 in taken.keys():
            e1 = hair.data.edges[en1]
            if e1.select:
                taken[en1] = True
                ring.append(en1)    
        if len(ring) >= hair.MhxMinHairLength:
            rcoord = getRingCoords(ring, hair, efaces, vedges)
            if rcoord:
                rings.append(rcoord)

    '''
    cross = dict([(n,[]) for n in range(len(rings))])
    for ln1,ring1 in enumerate(rings):
        for ln2,ring2 in enumerate(rings[:ln1]):
            if crosses(ring1, ring2, efaces):
                cross[ln1].append(ln2)
                cross[ln2].append(ln1)
    
    print(cross.items())
    '''

    '''
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for ring in rings:
        print("  ", len(ring))
        for en in ring:
            hair.data.edges[en].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    '''
    
    hcoords = []
    for ring in rings:
        hcoord = []
        for r in ring:
            hcoord.append(r)
        hcoords.append(hcoord)
        print(hcoords[0])

    struct = {
        "particle_systems" : [{
            "name" : hair.name,
            "particles" : {},
        }]
    }          
    
    reallySelect(human, scn)
    addHair(human, struct, hcoords, scn)
    hair.hide = True
    hair.hide_render = True
    

def crosses(ring1, ring2, efaces):                                    
    for en1 in ring1:
        for en2 in ring2:
            for f in efaces[en1]:
                if f in efaces[en2]:
                    return True
    return False                
        
        
def getRingCoords(ring, hair, efaces, vedges):
    finals = []
    for en in ring:
        if len(efaces[en]) < 2:
            finals.append(en)

    if len(finals) != 2:
        print("Wrong ring:", ring)
        return None

    en1 = finals[0]
    en2 = finals[1]
    r1 = centrum(en1, hair)
    r2 = centrum(en2, hair)
    if r1[1] > r2[1]:
        en0 = en1
        enlast = en2
        rcoord = [r1]
    else:
        en0 = en2
        enlast = en1
        rcoord = [r2]
    print("Loop", en0, enlast)        
    en = opposite(en0, -1, efaces, vedges, hair)

    while True:
        rcoord.append(centrum(en, hair))
        en1 = opposite(en, en0, efaces, vedges, hair)
        en0 = en
        en = en1
        if en0 == enlast:
            break
    print("End loop")        
    return rcoord            
            

def opposite(en, en0, efaces, vedges, ob):
    verts = ob.data.edges[en].vertices
    for fn in efaces[en]:
        if en0 < 0 or fn not in efaces[en0]:
            f = ob.data.polygons[fn]
            for vn1,vn2 in f.edge_keys:
                if not (vn1 in verts or vn2 in verts):
                    for en1 in vedges[vn1]:
                        if en1 in vedges[vn2]:
                            return en1
    print("What", en, en0)   
    return -1            
    

def centrum(en, ob):
    vn1,vn2 = ob.data.edges[en].vertices
    c = (ob.data.vertices[vn1].co + ob.data.vertices[vn2].co)/2
    return (c[0], c[2], -c[1])
    

class VIEW3D_OT_ParticlifyHairButton(bpy.types.Operator):
    bl_idname = "mhx2.particlify_hair"
    bl_label = "Particlify Hair"
    bl_description = "Make particle hair from mesh hair"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob and ob.type == 'MESH')

    def execute(self, context):
        try:
            particlifyHair(context) 
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}
