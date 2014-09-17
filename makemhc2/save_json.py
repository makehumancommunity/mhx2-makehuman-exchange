#
#    MakeProxy - Utility for making proxy meshes.
#    Like MakeClothes but slightly newer
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

import json
import gzip
from mathutils import Vector, Color

def saveJson(struct, filepath, binary=False):
    if binary:
        bytes = encodeJsonData(struct, "")
        #bytes = json.dumps(struct)
        with gzip.open(filepath, 'wb') as fp:
            fp.write(bytes)
    else:
        import codecs
        string = encodeJsonData(struct, "")
        with codecs.open(filepath, "w", encoding="utf-8") as fp:
            fp.write(string)
            fp.write("\n")


def encodeJsonData(data, pad=""):
    if data is None:
        return "null"
    elif isinstance(data, (bool)):
        if data:
            return "true"
        else:
            return "false"
    elif isinstance(data, (float)):
        if abs(data) < 1e-6:
            return "0"
        else:
            return "%.5g" % data
    elif isinstance(data, (int)):
        return str(data)

    elif isinstance(data, (str)):
        return "\"%s\"" % data
    elif isinstance(data, (list, tuple, Vector, Color)):
        if leafList(data):
            string = "["
            string += ",".join([encodeJsonData(elt) for elt in data])
            return string + "]"
        else:
            string = "["
            string += ",".join(
                ["\n    " + pad + encodeJsonData(elt, pad+"    ")
                 for elt in data])
            if string == "[":
                return "[]"
            else:
                return string + "\n%s]" % pad
    elif isinstance(data, dict):
        string = "{"
        string += ",".join(
            ["\n    %s\"%s\" : " % (pad, key) + encodeJsonData(value, pad+"    ")
             for key,value in data.items()])
        if string == "{":
            return "{}"
        else:
            return string + "\n%s}" % pad
    else:
        try:
            string = "["
            string += ",".join([encodeJsonData(elt) for elt in data])
            return string + "]"
        except:
            print(data)
            print(data.type)
            raise RuntimeError("Can't encode: %s %s" % (data, data.type))


def leafList(data):
    for elt in data:
        if isinstance(elt, (list,dict)):
            return False
    return True
