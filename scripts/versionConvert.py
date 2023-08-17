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
        "-d",
        "--drop_unmapped",
        dest="drop_unmapped",
        action="store_true",
        help="Drop rows with unmapped positions.",
    )

    return parser


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    chain = args.chain
    input_cols = args.input_cols
    delimter = args.delimter
    addLast = args.add_last
    drop_unmapped = args.drop_unmapped
    outputDelimter = "\t" if delimter is None else delimter

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
    for line in sys.stdin:
        line = line.strip()  # remove \n
        if line_idx == 1:
            header = line.split(delimter)

            # parse order list with col_idx or col_name
            input_cols = [header_mapper(x, header) for x in input_cols]
            if addLast:
                newCols = [
                    f"{header[x-1]}_{query}" for x in input_cols[1:]
                ]  # input_cols = [chr, pos1, pos2, ...]
                # ss = line + outputDelimter + outputDelimter.join(newCols)
                # print(line + outputDelimter + outputDelimter.join(newCols))
                header += newCols
                ss = outputDelimter.join(header)
            else:
                ss = line  # keep same header

        else:
            line = line.split(delimter)
            chr = line[input_cols[0] - 1]
            for each in input_cols[1:]:
                pos = int(line[each - 1])

                lifter_res = lifter[chr][pos]
                # TODO: warnning message passed to stderr
                if len(lifter_res) == 0:
                    message = f"Warning: {chr}:{pos} can not convert to {query} version, will return NA"
                    # sys.stderr.write(f"{message}\n")
                    unmapped += 1
                    new_pos = "NA"
                    if drop_unmapped:
                        continue
                elif len(lifter_res) > 1:
                    # message = f"Warning: {chr}:{pos} convert to {query} version have multiple results, will return NA"
                    sys.stderr.write(f"{message}\n")
                    new_pos = "NA"
                    multiple += 1
                    if drop_unmapped:
                        continue
                else:
                    # TODO: new_chr 是否和原始chr一致？ strand信息是否需要输出
                    new_chr, new_pos, new_strand = lifter_res[0]
                    new_pos = str(new_pos)  # int => str
                if not addLast:
                    line[each - 1] = new_pos
                else:
                    line.append(new_pos)
            ss = outputDelimter.join(line)
        sys.stdout.write(f"{ss}\n")
        line_idx += 1

sys.stderr.write(f"unmapped count: {unmapped}\n")
sys.stderr.write(f"multiple count: {multiple}\n")
if unmapped + multiple >= line_idx // 2:
    sys.stderr.write(
        "Warning: over half of the input lines are unmapped or multiple mapped, please check your target and query version\n"
    )


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
