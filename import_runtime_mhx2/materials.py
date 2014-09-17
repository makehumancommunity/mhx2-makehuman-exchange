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

# ---------------------------------------------------------------------
#   Cycles
# ---------------------------------------------------------------------

class NodeTree:
    def __init__(self, tree):
        self.nodes = tree.nodes
        self.links = tree.links
        self.texco = None

        self.ycoord1 = 1
        self.ycoord2 = 1
        self.ycoord3 = 1
        self.ycoord4 = 1
        self.dy1 = 300
        self.dy2 = 300
        self.dy3 = 200
        self.dy4 = 200

    def addTexcoNode(self):
        texco = self.texco = self.nodes.new(type = 'ShaderNodeTexCoord')
        texco.location = (1, self.ycoord1)
        self.ycoord1 += self.dy1
        return texco

    def addTexImageNode(self, mhMat, channel, cfg):
        try:
            filepath = mhMat[channel]
        except KeyError:
            return None
        tex = self.nodes.new(type = 'ShaderNodeTexImage')
        tex.image = loadImage(filepath, cfg)
        self.links.new(self.texco.outputs['UV'], tex.inputs['Vector'])
        tex.location = (251, self.ycoord2)
        self.ycoord2 += self.dy2
        return tex

    def addBsdfNode(self, stype):
        node = self.nodes.new(type = stype)
        node.location = (501, self.ycoord3)
        self.ycoord3 += self.dy3
        return node

    def addMixNode(self):
        mix = self.nodes.new(type = 'ShaderNodeMixShader')
        mix.location = (751, self.ycoord4)
        self.ycoord4 += self.dy4
        return mix


def buildMaterialCycles(mat, mhMat, scn, cfg):
    print("Creating CYCLES material", mat.name)
    mat.use_nodes= True
    mat.node_tree.nodes.clear()
    tree = NodeTree(mat.node_tree)
    links = mat.node_tree.links
    texco = tree.addTexcoNode()

    diffuse = tree.addBsdfNode('ShaderNodeBsdfDiffuse')
    diffuse.inputs["Color"].default_value[0:3] =  mhMat["diffuse_color"]
    diffuse.inputs["Roughness"].default_value = 0
    diffuseTex = tree.addTexImageNode(mhMat, "diffuse_texture", cfg)
    if diffuseTex:
        links.new(diffuseTex.outputs['Color'], diffuse.inputs['Color'])
        transparent = tree.addBsdfNode('ShaderNodeBsdfTransparent')
    else:
        transparent = None

    glossy = tree.addBsdfNode('ShaderNodeBsdfGlossy')
    glossy.inputs["Color"].default_value[0:3] = mhMat["diffuse_color"]
    glossy.inputs["Roughness"].default_value = 0
    glossyTex = tree.addTexImageNode(mhMat, "specular_map_texture", cfg)
    if glossyTex:
        links.new(glossyTex.outputs['Color'], glossy.inputs['Color'])

    normalTex = tree.addTexImageNode(mhMat, "normal_map_texture", cfg)
    if normalTex:
        normalMap = tree.addBsdfNode('ShaderNodeNormalMap')
        normalMap.space = 'TANGENT'
        links.new(normalTex.outputs['Color'], normalMap.inputs['Color'])
        links.new(normalMap.outputs['Normal'], glossy.inputs['Normal'])
    else:
        normalMap = None

    mixGloss = tree.addMixNode()
    mixGloss.inputs['Fac'].default_value = 0.02
    links.new(diffuse.outputs['BSDF'], mixGloss.inputs[1])
    links.new(glossy.outputs['BSDF'], mixGloss.inputs[2])

    if transparent is not None:
        mixTrans = tree.addMixNode()
        links.new(diffuseTex.outputs['Alpha'], mixTrans.inputs['Fac'])
        links.new(transparent.outputs['BSDF'], mixTrans.inputs[1])
        links.new(mixGloss.outputs['Shader'], mixTrans.inputs[2])
    else:
        mixTrans = mixGloss

    output = mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    links.new(mixTrans.outputs['Shader'], output.inputs['Surface'])
    output.location = (1001, 1)

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
            mat.emit = value[0]
        elif key == "ambient_color":
            mat.ambient = value[0]
        elif key == "castShadows":
            mat.use_cast_shadows = value
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
                mtex.use_map_specular = True
                mtex.specular_factor = mhMaterial["specular_map_intensity"]
                mtex.use_map_reflect = True
                mtex.reflection_factor = 1.0
        elif key == "normal_map_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
                mtex.normal_factor = cfg.scale # mhMaterial["normal_map_intensity"]
                mtex.use_map_normal = True
                tex = mtex.texture
                tex.use_normal_map = True
        elif key == "bump_map_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
                mtex.use_map_normal = True
                mtex.normal_factor = cfg.scale #mhMaterial["bump_map_intensity"]
                mtex.use_rgb_to_intensity = True
                tex = mtex.texture
                tex.use_normal_map = False
        elif key == "displacement_map_texture":
            if value:
                mtex = addTexture(mat, value, cfg)
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
    img = bpy.data.images.load(abspath)
    img.name = os.path.splitext(os.path.basename(filepath))[0]
    #img.use_premultiply = True
    return img


def addTexture(mat, filepath, cfg):
    img = loadImage(filepath, cfg)
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
        print("***", key, data)


def buildRamp(ramp, struct):
    for key,value in struct.items():
        if key == "elements":
            for elt in value:
                element = ramp.elements.new(elt["position"])
                element.color = elt["color"]
        else:
            setSimple(ramp, key, value)
