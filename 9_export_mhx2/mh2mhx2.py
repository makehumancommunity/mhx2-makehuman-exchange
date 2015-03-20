#
#    MakeHuman .mhx2 exporter
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

Mhx2Version = "0.22"

import os.path
import sys
import codecs
from collections import OrderedDict
import numpy as np
import shutil

from core import G
import log

import skeleton
from .save_json import saveJson
from .hm8 import getBaseMesh


def exportMhx2(filepath, cfg):
    G.app.progress(0, text="Preparing")

    human = cfg.human
    cfg.setupTexFolder(filepath)

    log.message("Write MHX2 file %s" % filepath)
    G.app.progress(0.1, text="Exporting %s" % filepath)

    filename = os.path.basename(filepath)
    name = cfg.goodName(os.path.splitext(filename)[0])
    texhandler = TextureHandler(filepath)

    # Collect objects, scale meshes and filter out hidden faces/verts, scale rig
    objects = human.getObjects(excludeZeroFaceObjs=True)
    meshes = [obj.mesh.clone(cfg.scale, True) for obj in objects]
    #human.changeVertexMask(None)
    skel = human.getSkeleton()
    if skel:
        skel = skel.scaled(cfg.scale)
        if not skel.isInRestPose():
            skel = skel.createFromPose()
        rawWeights = human.getVertexWeights()  # Basemesh weights
    else:
        rawWeights = None

    mhFile = OrderedDict()
    mhFile["mhx2_version"] = Mhx2Version
    #mhFile["basemesh"] = getBaseMesh()

    if skel:
        mhSkel = mhFile["skeleton"] = OrderedDict()
        addSkeleton(mhSkel, skel, name, cfg)

    mhMaterials = mhFile["materials"] = []
    mats = {}
    for mesh in meshes:
        mats[mesh.name] = mname = getMaterialName(name, mesh.name, mesh.material.name)
        addMaterial(mhMaterials, mesh.material, mname, texhandler)

    mhGeos = mhFile["geometries"] = []
    for mesh in meshes:
        mname = getGeoName(name, mesh.name)
        addGeometry(mhGeos, mesh, skel, rawWeights, mats, mname, cfg)

    G.app.progress(0.2, text="Writing Json file %s" % filepath)
    saveJson(mhFile, filepath, cfg.useBinary)
    G.app.progress(1)
    log.message("%s written" % filepath)

#-----------------------------------------------------------------------
#   Materials
#-----------------------------------------------------------------------

def addMaterial(mhMaterials, mat, mname, texhandler):
    mhMat = OrderedDict()
    mhMaterials.append(mhMat)
    mhMat["name"] = mname

    mhMat["diffuse_color"] = mat.diffuseColor.asTuple()
    mhMat["diffuse_map_intensity"] = 1.0
    mhMat["specular_color"] = mat.specularColor.asTuple()
    mhMat["specular_map_intensity"] = mat.specularMapIntensity
    mhMat["shininess"] = mat.shininess
    mhMat["opacity"] = mat.opacity
    mhMat["translucency"] = mat.translucency
    mhMat["emissive_color"] = mat.emissiveColor.asTuple()
    mhMat["ambient_color"] = mat.ambientColor.asTuple()
    mhMat["transparency_map_intensity"] = mat.transparencyMapIntensity

    mhMat["shadeless"] = mat.shadeless
    mhMat["wireframe"] = mat.wireframe
    mhMat["transparent"] = mat.transparent
    mhMat["alphaToCoverage"] = mat.alphaToCoverage
    mhMat["backfaceCull"] = mat.backfaceCull
    mhMat["depthless"] = mat.depthless
    mhMat["castShadows"] = mat.castShadows
    mhMat["receiveShadows"] = mat.receiveShadows

    mhMat["sssEnabled"] = mat.sssEnabled
    mhMat["sssRScale"] = mat.sssRScale
    mhMat["sssGScale"] = mat.sssBScale
    mhMat["sssBScale"] = mat.sssBScale

    texhandler.addTexture(mhMat, "diffuse_texture", mat.diffuseTexture)
    texhandler.addTexture(mhMat, "specular_map_texture", mat.specularMapTexture)
    texhandler.addTexture(mhMat, "normal_map_texture", mat.normalMapTexture)
    texhandler.addTexture(mhMat, "transparency_map_texture", mat.transparencyMapTexture)
    texhandler.addTexture(mhMat, "bump_map_texture", mat.bumpMapTexture)
    texhandler.addTexture(mhMat, "displacement_map_texture", mat.displacementMapTexture)
    texhandler.addTexture(mhMat, "ao_map_texture", mat.aoMapTexture)


class TextureHandler:

    def __init__(self, filepath):
        self.outFolder = os.path.realpath(os.path.dirname(filepath))
        self.texFolder = self.getSubFolder(self.outFolder, "textures")
        self._copiedFiles = {}


    def getSubFolder(self, path, name):
        folder = os.path.join(path, name)
        if not os.path.exists(folder):
            log.message("Creating folder %s", folder)
            try:
                os.mkdir(folder)
            except:
                log.error("Unable to create separate folder:", exc_info=True)
                return None
        return folder


    def copyTextureToNewLocation(self, filepath):
        srcDir = os.path.abspath(os.path.expanduser(os.path.dirname(filepath)))
        filename = os.path.basename(filepath)

        newpath = os.path.abspath( os.path.join(self.texFolder, filename) )
        try:
            self._copiedFiles[filepath]
            done = True
        except:
            done = False
        if not done:
            try:
                shutil.copyfile(filepath, newpath)
            except:
                log.message("Unable to copy \"%s\" -> \"%s\"" % (filepath, newpath))
            self._copiedFiles[filepath] = True

        relpath = os.path.relpath(newpath, self.outFolder)
        return str(os.path.normpath(relpath))


    def addTexture(self, mhMat, key, filepath):
        if not filepath:
            return
        newpath = self.copyTextureToNewLocation(filepath)
        mhMat[key] = newpath.replace("\\","/")


    def goodName(self, name):
        string = name.replace(" ", "_").replace("-","_").lower()
        return string

#-----------------------------------------------------------------------
#   Skeletons
#-----------------------------------------------------------------------

def addSkeleton(mhSkel, skel, name, cfg):
    mhSkel["name"] = getSkelName(name)
    mhSkel["offset"] = cfg.offset
    mhSkel["scale"] = cfg.scale
    mhBones = mhSkel["bones"] = []
    for bone in skel.getBones():
        addBone(mhBones, bone)


def addBone(mhBones, bone):
    mhBone = OrderedDict()
    mhBones.append(mhBone)
    mhBone["name"] = bone.name
    if bone.parent:
        mhBone["parent"] = bone.parent.name
    mhBone["head"] = list(bone.getHead())
    mhBone["tail"] = list(bone.getTail())
    mhBone["roll"] = bone.getRoll()
    #mat = bone.getRelativeMatrix(cfg.meshOrientation, cfg.localBoneAxis, cfg.offset)
    #mhBone["matrix"] = [list(mat[0,:]), list(mat[1,:]), list(mat[2,:]), list(mat[3,:])]

#-----------------------------------------------------------------------
#   Meshes
#-----------------------------------------------------------------------

def addGeometry(mhGeos, mesh, skel, rawWeights, mats, mname, cfg):
    from .uuid4 import uuid4

    mhGeo = OrderedDict()
    mhGeos.append(mhGeo)

    pxy = mesh.object.proxy
    if pxy:
        if pxy.type == 'Proxymeshes':
            mhGeo["license"] = BaseMeshLicense
        else:
            addProxyLicense(mhGeo, pxy)
    else:
        mhGeo["license"] = BaseMeshLicense

    mhName = mhGeo["name"] = mname
    mhGeo["uuid"] = str(uuid4())
    mhGeo["offset"] = cfg.offset
    mhGeo["scale"] = cfg.scale
    try:
        mhGeo["material"] = mats[mesh.name]
    except KeyError:
        pass

    mhMesh = mhGeo["mesh"] = OrderedDict()
    if pxy and pxy.type == 'Proxymeshes':
        addMesh(mhMesh, mesh.clone())
    else:
        addMesh(mhMesh, mesh)
    mhSeed = mhGeo["seed_mesh"] = OrderedDict()
    obj = mesh.object
    addMesh(mhSeed, obj.getSeedMesh())

    if pxy:
        if pxy.type == 'Proxymeshes':
            mhGeo["human"] = True
            #vmask = obj.vertexMask
            obj.changeVertexMask(None)
            #obj.update()
            mhProxySeed = mhGeo["proxy_seed_mesh"] = OrderedDict()
            addMesh(mhProxySeed, obj.mesh)
            #obj.changeVertexMask(vmask)
            #obj.update()
        else:
            mhGeo["human"] = False
            mhProxySeed = None

        if skel:
            if hasattr(mesh, "getVertexWeights"):
                pxySeedWeights = pxy.getVertexWeights(rawWeights)
                weights = mesh.getVertexWeights(pxySeedWeights)
            else:
                pxySeedWeights = skeleton.getProxyWeights(pxy, rawWeights)
                weights = mesh.getWeights(pxySeedWeights)
            addWeights(mhMesh, skel, weights)
            if mhProxySeed:
                addWeights(mhSeed, skel, rawWeights)
                addWeights(mhProxySeed, skel, pxySeedWeights)
            else:
                addWeights(mhSeed, skel, pxySeedWeights)

        mhProxy = mhGeo["proxy"] = OrderedDict()
        addProxyLicense(mhProxy, pxy)
        mhProxy["name"] = pxy.name.capitalize()
        mhProxy["type"] = pxy.type
        mhProxy["uuid"] = pxy.uuid
        mhProxy["basemesh"] = pxy.basemesh
        mhProxy["tags"] = list(pxy.tags)

        mhProxy["fitting"] = np.array(
            [(vnums, pxy.weights[n], pxy.offsets[n])
                for n,vnums in enumerate(pxy.ref_vIdxs)]
            )
        #mhProxy["ref_wvIdxs"] = pxy.ref_wvIdxs
        mhProxy["delete_verts"] = pxy.deleteVerts
        if pxy.vertexBoneWeights:
            mhProxy["vertex_bone_weights"] = pxy.vertexBoneWeights.data
        else:
            mhProxy["vertex_bone_weights"] = None
    else:
        mhGeo["human"] = True
        if skel:
            addWeights(mhSeed, skel, rawWeights)
            if hasattr(mesh, "getVertexWeights"):
                weights = mesh.getVertexWeights(rawWeights)
            else:
                weights = mesh.getWeights(rawWeights)
            addWeights(mhMesh, skel, weights)


def addWeights(mhMesh, skel, vertexWeights):
    mhWeights = mhMesh["weights"] = OrderedDict()
    for bone in skel.getBones():
        try:
            if hasattr(vertexWeights, "data"):
                idxs,weights = vertexWeights.data[bone.name]
            else:
                idxs,weights = vertexWeights[bone.name]
        except KeyError:
            continue
        if idxs[0] < 0:
            idxs = idxs[1:]
            weights = weights[1:]
        if len(idxs) > 0:
            mhWeights[bone.name] = np.array([(vn,weights[n]) for n,vn in enumerate(idxs)])


def addMesh(mhGeo, mesh):
    mhGeo["vertices"] = mesh.coord
    mhGeo["normals"] = mesh.vnorm
    mhGeo["faces"] = mesh.fvert
    mhGeo["uv_coordinates"] = mesh.texco
    mhGeo["uv_faces"] = mesh.fuvs


#-----------------------------------------------------------------------
#   Naming
#-----------------------------------------------------------------------

def getSkelName(name):
    return name.capitalize()


def getGeoName(name, meshname):
    mname = os.path.splitext(meshname)[0].capitalize()
    if mname == "Base":
        mname = "Body"
    return ("%s:%s" % (getSkelName(name), mname))


def getMaterialName(name, meshname, matname):
    return ("%s:%s" % (getGeoName(name, meshname), matname.capitalize()))


#-----------------------------------------------------------------------
#   Licensing
#-----------------------------------------------------------------------

'''
BaseMeshLicense = (
    ["MakeHuman 3d morphing modelled by Manuel Bastioni"],
    ["Copyright (C) 2014 Manuel Bastioni (mb@makehuman.org)"],
    ["homepage http://www.makehuman.org"],
    ["basemesh hm08"],
    ["license AGPL3 (http://www.makehuman.org/doc/node/makehuman_mesh_license.html)"],
    ["   This file is part of MakeHuman (www.makehuman.org)."],
    [""],
    ["   This program is free software: you can redistribute it and/or modify"],
    ["   it under the terms of the GNU Affero General Public License as"],
    ["   published by the Free Software Foundation, either version 3 of the"],
    ["   License, or (at your option) any later version."],
    [""],
    ["   This program is distributed in the hope that it will be useful,"],
    ["   but WITHOUT ANY WARRANTY; without even the implied warranty of"],
    ["   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"],
    ["   GNU Affero General Public License for more details."],
    [""],
    ["   You should have received a copy of the GNU Affero General Public License"],
    ["   along with this program.  If not, see <http://www.gnu.org/licenses/>."],
)
'''

BaseMeshLicense = OrderedDict([
    ("author",  "Manuel Bastioni"),
    ("license", "AGPL3 (http://www.makehuman.org/doc/node/makehuman_mesh_license.html)"),
    ("homepage", "http://www.makehuman.org/")
])

def addProxyLicense(mhGeo, pxy):
    mhLicense = mhGeo["license"] = OrderedDict()
    if hasattr(pxy, "license"):
        for key in ["author", "license", "homepage"]:
            mhLicense[key] = getattr(pxy.license, key)
    else:
        mhLicense["author"] = "MakeHuman Team"
        mhLicense["license"] = "AGPL3 (see also http://www.makehuman.org/doc/node/external_tools_license.html)"
        mhLicense["homepage"] = "http://www.makehuman.org/"


