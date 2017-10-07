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
import codecs
import numpy as np
import log
import sys

python3 = sys.version_info[0] >= 3


def saveJson(struct, filepath, binary=False):
    if binary:
        if python3:
            bdata = bytes(encodeJsonData3(struct, ""), 'utf8')
        else:
            bdata = encodeJsonData2(struct, "")
        with gzip.open(filepath, 'wb') as fp:
            fp.write(bdata)
    else:
        if python3:
            string = encodeJsonData3(struct, "")
        else:
            string = encodeJsonData2(struct, "")
        with codecs.open(filepath, "w", encoding="utf-8") as fp:
            fp.write(string)
            fp.write("\n")


def encodeJsonData3(data, pad=""):
    if data is None:
        return "null"
    elif isinstance(data, (bool, np.bool_)):
        if data:
            return "true"
        else:
            return "false"
    elif isinstance(data, (float, np.float32, np.float64)):
        if abs(data) < 1e-6:
            return "0"
        else:
            return "%.5g" % data
    elif isinstance(data, (int, np.int32, np.uint32, np.int64, np.uint64)):
        return str(data)
    elif isinstance(data, str):
        return "\"%s\"" % data
    elif isinstance(data, bytes):
        return "\"%s\"" % str(data, 'utf8')
    elif isinstance(data, (list, tuple, np.ndarray)):
        if leafList(data):
            string = "["
            string += ",".join([encodeJsonData3(elt) for elt in data])
            return string + "]"
        else:
            string = "["
            string += ",".join(
                ["\n    " + pad + encodeJsonData3(elt, pad+"    ")
                 for elt in data])
            if string == "[":
                return "[]"
            else:
                return string + "\n%s]" % pad
    elif isinstance(data, dict):
        string = "{"
        string += ",".join(
            ["\n    %s\"%s\" : " % (pad, key) + encodeJsonData3(value, pad+"    ")
             for key,value in data.items()])
        if string == "{":
            return "{}"
        else:
            return string + "\n%s}" % pad
    else:
        log.debug(data)
        raise RuntimeError("Can't encode: %s %s" % (data, data.type))

def encodeJsonData2(data, pad=""):
    if data is None:
        return "null"
    elif isinstance(data, (bool, np.bool_)):
        if data:
            return "true"
        else:
            return "false"
    elif isinstance(data, (float, np.float32, np.float64)):
        if abs(data) < 1e-6:
            return "0"
        else:
            return "%.5g" % data
    elif isinstance(data, (int, np.int32, np.uint32)):
        return str(data)
    elif isinstance(data, (str, unicode)):
        return "\"%s\"" % data
    elif isinstance(data, (list, tuple, np.ndarray)):
        if leafList(data):
            string = "["
            string += ",".join([encodeJsonData2(elt) for elt in data])
            return string + "]"
        else:
            string = "["
            string += ",".join(
                ["\n    " + pad + encodeJsonData2(elt, pad+"    ")
                 for elt in data])
            if string == "[":
                return "[]"
            else:
                return string + "\n%s]" % pad
    elif isinstance(data, dict):
        string = "{"
        string += ",".join(
            ["\n    %s\"%s\" : " % (pad, key) + encodeJsonData2(value, pad+"    ")
             for key,value in data.items()])
        if string == "{":
            return "{}"
        else:
            return string + "\n%s}" % pad
    else:
        log.debug(data)
        raise RuntimeError("Can't encode: %s %s" % (data, data.type))


def leafList(data):
    for elt in data:
        if isinstance(elt, (list,tuple,dict)):
            return False
    return True
