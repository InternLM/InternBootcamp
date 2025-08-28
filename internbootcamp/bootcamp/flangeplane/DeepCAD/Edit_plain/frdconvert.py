import argparse
import itertools as itt
import logging
import os
import pickle
import sys


# These data are node-related.
# The first item, NODES is special. It contains the original positions of the
# nodes.
'''
NODES：节点编号。
CP3DF：三维节点的位移分量。
CT3D-MIS：三维单元的主应力。
CURR：当前时间步。
DEPTH：深度。
DISP：位移。
DTIMF：时间步长。
ELPOT：元素的潜在能量。
EMFB：元素的磁场强度。
EMFE：元素的电场强度。
ENER：能量。
ERROR：误差。
FLUX：通量。
FORC：力。
HCRIT：临界高度。
M3DF：三维主应力。
MAFLOW：质量流量。
MDISP：主位移。
MESTRAIN：主应变。
MSTRAIN：应变。
MSTRESS：应力。
NDTEMP：节点温度。
PDISP：位移的主分量。
PE：元素的应变能。
PFORC：力的主分量。
PNDTEMP：节点温度的主分量。
PS3DF：三维主应力的主分量。
PSTRESS：应力的主分量。
PT3DF：三维主应力的主分量。
RFL：反射系数。
SDV：状态变量。
SEN：灵敏度。
STPRES：压力。
STRESS：应力。
STRMID：中间应力。
STRNEG：负应力。
STRPOS：正应力。
STTEMP：温度。
THSTRAIN：热应变。
TOPRES：压力。
TOSTRAIN：应变。
TOTEMP：温度。
TS3DF：三维主应力。
TT3DF：三维主应力的主分量。
TURB3DF：三维湍流应力。
V3DF：三维速度分量。
VELO：速度。
VSTRES：速度应力。
ZZSTR：Z方向的应力。
'''
NODE_RELATED = (
    "NODES",
    "CP3DF",
    "CT3D-MIS",
    "CURR",
    "DEPTH",
    "DISP",
    "DTIMF",
    "ELPOT",
    "EMFB",
    "EMFE",
    "ENER",
    "ERROR",
    "FLUX",
    "FORC",
    "HCRIT",
    "M3DF",
    "MAFLOW",
    "MDISP",
    "MESTRAIN",
    "MSTRAIN",
    "MSTRESS",
    "NDTEMP",
    "PDISP",
    "PE",
    "PFORC",
    "PNDTEMP",
    "PS3DF",
    "PSTRESS",
    "PT3DF",
    "RFL",
    "SDV",
    "SEN",
    "STPRES",
    "STRESS",
    "STRMID",
    "STRNEG",
    "STRPOS",
    "STTEMP",
    "THSTRAIN",
    "TOPRES",
    "TOSTRAIN",
    "TOTEMP",
    "TS3DF",
    "TT3DF",
    "TURB3DF",
    "V3DF",
    "VELO",
    "VSTRES",
    "ZZSTR",
)


def _process_float_data(lines, first, last):
    """Convert node-related float data to a dictionary indexed by the node number."""
    data = {}
    while not lines[first].startswith("-1"):
        first += 1
    count = int(len(lines[first]) / 12)
    indices = [(c * 12, (c + 1) * 12) for c in range(1, count)]
    for ln in itt.islice(lines, first, last):
        num = int(ln[2:12])
        numbers = [float(ln[a:b]) for a, b in indices]
        data[num] = tuple(numbers)
    return data


def _find_ranges(lines):
    """Find the start and end lines of the different data sets."""
    starts, ends = {}, {}
    for num, ln in enumerate(lines):
        # Node data is preceded by a “2C”-line.
        if ln.startswith("2C"):
            starts["NODES"] = num + 1
        # Element data is preceded by a “3C”-line
        if ln.startswith("3C"):
            starts["ELEMENTS"] = num + 1
        # All other data is preceded by a “-4” line.
        elif ln.startswith("-4"):
            items = ln.split()
            starts[items[1]] = num + 1
        # Data ends with a “-3”-line.
        elif ln.startswith("-3"):
            #ends[next(reversed(starts.keys()))] = num 
            ends[list(starts.keys())[-1]] = num

    ranges = {name: (starts[name], ends[name]) for name in starts.keys()}
    del starts, ends
    return ranges


def read_frd(path):
    """
    Read and return the data in an frd file as a dictionary of dictionaries.

    The return value is a dictionary with the keys being the names of the
    data sets present in the FRD-file.
    The values in the underlying dictionaries are tuples of ``float``.
    The keys are the number of the node that the tuple belong to.
    Note that node numbers do not have to start at 1!
    """
    with open(path) as file:
        lines = [ln.strip() for ln in file]
    ranges = _find_ranges(lines)
    contents = {}
    for name in ranges.keys():
        if name not in NODE_RELATED:
            print("pass {}".format(name))
            continue  # skip
        first, last = ranges[name]
        contents[name] = _process_float_data(lines, first, last)
        logging.info(f"extracted {len(contents[name])} “{name}”")
    return contents
