#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:Reset Variants ID by chr:pos:ref:alt
@Date     :2023/08/15 19:05:42
@Author      :Tingfeng Xu
@version      :2.0
"""
import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal

# need to change a lot !


warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog Set/Replace ID for any file. setID as : chr:pos:ref:alt
        @Author: wavefancy@gmail.com (raw code comes from) and xutingfeng@big.ac.cn (modified for this version)

        Version: 2.0
        本脚本会在原始ID列生成新的ID。新的ID格式为：chr:pos:ref:alt

        默认有header；如果存在comment，`--comment '#'`，则会忽略所有以#开头的行；
        -s 会对ref和alt进行排序，sorted([ref,alt])，默认不排序；
        -k 会保留原始ID，即在新的ID后面添加原始ID，用-I/--id-delimter分割（默认:）；
        -d 指定输入文件的分隔符，默认为任意空格；
        -I 指定ID的分隔符，默认为:
        --add-chr 会在ID的chr列添加chr前缀，即chr1,chr2,chrX,chrY,chrMT，默认则是自动去掉chr，只有加上这个参数才会保持或者加上chr。
        Example
            1. cat test.txt | resetID2.py -i variant_id 1 2 3 4 既可对variant_id列进行重命名，命名规则为：1:2:3:4 => chr:pos:ref:alt
            2. cat test.txt | resetID2.py -i variant_id 1 2 3 4 -s --add-chr 既可对variant_id列进行重命名，命名规则为：1:2:3:4 => chr:pos:ref:alt，且会对ref和alt进行排序，sorted([ref,alt])，并且会在chr列添加chr前缀，即chr1,chr2,chrX,chrY,chrMT
        """
        ),
    )

    parser.add_argument(
        "-i",
        "--col_oreder",
        dest="col_order",
        default=[],
        nargs="+",
        help="default is -i 2 1 4 5 6 => ID col is 2, chr col is 1, pos col is 4, ref col is 5, alt col is 6. Note col index start from 1.如果已经是这个格式了则可以直接 -i 3， 然后进行下面的操作",
        # type=str,
    )
    parser.add_argument(
        "-k",
        "--keep",
        dest="keep",
        required=False,
        action="store_true",
        help="Include old rsID.",
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sort",
        required=False,
        action="store_true",
        help="ort the ref and alt alleles, sorted([ref,alt])",
    )
    parser.add_argument(
        "-d",
        "--delimter",
        dest="delimter",
        default=None,
        help="delimter for input file, default is 'any white sapce'.",
    )

    parser.add_argument(
        "--add-chr",
        dest="addChr",
        action="store_true",
        help="add chr for chr col of ID",
    )
    parser.add_argument(
        "-I",
        "--id-delimter",
        dest="id_delimter",
        default=":",
        help="delimter for ID, default is ':'，这个会控制输出的ID的分隔符，如果传入-i 只有一个参数的时候来进行添加chr或者sort的操作时，这个则会用于分割oldID来得到chr pos ref alt",
    )

    return parser


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
        else:
            raise ValueError(f"Unknown chromosome: {x}")
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


# def resetID_by_pattern(line, reset_pattern, delimter=None, need_sort=False, needChr=False):


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


def resetID2(
    line,
    orderList,
    ID_delimter=":",
    header=None,
    delimter=None,
    need_sort=False,
    needChr=False,
    includeOld=False,
):
    """
    Reset the ID format in a line based on the specified order and options.

    Args:
        line (str): The input line containing the values to reset.
        orderList (list): A list specifying the order of columns for ID and additional information.
        ID_delimter (str, optional): Delimiter used to separate components in the old ID. Default is ":".
        header (list, optional): List of header strings. Used for mapping header strings to column indices.
        delimter (str, optional): Delimiter used to split and join values in the input and output lines.
        need_sort (bool, optional): Whether to sort reference and alternate alleles. Default is False.
        needChr (bool, optional): Whether to add "chr" prefix to chromosome identifier. Default is False.
        includeOld (bool, optional): Whether to include the old ID in the new ID. Default is False.

    Returns:
        str: The input line with the ID column reset based on the specified order and options.

    Raises:
        ValueError: If the length of orderList is not 1 or 5.

    Notes:
        - The function supports resetting the ID column from the old ID column and support needChr or sort ref/alt when -i only have one element.

        - If need_sort is True, the reference and alternate alleles are sorted.
        - If needChr is True, the "chr" prefix is added to the chromosome identifier.
        - If includeOld is True, the old ID is included in the new ID.


    """
    ss = line.split(delimter)

    if len(orderList) == 1:  # only for add chr or sort or do nothing~
        idCol = header_mapper(orderList[0], header)
        oldID = ss[idCol - 1]
        chr, pos, A0, A1 = oldID.split(ID_delimter)
        pass
    elif len(orderList) == 5:
        idCol, chrCol, posCol, refCol, altCol = [
            header_mapper(x, header) for x in orderList
        ]

        oldID, chr, pos, A0, A1 = (
            ss[idCol - 1],
            ss[chrCol - 1],
            ss[posCol - 1],
            ss[refCol - 1],
            ss[altCol - 1],
        )

    else:
        raise ValueError(
            "Error: orderList should contain at least one element, which is ID col"
        )

    if need_sort:
        stemp = sorted([A0, A1])
    else:
        stemp = [A0, A1]
    if needChr:
        chr = formatChr(chr, not needChr)
    newID = chr + ID_delimter + pos + ID_delimter + stemp[0] + ID_delimter + stemp[1]
    if includeOld:
        newID = newID + ID_delimter + oldID

    ss[idCol - 1] = newID

    ss = delimter.join(ss) if delimter is not None else "\t".join(ss)
    return ss


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    orderList = args.col_order
    if orderList == []:
        orderList = [3, 1, 2, 4, 5]
    IncludeOld = args.keep
    is_sort = args.sort
    id_delimter = args.id_delimter
    delimter = args.delimter

    addChr = args.addChr
    # check header and comments

    line_idx = 1
    for line in sys.stdin:
        if line_idx == 1:
            header = line.split(delimter)
            ss = line

        else:
            ss = resetID2(
                line=line,
                orderList=orderList,
                header=header,
                ID_delimter=id_delimter,
                includeOld=IncludeOld,
                need_sort=is_sort,
                delimter=delimter,
                needChr=addChr,
            )
        sys.stdout.write(f"{ss}\n")
        line_idx += 1


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
