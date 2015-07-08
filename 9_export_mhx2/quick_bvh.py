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
    ncols = 0
    nskip = 0
    nchannels = 0
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
            elif words[0] == "CHANNELS":
                n = int(words[1])
                ncols += n
                nskip += n-3
                cnames = words[-3:]
                channels[joint] = cnames[0][0] + cnames[1][0] + cnames[2][0]
            elif words[0] == "MOTION":
                useMotion = True
                nchannels = (ncols-nskip)//3
            elif useMotion and len(words) == ncols:
                frame = []
                words = words[nskip:]
                while words:
                    floats = []
                    for word in words[:3]:
                        x = float(word)
                        if abs(x) < 1e-5:
                            x = 0
                        floats.append(x)
                    frame.append(np.array(floats))
                    words = words[3:]
                frames.append(frame)
    finally:
        fp.close()
    return joints, channels, frames
                
            