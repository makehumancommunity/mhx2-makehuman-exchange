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

from .materials import NodeTree

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def buildSkinShader(mat, mhMat, scn, cfg):
    print("Creating skin shader", mat.name)
    mat.use_nodes= True
    mat.node_tree.nodes.clear()
    tree = NodeTree(mat.node_tree)
    links = mat.node_tree.links
    texco = tree.addNode(1, 'ShaderNodeTexCoord')

    diffuseTex = tree.addTexImageNode(mhMat, texco, "diffuse_texture", cfg)
