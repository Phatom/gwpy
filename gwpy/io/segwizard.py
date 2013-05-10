# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Read SegmentLists from seg-wizard format ASCII files
"""

import re

from astropy.io import registry

from .. import version
from ..segments import (Segment, SegmentList, DataQualityFlag)

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__version__ = version.version

from ..utils import lal

if lal.SWIG_LAL:
    LIGOTimeGPS = lal.swiglal.LIGOTimeGPS
else:
    LIGOTimeGPS = float


def from_segwizard(fileobj, coltype=LIGOTimeGPS, strict=True):
    commentpat = re.compile(r"\s*([#;].*)?\Z", re.DOTALL)
    twocolsegpat = re.compile(r"\A\s*([\d.+-eE]+)\s+([\d.+-eE]+)\s*\Z")
    fourcolsegpat = re.compile(
        r"\A\s*([\d]+)\s+([\d.+-eE]+)\s+([\d.+-eE]+)\s+([\d.+-eE]+)\s*\Z")
    format = None
    out = SegmentList()
    for line in fileobj:
        line = commentpat.split(line)[0]
        if not line:
            continue
        try:
            [tokens] = fourcolsegpat.findall(line)
            num = int(tokens[0])
            seg = Segment(map(coltype, tokens[1:3]))
            duration = coltype(tokens[3])
            this_line_format = 4
        except ValueError:
            try:
                [tokens] = twocolsegpat.findall(line)
                seg = Segment(map(coltype, tokens[0:2]))
                duration = abs(seg)
                this_line_format = 2
            except ValueError:
                break
        if strict:
            if abs(seg) != duration:
                raise ValueError("Segment '%s' has incorrect duration"
                                 % line)
            if format is None:
                format = this_line_format
            elif format != this_line_format:
                raise ValueError("Segment '%s' format mismatch" % line)
        out.append(seg)
    return out


def _flag_from_segwizard(filename, flag=None, coltype=LIGOTimeGPS, strict=True):
    return DataQualityFlag(name=None, active=from_segwizard(filename,
                                                            coltype=coltype,
                                                            strict=strict))

def identify_segwizard(*args, **kwargs):
    filename = args[1][0]
    if isinstance(filename, file):
        filename = filename.name
    if filename.endswith("txt"):
        return True
    else:
        return False

registry.register_reader('txt', DataQualityFlag, _flag_from_segwizard,
                         force=True)
registry.register_identifier('txt', DataQualityFlag, identify_segwizard)
