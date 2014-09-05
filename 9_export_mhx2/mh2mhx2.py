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

import os.path
import sys
import codecs
from collections import OrderedDict
import numpy as np

from core import G
import exportutils
import log

import skeleton
from .save_json import saveJson
from .hm8 import getBaseMesh


def exportMhx2(filepath, cfg):
    G.app.progress(0, text="Preparing")

    human = cfg.human
    cfg.setupTexFolder(filepath)

    log.message("Write MHX2 file %s" % filepath)

    filename = os.path.basename(filepath)
    folder = os.path.dirname(filepath)
    name = cfg.goodName(os.path.splitext(filename)[0])

    # Collect objects, scale meshes and filter out hidden faces/verts, scale rig
    objects = human.getObjects(excludeZeroFaceObjs=True)
    meshes = [obj.mesh.clone(cfg.scale, True) for obj in objects]
    skel = human.getSkeleton()
    if skel:
        skel = skel.scaled(cfg.scale)

    G.app.progress(0.5, text="Exporting %s" % filepath)

    # Generate bone weights for all meshes up front so they can be reused for all
    if skel:
        rawWeights = human.getVertexWeights()  # Basemesh weights
        for mesh in meshes:
            if mesh.object.proxy:
                # Transfer weights to proxy
                parentWeights = skeleton.getProxyWeights(mesh.object.proxy, rawWeights)
            else:
                parentWeights = rawWeights
            # Transfer weights to face/vert masked and/or subdivided mesh
            weights = mesh.getWeights(parentWeights)

            # Attach these vertexWeights to the mesh to pass them around the
            # exporter easier, the cloned mesh is discarded afterwards, anyway
            mesh.vertexWeights = weights
    else:
        # Attach trivial weights to the meshes
        for mesh in meshes:
            mesh.vertexWeights = dict()

    mhFile = OrderedDict()

    mhFile["basemesh"] = getBaseMesh()

    if skel:
        mhSkel = mhFile["skeleton"] = OrderedDict()
        addSkeleton(mhSkel, skel, name, cfg)

    if cfg.useMaterials:
        mhMaterials = mhFile["materials"] = []
        mats = {}
        for mesh in meshes:
            mats[mesh.name] = mname = getMaterialName(name, mesh.name, mesh.material.name)
            addMaterial(mhMaterials, mesh.material, mname, folder, cfg)

    mhGeos = mhFile["geometries"] = []
    for mesh in meshes:
        mname = getGeoName(name, mesh.name)
        addGeometry(mhGeos, mesh, skel, mats, mname, cfg)

    saveJson(mhFile, filepath, cfg.useBinary)
    G.app.progress(1)
    log.message("%s written" % filepath)

#-----------------------------------------------------------------------
#   Materials
#-----------------------------------------------------------------------

def addMaterial(mhMaterials, mat, mname, folder, cfg):
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

    addTexture(mhMat, "diffuse_texture", mat.diffuseTexture, folder, cfg)
    addTexture(mhMat, "specular_map_texture", mat.specularMapTexture, folder, cfg)
    addTexture(mhMat, "normal_map_texture", mat.normalMapTexture, folder, cfg)
    addTexture(mhMat, "transparency_map_texture", mat.transparencyMapTexture, folder, cfg)
    addTexture(mhMat, "bump_map_texture", mat.bumpMapTexture, folder, cfg)
    addTexture(mhMat, "displacement_map_texture", mat.displacementMapTexture, folder, cfg)
    addTexture(mhMat, "ao_map_texture", mat.aoMapTexture, folder, cfg)


def addTexture(mhMat, key, filepath, folder, cfg):
    if not filepath:
        #mhMat[key] = None
        return
    newpath = cfg.copyTextureToNewLocation(filepath)
    texfile = os.path.basename(newpath)
    relpath = os.path.relpath(os.path.abspath(newpath), folder)
    #relpath = os.path.join("textures", os.path.basename(newpath))
    mhMat[key] = relpath.replace("\\","/")

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

def addGeometry(mhGeos, mesh, skel, mats, mname, cfg):
    mhGeo = OrderedDict()
    mhGeos.append(mhGeo)
    mhName = mhGeo["name"] = mname
    mhGeo["offset"] = cfg.offset
    mhGeo["scale"] = cfg.scale
    try:
        mhGeo["material"] = mats[mesh.name]
    except KeyError:
        pass

    mhMesh = mhGeo["mesh"] = OrderedDict()
    addMesh(mhMesh, mesh)
    mhSeed = mhGeo["seed_mesh"] = OrderedDict()
    addMesh(mhSeed, mesh.object.getSeedMesh())

    pxy = mesh.object.proxy
    if pxy:
        if pxy.type == 'Proxymeshes':
            mhGeo["human"] = True
        else:
            mhGeo["human"] = False
        mhProxy = mhGeo["proxy"] = OrderedDict()
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
    else:
        mhGeo["human"] = True

    if mesh.vertexWeights:
        mhWeights = mhGeo["weights"] = OrderedDict()
        for bone in skel.getBones():
            try:
                idxs,weights = mesh.vertexWeights[bone.name]
            except KeyError:
                continue
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
    return ("%s:%s" % (getSkelName(name), os.path.splitext(meshname)[0].capitalize()))

def getMaterialName(name, meshname, matname):
    return ("%s:%s" % (getGeoName(name, meshname), matname.capitalize()))
