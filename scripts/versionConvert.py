#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:       :
@Date     :2023/08/17 15:55:55
@Author      :Tingfeng Xu
@version      :1.0
"""
import subprocess
import sys
import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal
import os.path as osp

DEFAULT_NA = "NA"

warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.

# 检查是否已安装liftover模块
try:
    from liftover import ChainFile
    from liftover import get_lifter
except ImportError:
    print("缺少liftover模块，开始安装...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "liftover"], check=True)
        print("liftover模块安装完成。")
    except subprocess.CalledProcessError:
        print("安装liftover模块时出错。请手动安装liftover。")
        sys.exit(1)


def header_mapper(string, header_col):
    """
    Map a header string or index to a column index.

    Args:
        string (str or int): The header string or index to be mapped.
        header_col (list): The list of header strings.

    Returns:
        int or None: The mapped column index, or None if the input is None.

    Notes:
        - If the input string can be converted to an integer, it is treated as an index.
        - If the index is negative, it is treated as counting from the end of the list.
        - If the input is a string, it is treated as a header and its index is returned.
        - If the input is None, None is returned.
    """
    if string is not None:
        try:
            idx = int(string)

            if idx < 0:
                idx = len(header_col) + idx + 1
        except ValueError:
            idx = header_col.index(string) + 1
    else:
        idx = None
    return idx


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
       formatChr("chrMT")  # Returns "25"

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
        elif x == "mt":
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
        %prog - Genome Position Conversion Tool by Liftover

        Author: Tingfeng Xu (xutingfeng@big.ac.cn)
        Version: 1.0

        This tool allows you to convert genome positions from one build to another using liftover.

        By default, input files are assumed to have a header.

        -c target source cache
            target: genome build to convert from e.g. 'hg19'
            source: genome build to convert to e.g. 'hg38'
            cache: path to cache folder, defaults to ~/.liftover, if not exists will auto download
        chain file of liftoOver, you can download from :https://hgdownload.soe.ucsc.edu/downloads.html

        Usage examples:
        --------------
        Convert positions from hg19 to hg38 and download chain file automatically:
        cat yourfile | %prog -c hg19 hg38 -i 1 2 3 4

        Convert positions from hg19 to hg38 using a specific chain dir, this will use local cache file as '{target}To{query}.over.chain.gz':
        cat yourfile %prog -c hg19 hg38 chainFilePath -i 1 2 3 4
        """
        ),
    )
    # "hg19", "hg38"
    parser.add_argument(
        "-c",
        "--chain",
        default=[],
        nargs="+",
        dest="chain",
        help="""
                Specify the genome builds to convert from and to (e.g., 'hg19' to 'hg38').
                Optional 'cache' argument specifies the cache folder (defaults to ~/.liftover).
                Chain files can be downloaded from: https://hgdownload.soe.ucsc.edu/downloads.html        
""",
    )
    parser.add_argument(
        "-i",
        "--input_cols",
        dest="input_cols",
        default=[],
        nargs="+",
        help="""
        Specify the genome positions to be converted. You can provide multiple columns.
                The first column should be the chromosome index, followed by position columns.
                Example: -i 1 2 3 4 (to convert chromosome and positions in columns 2, 3, and 4).""",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--add-last",
        dest="add_last",
        action="store_true",
        help="Add the converted positions as new columns at the end.",
    )
    parser.add_argument(
        "-s",
        "--sep",
        dest="delimter",
        default=None,
        help="Specify the delimiter used in the input file. Default is tab.",
    )
    parser.add_argument(
        "-k",
        "--keep-unmapped",
        dest="keep_unmapped",
        action="store_true",
        help="keep rows with unmapped and multiple positions.",
    )
    parser.add_argument("--drop", dest="drop_unSameChromosome", action="store_true", help="drop if convert pos is not in the same chromosome. If input file is all in one chromosome, you should use this option.")
    parser.add_argument(
        "-n",
        "--no-suffix",
        dest="no_suffix",
        action="store_true",
        help="Do not add suffix to the column names.",
    )

    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    chain = args.chain
    input_cols = args.input_cols
    delimter = args.delimter
    addLast = args.add_last
    keep_unmapped = args.keep_unmapped
    drop = args.drop_unSameChromosome
    outputDelimter = "\t" if delimter is None else delimter
    no_suffix = args.no_suffix

    if len(chain) == 2:
        target, query = chain
        chainPath = None
    elif len(chain) == 3:
        target, query, chainPath = chain
    else:
        raise ValueError(
            "chain args error, please check, would be -c hg19 hg38 or -c hg19 hg38 chainFilePath or other version"
        )

    # lifter = ChainFile(chainPath, target, query)
    lifter = get_lifter(target, query, cache=chainPath)

    if len(input_cols) <= 1:
        raise ValueError("input cols error, please check, at least 1 col")

    # lifter[chrom][pos]
    line_idx = 1
    unmapped = 0
    multiple = 0
    notSameChr = 0

    print(keep_unmapped)
    for line in sys.stdin:
        line = line.strip()  # remove \n
        line_need_skip = False
        if line_idx == 1:
            header = line.split(delimter)

            # parse order list with col_idx or col_name
            input_cols = [header_mapper(x, header) for x in input_cols]

            if not no_suffix:
                newCols = [
                    f"{header[x-1]}_{query}" for x in input_cols[1:]
                ]  # input_cols = [chr, pos1, pos2, ...]
            else:  # no_suffix
                newCols = [f"{header[x-1]}" for x in input_cols[1:]]

            if addLast:
                header += newCols
            else:
                for idx, new_header in zip(input_cols[1:], newCols):
                    header[idx - 1] = new_header

            ss = outputDelimter.join(header)

        else:
            line = line.split(delimter)
            chr = line[input_cols[0] - 1]
            chr = formatChr(
                chr, nochr=True
            )  # liftover only support 1, 2 ... not chr1 ...
            for each in input_cols[1:]:
                pos = int(line[each - 1])
                # TODO: chrX和chrY的处理
                lifter_res = lifter[chr][pos]
                # TODO: warnning message passed to stderr
                if len(lifter_res) == 0:
                    # message = f"Warning: {chr}:{pos} can not convert to {query} version, will return NA"
                    # sys.stderr.write(f"{message}\n")

                    unmapped += 1
                    new_pos = DEFAULT_NA
                    if not keep_unmapped:
                        line_need_skip = True
                        # continue
                        break
                elif len(lifter_res) > 1:
                    # message = f"Warning: {chr}:{pos} convert to {query} version have multiple results, will return NA"
                    # sys.stderr.write(f"{message}\n")

                    new_pos = DEFAULT_NA
                    multiple += 1
                    if not keep_unmapped:
                        # continue
                        line_need_skip = True
                        break
                else:
                    # TODO: new_chr 是否和原始chr一致？ strand信息是否需要输出
                    # Waring: new_chr may not as same as chr
                    new_chr, new_pos, new_strand = lifter_res[0]
                    new_pos = str(new_pos)  # int => str
                    new_chr = formatChr(new_chr, nochr=True)  # remove chr
                    if new_chr != chr:
                        notSameChr += 1
                        if drop:
                            # continue
                            line_need_skip = True
                            break
                        else:
                            # new_pos = DEFAULT_NA
                            # new_pos = new_pos 
                            line[input_cols[0] - 1] = new_chr # new_chr will replace old_chr

                if not addLast:
                    line[each - 1] = new_pos
                else:
                    line.append(new_pos)
            ss = outputDelimter.join(line)

        line_idx += 1
        if line_need_skip and not keep_unmapped:
            continue
        else:
            sys.stdout.write(f"{ss}\n")

if not drop:
    sys.stderr.write(f"Warning drop is False, so if converted pos is not the same chr, the data will update, so if your data containes only one chromosome, make sure to filter it later!")
sys.stderr.write(f"unmapped count: {unmapped}\n")
sys.stderr.write(f"multiple count: {multiple}\n")
sys.stderr.write(f"notSameChr count: {notSameChr}\n")

if unmapped >= line_idx / 100:
    sys.stderr.write(
        "Warning: over 1% of the input lines are unmapped, please check your target and query version\n"
    )
if multiple >= line_idx / 100:
    sys.stderr.write(
        "Warning: over 1% of the input lines are multiple mapped, please check your target and query version\n"
    )
if notSameChr >= line_idx / 100:
    sys.stderr.write(
        "Warning: over 1% of the input lines are not same chromosome, please check your target and query version\n"
    )


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
