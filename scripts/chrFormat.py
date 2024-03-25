#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:check chro
@Date     :2023/08/25 19:05:42
@Author      :Tingfeng Xu
@version      :1.0
"""

import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal


warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.


def formatChr(x, nochr=True):
    """
    Format chromosome identifier.

    Args:
        x (str/int): Input chromosome identifier, can be a string or integer.
        nochr (bool): Control whether to remove the "chr" prefix. Default is True, which removes the prefix.

    Returns:
        str: Formatted chromosome identifier.

    Raises:
        ValueError: If the chromosome identifier is unknown or invalid.

    Usage Examples:

    1. Remove "chr" prefix and convert x, y, mt to 23, 24, 25:
       formatChr("chrX")  # Returns "23"
       formatChr("chrY")  # Returns "24"
       formatChr("chrMT") or chrM  # Returns "25"

    2. Add "chr" prefix and convert 23, 24, 25 to x, y, mt:
       formatChr("23", nochr=False)  # Returns "chrX"
       formatChr("24", nochr=False)  # Returns "chrY"
       formatChr("25", nochr=False)  # Returns "chrMT"

    3. Remove "chr" prefix and convert any string or integer to 23, 24, 25:
       formatChr("chr1")  # Returns "1"
       formatChr(23)  # Returns "23"

    Notes:
        - ValueError will be raised if the given chromosome identifier is invalid.
        - When nochr is True, "x", "y", "mt" will be converted to 23, 24, 25.
        - When nochr is False, 23, 24, 25 will be converted to "chrX", "chrY", "chrMT".
    """
    if isinstance(x, int):
        x = str(x)
    if x.startswith("0"):
        x = x.lstrip("0")
    if nochr:
        x = x.lower()
        # remove chr
        if x.startswith("chr"):
            x = x.lstrip("chr")

        # turn x, y, mt => 23, 24, 25
        if x == "x":
            x = "23"
        elif x == "y":
            x = "24"
        elif x == "mt" or x == "m":
            x = "25"

        return x
    else:
        if x not in ["23", "24", "25"]:
            x = "chr" + x
        else:
            if x == "23":
                x = "chrX"
            elif x == "24":
                x = "chrY"
            elif x == "25":
                x = "chrMT"
        return x

def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            %prog Set/Replace ID for any file. setID as : chr:pos:ref:alt
            @Author: wavefancy@gmail.com (raw code comes from) and xutingfeng@big.ac.cn (modified for this version)

            Version: 2.0
            This script generates new IDs based on the original ID column. The new ID format is chr:pos:ref:alt by default.

            """
        ),
    )

    parser.add_argument("-c", "--col", dest="col", type=int, default=1, help="Column index for the ID to be replaced. Default is 1.")
    parser.add_argument("-a", "--add-chr", dest="add_chr", action="store_true", default=False, help="Add 'chr' prefix to the chr column of the ID. Default is False.")
    parser.add_argument("-d", "--delimiter", dest="delimiter", default=None, help="Delimiter for the input file. Default is any whitespace.")

    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    col = args.col
    addChr = args.add_chr
    # check header and comments
    delimiter = args.delimiter if args.delimiter else None
    outDelimiter = "\t" if delimiter is None else delimiter

    line_idx = 1
    for line in sys.stdin:
        line = line.strip()  # remove \n
        if line_idx == 1:
            ss = line 

        else:
            ss = line.split()
            ss[col - 1] = formatChr(ss[col - 1], not addChr)
            ss = outDelimiter.join(ss)
        sys.stdout.write(f"{ss}\n")
        line_idx += 1


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
