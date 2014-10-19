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
import os
import math
D = math.pi/180

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def buildMaterial(mhMaterial, scn, cfg):
    mname = mhMaterial["name"]
    mat = bpy.data.materials.new(mname)
    if scn.render.engine == 'CYCLES':
        buildMaterialCycles(mat, mhMaterial, scn, cfg)
    else:
        buildMaterialInternal(mat, mhMaterial, scn, cfg)
    return mname, mat


def buildHairMaterial(color, scn):
    mat = bpy.data.materials.new("Hair")
    if scn.render.engine == 'CYCLES':
        buildHairMaterialCycles(mat, list(color[0:3]))
    else:
        buildHairMaterialInternal(mat, list(color[0:3]))
    return mat

# ---------------------------------------------------------------------
#   Cycles
# ---------------------------------------------------------------------

class NodeTree:
    def __init__(self, tree):
        self.nodes = tree.nodes
        self.links = tree.links
        self.ycoord1 = 1
        self.ycoord2 = 1
        self.ycoord3 = 1
        self.ycoord4 = 1
        self.ycoord5 = 1
        self.dy1 = -250
        self.dy2 = -250
        self.dy3 = -250
        self.dy4 = -250
        self.dy5 = -250

    def addNode1(self, stype):
        node = self.nodes.new(type = stype)
        node.location = (1, self.ycoord1)
        self.ycoord1 += self.dy1
        return node

    def addNode2(self, stype):
        node = self.nodes.new(type = stype)
        node.location = (251, self.ycoord2)
        self.ycoord2 += self.dy2
        return node

    def addNode3(self, stype):
        node = self.nodes.new(type = stype)
        node.location = (501, self.ycoord3)
        self.ycoord3 += self.dy3
        return node

    def addNode4(self, stype):
        node = self.nodes.new(type = stype)
        node.location = (751, self.ycoord4)
        self.ycoord4 += self.dy4
        return node

    def addNode5(self, stype):
        node = self.nodes.new(type = stype)
        node.location = (1001, self.ycoord5)
        self.ycoord5 += self.dy5
        return node

    def addTexImageNode(self, mhMat, texco, channel, cfg):
        try:
            filepath = mhMat[channel]
        except KeyError:
            return None
        tex = self.addNode2('ShaderNodeTexImage')
        tex.image = loadImage(filepath, cfg)
        self.links.new(texco.outputs['UV'], tex.inputs['Vector'])
        return tex


def buildHairMaterialCycles(mat, rgb):
    print("Creating CYCLES HAIR material", mat.name)
    mat.use_nodes= True
    mat.node_tree.nodes.clear()
    tree = NodeTree(mat.node_tree)
    links = mat.node_tree.links

    refl = tree.addNode1('ShaderNodeBsdfHair')
    refl.component = 'Reflection'
    refl.inputs['Color'].default_value[0:3] = rgb
    refl.inputs['Offset'].default_value = -4.0*D
    refl.inputs[2].default_value = 1.0
    refl.inputs[3].default_value = 0.3

    trans = tree.addNode1('ShaderNodeBsdfHair')
    trans.component = 'Transmission'
    trans.inputs['Color'].default_value[0:3] = rgb
    trans.inputs['Offset'].default_value = 0*D
    trans.inputs[2].default_value = 0.2
    trans.inputs[3].default_value = 1.0

    add = tree.addNode2('ShaderNodeAddShader')
    links.new(refl.outputs['BSDF'], add.inputs[0])
    links.new(trans.outputs['BSDF'], add.inputs[1])

    refl2 = tree.addNode2('ShaderNodeBsdfHair')
    refl2.component = 'Reflection'
    refl2.inputs['Color'].default_value[0:3] = (1,1,1)
    refl2.inputs['Offset'].default_value = 4*D
    refl2.inputs[2].default_value = 0.05
    refl2.inputs[3].default_value = 0.87

    mix = tree.addNode3('ShaderNodeMixShader')
    mix.inputs[0].default_value = 0.6
    links.new(add.outputs['Shader'], mix.inputs[1])
    links.new(refl2.outputs['BSDF'], mix.inputs[2])

    output = mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    links.new(mix.outputs['Shader'], output.inputs['Surface'])
    output.location = (751, 1)


def buildMaterialCycles(mat, mhMat, scn, cfg):
    print("Creating CYCLES material", mat.name)
    mat.use_nodes= True
    mat.node_tree.nodes.clear()
    tree = NodeTree(mat.node_tree)
    links = mat.node_tree.links
    texco = tree.addNode1('ShaderNodeTexCoord')

    fresnel = tree.addNode3('ShaderNodeFresnel')
    #fresnel.input['IOR'] = 1.45

    diffuse = tree.addNode3('ShaderNodeBsdfDiffuse')
    diffuse.inputs["Color"].default_value[0:3] =  mhMat["diffuse_color"]
    diffuse.inputs["Roughness"].default_value = 0
    diffuseTex = tree.addTexImageNode(mhMat, texco, "diffuse_texture", cfg)
    if diffuseTex:
        links.new(diffuseTex.outputs['Color'], diffuse.inputs['Color'])

    glossy = tree.addNode3('ShaderNodeBsdfGlossy')
    glossy.inputs["Color"].default_value[0:3] = mhMat["diffuse_color"]
    glossy.inputs["Roughness"].default_value = 0
    glossyTex = tree.addTexImageNode(mhMat, texco, "specular_map_texture", cfg)
    if glossyTex:
        links.new(glossyTex.outputs['Color'], glossy.inputs['Color'])

    normalTex = tree.addTexImageNode(mhMat, texco, "normal_map_texture", cfg)
    if normalTex:
        normalTex.color_space = 'NONE'
        normalMap = tree.addNode2('ShaderNodeNormalMap')
        normalMap.space = 'TANGENT'
        normalMap.uv_map = "UVMap"
        links.new(normalTex.outputs['Color'], normalMap.inputs['Color'])
        links.new(normalMap.outputs['Normal'], fresnel.inputs['Normal'])
        links.new(normalMap.outputs['Normal'], diffuse.inputs['Normal'])
        links.new(normalMap.outputs['Normal'], glossy.inputs['Normal'])
    else:
        normalMap = None

    if diffuseTex:
        transparent = tree.addNode4('ShaderNodeBsdfTransparent')
    else:
        transparent = None

    mixGloss = tree.addNode4('ShaderNodeMixShader')
    links.new(fresnel.outputs['Fac'], mixGloss.inputs['Fac'])
    links.new(diffuse.outputs['BSDF'], mixGloss.inputs[1])
    links.new(glossy.outputs['BSDF'], mixGloss.inputs[2])

    output = tree.addNode5('ShaderNodeOutputMaterial')

    if transparent:
        mixTrans = tree.addNode5('ShaderNodeMixShader')
        links.new(diffuseTex.outputs['Alpha'], mixTrans.inputs['Fac'])
        links.new(transparent.outputs['BSDF'], mixTrans.inputs[1])
        links.new(mixGloss.outputs['Shader'], mixTrans.inputs[2])
    else:
        mixTrans = mixGloss

    links.new(mixTrans.outputs['Shader'], output.inputs['Surface'])

# ---------------------------------------------------------------------
#   Blender Internal
# ---------------------------------------------------------------------

def buildMaterialInternal(mat, mhMaterial, scn, cfg):
    for key,value in mhMaterial.items():
        if value is None:
            continue
        elif key == "diffuse_color":
            mat.diffuse_color = value
            mat.diffuse_intensity = 1.0
        elif key == "specular_color":
            mat.specular_color = value
            mat.specular_intensity = 1.0
        elif key == "shininess":
            mat.specular_hardness = 512*value
        elif key == "transparent":
            setTransparent(mat, scn)
            if value:
                mat.alpha = 0
                mat.specular_alpha = 0
        elif key == "emissive_color":
            pass
            #mat.emit = value[0]
        elif key == "ambient_color":
            mat.ambient = value[0]
        elif key == "castShadows":
            #mat.use_cast_shadows = value
            mat.use_cast_buffer_shadows = value
        elif key == "receiveShadows":
            mat.use_shadows = value
            mat.use_transparent_shadows = value
        elif key == "shadeless":
            mat.use_shadeless = value
        elif key == "wireframe":
            pass
        elif key == "translucency":
            mat.translucency = value
        elif key == "sssEnabled":
            mat.subsurface_scattering.use = value
        elif key == "sssRScale":
            mat.subsurface_scattering.radius[0] = cfg.scale*value
        elif key == "sssGScale":
            mat.subsurface_scattering.radius[1] = cfg.scale*value
        elif key == "sssBScale":
            mat.subsurface_scattering.radius[2] = cfg.scale*value
        elif key == "diffuse_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
                if mtex:
                    mtex.use_map_color_diffuse = True
                    mtex.use_map_alpha = True
                    mtex.diffuse_color_factor = mhMaterial["diffuse_map_intensity"]
                    mtex.alpha_factor = 1.0
                    setTransparent(mat, scn)
                    mat.alpha = 0
                    mat.specular_alpha = 0
        elif key == "specular_map_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
                if mtex:
                    mtex.use_map_specular = True
                    mtex.specular_factor = mhMaterial["specular_map_intensity"]
                    mtex.use_map_reflect = True
                    mtex.reflection_factor = 1.0
        elif key == "normal_map_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
                if mtex:
                    mtex.normal_factor = cfg.scale # mhMaterial["normal_map_intensity"]
                    mtex.use_map_normal = True
                    tex = mtex.texture
                    tex.use_normal_map = True
        elif key == "bump_map_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
                if mtex:
                    mtex.use_map_normal = True
                    mtex.normal_factor = cfg.scale #mhMaterial["bump_map_intensity"]
                    mtex.use_rgb_to_intensity = True
                    tex = mtex.texture
                    tex.use_normal_map = False
        elif key == "displacement_map_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
                if mtex:
                    mtex.use_map_displacement = True
                    mtex.displacement_factor = cfg.scale #mhMaterial["displacement_map_intensity"]
                    mtex.use_rgb_to_intensity = True



def setTransparent(mat, scn):
    mat.use_transparency = True
    if scn.render.use_raytrace:
        mat.transparency_method = 'RAYTRACE'
    else:
        mat.transparency_method = 'Z_TRANSPARENCY'


def loadImage(filepath, cfg):
    abspath = os.path.join(cfg.folder, filepath)
    try:
        img = bpy.data.images.load(abspath)
    except RuntimeError:
        print("Unable to load \"%s\"" % abspath)
        return None
    img.name = os.path.splitext(os.path.basename(filepath))[0]
    #img.use_premultiply = True
    return img


def addTexture(mat, filepath, cfg):
    img = loadImage(filepath, cfg)
    if img is None:
        return None
    tex = bpy.data.textures.new(img.name, 'IMAGE')
    tex.image = img

    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = False
    mtex.use_rgb_to_intensity = False

    return mtex

# ---------------------------------------------------------------------
#   Get material from mhc2 file
# ---------------------------------------------------------------------

def getMaterial(mhMaterial, gname):
    if isinstance(mhMaterial, str):
        if mhMaterial == "Invisio":
            return {
                "name" : ("%s:Invisio" % gname),
                "diffuse_map_intensity" : 0,
                "specular_map_intensity" : 0,
                "shininess" : 0,
                "opacity" : 0,
                "shadeless" : True,
                "wireframe" : False,
                "transparent" : True,
                "alphaToCoverage" : True,
                "backfaceCull" : True,
                "depthless" : True,
                "castShadows" : False,
                "receiveShadows" : False,
                "sssEnabled" : False
            }
    raise RuntimeError("Unable to get material %s" % mhMaterial)

# ---------------------------------------------------------------------
#   Blender Internal specific material
# ---------------------------------------------------------------------

def buildBlenderMaterial(struct):
    mat = bpy.data.materials.new(struct["name"])
    for key,value in struct.items():
        if key == "diffuse_ramp":
            mat.use_diffuse_ramp = True
            buildRamp(mat.diffuse_ramp, value)
        elif key == "specular_ramp":
            mat.use_specular_ramp = True
            buildRamp(mat.specular_ramp, value)
        else:
            setSimple(mat, key, value)
    return mat


def setSimple(rna, key, data):
    try:
        setattr(rna, key, data)
    except AttributeError:
        pass
        #print("***", key, data)


def buildRamp(ramp, struct):
    for key,value in struct.items():
        if key == "elements":
            for elt in value:
                element = ramp.elements.new(elt["position"])
                element.color = elt["color"]
        else:
            setSimple(ramp, key, value)

# ---------------------------------------------------------------------
#   Default hair material
# ---------------------------------------------------------------------

ColorItems = [("BLACK", "Black", "Black"),
              ("WHITE", "White", "White"),
              ("GREY", "Grey", "Grey"),
              ("BLOND", "Blond", "Blond"),
              ("BROWN", "Brown", "Brown"),
             ]

ColorRGB = {
    'BLACK' : [0,0,0],
    'WHITE' : [0.6, 0.6, 0.6],
    'GREY' : [0.2, 0.2, 0.2],
    'BLOND' : [0.8, 0.5, 0.2],
    'BROWN' : [0.035, 0.004, 0.002],
}

def buildHairMaterialInternal(mat, rgb):
    mat.diffuse_color = rgb
    mat.diffuse_intensity = 0.1
    mat.specular_color = rgb

    mat.use_transparency = True
    mat.transparency_method = 'MASK'
    mat.alpha = 1.0
    mat.specular_alpha = 0.0

    mat.use_diffuse_ramp = True
    mat.diffuse_ramp_blend = 'MIX'
    mat.diffuse_ramp_factor = 1
    mat.diffuse_ramp_input = 'SHADER'

    mat.use_specular_ramp = True
    mat.specular_ramp_blend = 'MIX'
    mat.specular_ramp_factor = 1
    mat.specular_ramp_input = 'SHADER'

    defaultRamp(mat.diffuse_ramp, rgb)
    defaultRamp(mat.specular_ramp, rgb)

    mat.strand.root_size = 2
    mat.strand.tip_size = 1
    mat.strand.width_fade = 1
    return mat


def defaultRamp(ramp, rgb):
    ramp.interpolation = 'LINEAR'
    ramp.elements.new(0.1)
    ramp.elements.new(0.2)
    for n,data in enumerate([
        (0, rgb+[0]),
        (0.07, rgb+[1]),
        (0.6, rgb+[1]),
        (1.0, rgb+[0])
        ]):
        elt = ramp.elements[n]
        elt.position, elt.color = data

# ---------------------------------------------------------------------
#   Simple materials for helpers
# ---------------------------------------------------------------------

def makeSimpleMaterials(ob):
    from .hm8 import VertexRanges

    for mname,color,helper in [
            ("Red", (1,0,0), "Tights"),
            ("Blue", (0,0,1), "Skirt"),
            ("Yellow", (1,1,0), "Hair"),
            ("Green", (0,1,0), "Joints")
        ]:

        for mat in ob.data.materials:
            if mat.name == mname:
                return

        mat = bpy.data.materials.new(mname)
        mat.diffuse_color = color
        mn = len(ob.data.materials)
        ob.data.materials.append(mat)

        vrange = range(VertexRanges[helper][0], VertexRanges[helper][1])
        for f in ob.data.polygons:
            for vn in f.vertices:
                if vn in vrange:
                    print(f.index,vn,mn)
                    f.material_index = mn
                    break


class VIEW3D_OT_AddSimpleMaterialsButton(bpy.types.Operator):
    bl_idname = "mhx2.add_simple_materials"
    bl_label = "Add Simple Materials"
    bl_description = "Add simple materials to helper geometry"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob and ob.MhxHuman)

    def execute(self, context):
        makeSimpleMaterials(context.object)
        return{'FINISHED'}
