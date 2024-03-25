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
            4. if the format is by GWASFormat then `resetID2.py -i variant_id 1 2 4 3` is ok 
            

            For Plink Users:
            1. cat g1000_eur_GRCh38.pvar | resetID2.py -i 1 2 4 5 --add-col new_id | tail -n +2 |awk '{print $3, $6}' > id.map
            2. plink2 --pfile g1000_eur_GRCh38 --update-name  id.map --make-just-pvar --out g1000_eur_GRCh38  
            """
        ),
    )

    parser.add_argument(
        "-i",
        "--col_order",
        dest="col_order",
        default=[],
        nargs="+",
        help="Specify the order of columns for ID, chr, pos, ref, alt. Default: ID col=2, chr col=1, pos col=4, ref col=5, alt col=6. Column index starts from 1. If the format is already in this order, you can directly use `-i 3` for further operations. You can specify index or column name here.",
    )
    parser.add_argument(
        "-k",
        "--keep",
        dest="keep",
        required=False,
        action="store_true",
        help="Include the original rsID in the output.",
    )
    parser.add_argument("--drop-suffix", dest="drop_suffix", action="store_true", help = " drop the suffix of columns name, sorted_alleles => None, only work when -s is used")
    parser.add_argument(
        "-s",
        "--sort",
        dest="sort",
        required=False,
        action="store_true",
        help="Sort the ref and alt alleles using `sorted([ref, alt])`.",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        dest="delimiter",
        default=None,
        help="Delimiter for input file. Default: any whitespace.",
    )

    parser.add_argument(
        "--add-chr",
        dest="add_chr",
        action="store_true",
        help="Add 'chr' prefix to the chr column of the ID.",
    )
    parser.add_argument(
        "-I",
        "--id-delimiter",
        dest="id_delimiter",
        default=":",
        help="Delimiter for the ID. Default: ':'. This controls the delimiter for the output ID. If `-i` has only one parameter and 'chr' or sorting operations are applied, this delimiter will be used to split the oldID into chr, pos, ref, alt.",
    )
    parser.add_argument('--no-header', dest='no_header', action='store_true', help='Input file has no header.')
    parser.add_argument('--add-col', dest='add_col',required=False, default=None, help='Add new column for the new ID with --add-col new_ID_name.')

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
        elif x == "mt" or "m":
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
    ss,
    orderList,
    ID_delimter=":",
    header=None,
    delimter=None,
    need_sort=False,
    needChr=False,
    includeOld=False,
    add_col=False,
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

    if len(orderList) == 1:  # only for add chr or sort or do nothing~
        idCol = header_mapper(orderList[0], header) if header else int(orderList[0])
        oldID = ss[idCol - 1]
        chr, pos, A0, A1 = oldID.split(ID_delimter)
        pass
    elif len(orderList) == 5:
        # idCol, chrCol, posCol, refCol, altCol = [
        #     header_mapper(x, header) for x in orderList
        # ]
        idCol, chrCol, posCol, refCol, altCol = orderList
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
        newID = newID + ID_delimter + oldID if oldID is not None else newID

    if add_col:
        ss.append(newID)
    else: 
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
    id_delimter = args.id_delimiter
    delimter = args.delimiter
    drop_suffix = args.drop_suffix
    addChr = args.add_chr
    new_col_name = args.add_col
    add_col = True if new_col_name else False
    # check header and comments

    line_idx = 2 if args.no_header else 1 # 2 will drop to find header 
    header = None

    if args.no_header:
        try:
            orderList = [int(x) for x in orderList]
        except:
            raise ValueError("if no header, the orderList should be int not str")

    if add_col:
        if len(orderList) == 4:

            orderList = [ '-1 '] + orderList
        else:
            raise ValueError("if add_col is True, the orderList should be 4 not 5")
        

    for line in sys.stdin:

        current_line = line.strip().split(delimter) if delimter is not None else line.strip().split()
        if args.no_header and line_idx == 2: 
            end = len(current_line) + 1 

            if add_col:
                end += 1

            header = list(range(1, end)) # fake header 
            orderList = [int(x) for x in orderList]


        if line_idx == 1:
            header = current_line
 
            if add_col:
                header.append(new_col_name)

            # parse order list with col_idx or col_name
            orderList = [header_mapper(x, header) for x in orderList]

            if is_sort:
                idCol = orderList[0]

                if not drop_suffix:
                    header[idCol - 1] = header[idCol - 1] + "_sorted_alleles"
                    
            #     ss = (
            #         delimter.join(header) if delimter is not None else "\t".join(header)
            #     )

            # else:
            #     ss = header
            ss = delimter.join(header) if delimter is not None else "\t".join(header)

        else:
            if add_col:
                current_line.append("")

            ss = resetID2(
                ss=current_line,
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
