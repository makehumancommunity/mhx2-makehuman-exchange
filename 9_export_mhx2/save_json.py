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


import gzip
import numpy as np
import json

def saveJson(struct, filepath, binary=False):
    if binary:
        bdata = bytes(json.dumps(struct, cls=MHEncoder), 'utf8')
        with gzip.open(filepath, 'wb') as fp:
            fp.write(bdata)
    else:
        string = json.dumps(struct, cls=MHEncoder)
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(string)


class MHEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, np.ndarray):
            if o.dtype == 'bool':
                return o.tolist()
            else:
                return o.round(5).tolist()
        elif isinstance(o, (np.float16, np.float32, np.float64)):
            return 0 if abs(o) < 1.0e-5 else round(float(o), 5)
        elif isinstance(o, (np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(o)
        elif isinstance(o, bytes):
            return o.decode('utf-8')
        else:
            return json.JSONEncoder.default(self, o)
