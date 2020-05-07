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

import log
import numpy as np

def loadBvh(filepath):
    joints = []
    channels = {}
    frames = []
    locations = []
    ncols = 0
    isRoot = False
    hasLocation = False
    rotIndex = []
    joint = None
    useMotion = False
    try:
        fp = open(filepath, "rU")
        for line in fp:
            words = line.split()
            if len(words) == 0:
                pass
            elif words[0] in ["ROOT", "JOINT"]:
                joint = words[1]
                joints.append(joint)
                isRoot = (words[0] == "ROOT")
            elif words[0] == "CHANNELS":
                n = int(words[1])
                if isRoot and n > 3:
                    hasLocation = True
                rotIndex.append(ncols + n - 3)
                ncols += n
                cnames = words[-3:]
                channels[joint] = cnames[0][0] + cnames[1][0] + cnames[2][0]
            elif words[0] == "MOTION":
                useMotion = True
            elif useMotion and len(words) == ncols:
                frame = [getTriple(idx, words) for idx in rotIndex]
                frames.append(frame)                
                if hasLocation:
                    locations.append(getTriple(0, words))                
    finally:
        fp.close()
    return joints, channels, frames, locations


def getTriple(idx, words):
    triple = []
    for word in words[idx:idx+3]:
        x = float(word)
        if abs(x) < 1e-5:
            x = 0
        triple.append(x)
    return np.array(triple)
