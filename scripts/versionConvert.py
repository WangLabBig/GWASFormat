#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date     :2024/02/22 11:40:45
@Author      :Tingfeng Xu
@version      :1.1
'''
import argparse

import re
import sys

import textwrap
import warnings
from signal import SIG_DFL, SIGPIPE, signal

DEFAULT_NA = "NA"

warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.

# 检查是否已安装liftover模块
try:
    from liftover import ChainFile, get_lifter
except ImportError:
    import subprocess
    import sys

    print("缺少liftover模块，开始安装...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "liftover"], check=True)
        print("liftover模块安装完成。")
        from liftover import ChainFile, get_lifter

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


def formatChrLiftover(x, nochr=True):
    """
    Format chromosome identifier.

    Args:
        x (str/int): Input chromosome identifier, can be a string or integer.
        nochr (bool): Control whether to remove the "chr" prefix. Default is True, which removes the prefix.

    Returns:
        str: Formatted chromosome identifier.

    Raises:
        ValueError: If the chromosome identifier is unknown or invalid.

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
        if x == "x" or x == "23":
            x = "X"
        elif x == "y" or x == "24":
            x = "Y"
        elif x == "mt" or x == "25":
            x = "MT"

        return x


def is_valid_chromosome(input_str):
    chrPattern = r"^(chr[XYMT0-9]{0,2}|[0-9]{1,2}|[XYMT]{0,2})$"
    return re.match(chrPattern, input_str, re.IGNORECASE) is not None


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog - Genome Position Conversion Tool by Liftover

        Author: Tingfeng Xu (xutingfeng@big.ac.cn)
        Version: 1.0

        ---------------------------------------WARNING---------------------------------------
        Note that coordinates of lifterover are 0-based, so coords converted from 1-based to 0-based will do, as we suppose input file is 1-base (for most of gwas summary file). if you are sure the input file is 0-based, then use --zero-based option.

        This tool allows you to convert genome positions from one build to another using liftover.
        Currently Positon Systems:

        Format\tType\tBase
        UCSC Genome Browser tables\t0-based
        BED\t0-based
        BAM\t0-based
        BCF\t0-based
        narrowPeak\t0-based
        SAF\t0-based
        bedGraph\t0-based
        UCSC Genome Browser web interface\t1-based
        GTF\t1-based
        GFF\t1-based
        SAM\t1-based
        VCF\t1-based
        Wiggle\t1-based
        GenomicRanges\t1-based
        IGV\t1-based
        BLAST\t1-based
        GenBank/EMBL Feature Table\t1-based
        ---------------------------------------WARNING---------------------------------------
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

        For plink2 Users:
        cat g1000_eur.pvar|  versionConvert.py -i 1 2 -c hg19 hg38 -l | awk '{print $3, $6}' > g1000_eur.map
        plink2 --pfile g1000_eur --sort-vars --update-map g1000_eur.map --make-pgen --out g1000_eur_GRCh38
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
    parser.add_argument(
        "--drop",
        dest="drop_unSameChromosome",
        action="store_true",
        help="drop if convert pos is not in the same chromosome. If input file is all in one chromosome, you should use this option.",
    )
    parser.add_argument(
        "-n",
        "--no-suffix",
        dest="no_suffix",
        action="store_true",
        help="Do not add suffix to the column names.",
    )
    parser.add_argument(
        "--no-header",
        dest="no_header",
        action="store_true",
        help="No header and not support for col name in the input",
    )
    parser.add_argument(
        # "-o",
        "--zero-based",
        help="specific this file is zero-based, if file is gwas summary, then do not use this option, otherwise u are sure the file is zero-based",
        action="store_true",
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

    if args.zero_based:
        sys.stderr.write(
            "Warning: zero-based option is on, so the input file should be zero-based, if not, please turn off this option!\n"
        )
        minus_pos = 0
    else:
        sys.stderr.write(
            "Warning: zero-based option is off, so the input file should be one-based (e.g. GWAS Summary Files), if not, please turn on this option!\n"
        )
        minus_pos = 1

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
    elif len(input_cols) >= 3 and not drop:
        raise ValueError(
            "input cols error, please check, if you are converting more than 1 postion col, you should use --drop option to avoid the not same chromosome problem, especially when the chrmosome of converted cols are different."
        )

    line_idx = 2 if args.no_header else 1  # header idx
    if line_idx == 2:
        input_cols = [int(x) for x in input_cols]  # convert str to int
    unmapped = 0
    multiple = 0
    key_error = 0
    notSameChr = 0
    notChr = 0
    notChrList = set()
    for line in sys.stdin:
        line = line.strip()  # remove \n
        line_need_skip = False
        if line_idx == 1:
            header = line.split(delimter)

            input_cols = [
                header_mapper(x, header) for x in input_cols
            ]  # parse order list with col_idx or col_name

            if not no_suffix:  # keep suffix
                newCols = [
                    f"{header[x-1]}_{query}" for x in input_cols[1:]
                ]  # input_cols = [chr, pos1, pos2, ...]
            else:  # drop suffix
                newCols = [f"{header[x-1]}" for x in input_cols[1:]]

            header += ["chain_direction"]  # for chain direction
            if addLast:  # add last fo header
                header += newCols
            else:
                for idx, new_header in zip(input_cols[1:], newCols):
                    header[idx - 1] = new_header

            ss = outputDelimter.join(header)

        else:
            try:
                line = line.split(delimter)
                chr = line[input_cols[0] - 1]
                chr = formatChrLiftover(
                    chr, nochr=True
                )  # liftover only support 1, 2 ... not chr1 ...
                for each in input_cols[1:]:
                    pos = (
                        int(line[each - 1]) - minus_pos
                    )  # convert 1-based to 0-based, if input is  1-based, then minus 1 else minus_pos = 0
                    # if (
                    #     args.zero_based
                    # ):  # if one based input, then minus 1 to convert to 0-based
                    #     pos -= 1

                    try:  # key is ok
                        lifter_res = lifter[chr][pos]

                        if len(lifter_res) == 0:  # unmapped
                            unmapped += 1
                            new_pos = DEFAULT_NA
                            if not keep_unmapped:  # drop if not keep_unmapped
                                line_need_skip = True
                                # continue
                                break
                        elif len(lifter_res) > 1:  # multiple mapped
                            new_pos = DEFAULT_NA
                            multiple += 1
                            if not keep_unmapped:  # drop if not keep_unmapped
                                # continue
                                line_need_skip = True
                                break
                        else:
                            new_chr, new_pos, new_strand = lifter_res[0]
                            new_pos = str(new_pos)  # int => str
                            new_chr = formatChrLiftover(
                                new_chr, nochr=True
                            )  # remove chr

                            if is_valid_chromosome(
                                str(new_chr)
                            ):  # not contig or something else
                                if new_chr != chr:  # not same chromosome
                                    notSameChr += 1

                                    if drop:  # drop if not same chromosome
                                        line_need_skip = True
                                        break
                                    else:  # update new chromosome
                                        line[input_cols[0] - 1] = new_chr
                            else:  # new chr is a contig or something else which is non default chromosome; will skip
                                notChr += 1
                                notChrList.add(new_chr)
                                line_need_skip = True
                                break

                    except KeyError:  # key error if not in lifter chain file
                        key_error += 1
                        new_pos = DEFAULT_NA
                        if not keep_unmapped:  # drop if not keep_unmapped
                            # continue
                            line_need_skip = True
                            break
                    # upadte pos
                    # if one-based input, then convert output 0-based to 1-based
                    # if args.one_based and new_pos != DEFAULT_NA:
                    #     new_pos = int(new_pos) + 1
                    new_pos = (
                        int(new_pos) + minus_pos
                    )  # convert 0-based to 1-based by adding 1 if input is 1-based, else add 0 if input is 0-based
                    # update pos into original cols
                    ## add chain direction

                    line.append(new_strand)
                    if not addLast:  # update pos in original cols if not add last
                        line[each - 1] = new_pos
                    else:
                        line.append(new_pos)

                ss = outputDelimter.join(
                    [str(i) if not isinstance(i, str) else i for i in line]
                )
            except:
                sys.stderr.write(
                    f"Error with line: {line}\n while the output of liftover is {lifter_res}"
                )
                raise

        line_idx += 1
        if line_need_skip and not keep_unmapped:
            continue
        else:
            sys.stdout.write(f"{ss}\n")

if not drop:
    sys.stderr.write(
        f"Warning drop is False, so if converted pos is not the same chr, the data will update, so if your data containes only one chromosome, make sure to filter it later!\n"
    )
if args.no_header:
    sys.stderr.write(
        f"Warning no_header is True, so the input file should not contain header, and the input_cols should be the col index, not col name!\n"
    )
sys.stderr.write(f"unmapped count: {unmapped}\n")
sys.stderr.write(f"multiple count: {multiple}\n")
sys.stderr.write(f"notSameChr count: {notSameChr}\n")
sys.stderr.write(f"key_error count: {key_error}\n")
sys.stderr.write(f"notChr count: {notChr}\n")

if len(notChrList) > 0:
    sys.stderr.write(
        "Undefault chromosome list:" + ",".join(list(notChrList)[:5]) + "\n"
    )
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
if key_error >= line_idx / 100:
    sys.stderr.write(
        "Warning: over 1% of the input lines are key error, please check your data of chr is consistent with your target and query genome version\n"
    )
if notChr >= line_idx / 100:
    sys.stderr.write(
        "Warning: over 1% of the input lines are not default chromosome, please check your data of chr is consistent with your target and query genome version\n"
    )

sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
