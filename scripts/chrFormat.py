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
        elif x == "mt" or "m"::
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

            By default, input files are assumed to have headers.
            -s sorts the ref and alt alleles using `sorted([ref, alt])`, by default no sorting is applied.
            -k retains the original ID and appends it after the new ID using `-I/--id-delimter` as a separator (default: ':').
            -d specifies the delimiter for the input file (default: any whitespace).
            -I specifies the ID delimiter (default: ':').
            --add-chr adds 'chr' prefix to the chr column of the ID, preserving or adding 'chr' to IDs.

            **Example:**

            1. Rename the 'variant_id' column: `cat test.txt | resetID2.py -i variant_id 1 2 3 4`
               This renames the 'variant_id' column to the format: 1:2:3:4 => chr:pos:ref:alt.

            2. Rename and format the 'variant_id' column with sorting and 'chr' prefix:
               `cat test.txt | resetID2.py -i variant_id 1 2 3 4 -s --add-chr`
               This renames the 'variant_id' column and formats it as chr:pos:ref:alt, 
               sorts ref and alt alleles, and adds 'chr' prefix to chr column.
            3. Rename, format and use '_' as id_delimiter with sorting and 'chr' prefix:
               `cat test.txt | resetID2.py -i variant_id 1 2 3 4 -I _ -s --add-chr`
               This renames the 'variant_id' column and formats it as chr:pos:ref:alt, 
               sorts ref and alt alleles, and adds 'chr' prefix to chr column.
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

