#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:       :
@Date     :2023/08/15 10:33:39
@Author      :Tingfeng Xu
@version      :1.0
"""
# import time
# start = time.time()


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
        %prog GWAS format standardization tool
        @Author: xutingfeng@big.ac.cn

        GWAS SSF: https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1
        GWAS Standard

        Version: 1.0
        
        -i 指定列索引，从1开始，如果要跳过某列，直接设置为0即可;支持的模式如下：
        1. 指定列索引，从1开始，支持-1对应倒数第一列
        2. 指定列名
        3. 0，表示这列设为#NA，即缺失信息
        columns of chrom pos effect_allele(EA) other_allele(OA) beta se EA_freq pval columns start from 1
        Example Code:

        1. specific column index and format all 
            cat xxx.tsv.gz | GWASFormat.py -i "CHR" 0 A1 A2 A1_FREQ -6 -5 9 
        2. specific beta is hazard ratio and pval is log10p; --pval_type log10p/pval --effect_type hazard_ratio/beta/odds_ratio
            cat /pmaster/chenxingyu/chenxy/project/10algorithm/GWAS_summary_statistic/Asthma/v7new_version_file_uniq | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --pval_type log10p --effect_type odds_ratio
        3. spcific other columns
         cat /pmaster/chenxingyu/chenxy/project/10algorithm/GWAS_summary_statistic/Asthma/v7new_version_file_uniq | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --other_cols -2 -4

        """
        ),
    )
    parser.add_argument(
        "-i",
        "--col",
        dest="col_indices",
        default=[],
        # type=int,
        nargs="+",
        help="Specify the columns of chrom pos effect_allele(EA) other_allele(OA) beta se EA_freq pval columns start from 1. If you want to skip a column, just set it to 0.",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--delimter",
        dest="delimter",
    )
    parser.add_argument(
        "--pval-type",
        dest="pval_type",
        default="pval",
        choices=["pval", "log10p"],
        help="column 8 in output File type, default: pval, should be one of pval, log10p",
    )
    parser.add_argument(
        "--effect-type",
        dest="effect_type",
        default="beta",
        choices=["beta", "odds_ratio", "hazard_ratio"],
        help="column 5 in output File type, default: beta, should be one of beta, odds_ratio, hazard_ratio",
    )
    parser.add_argument(
        "--ci-upper",
        dest="ci_upper",
        # type=int,
        help="Upper bound of confidence interval. Number of col index, optioanl",
        required=False,
    )
    parser.add_argument(
        "--ci-lower",
        dest="ci_lower",
        # type=int,
        help="Lower bound of confidence interval. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--rsid",
        dest="rsid",
        # type=int,
        help="rsid. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--variant-id",
        dest="variant_id",
        # type=int,
        help="variant_id. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--info",
        dest="info",
        # type=int,
        help="Imputation information metric. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--ref-allele",
        dest="ref_allele",
        # type=int,
        help="ref_allele. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "-n",
        dest="n",
        # type=int,
        help="Number of samples. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--other-cols",
        dest="other_cols",
        # type=int,
        default=[],
        nargs="+",
        help="Other columns. Number of col index, optional",
        required=False,
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


# def header_mapper(idx_or_str, header_col):
#     if isinstance(idx_or_str, str):
#         string = idx_or_str
#         idx = header_col.index(string) + 1
#     elif isinstance(idx_or_str, int):
#         idx = idx_or_str
#         if idx < 0:
#             idx = len(header_col) + idx + 1
#     else:
#         idx = None
#     return idx


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    # see gwas-ssf_v1.0.0.pdf: https://github.com/EBISPOT/gwas-summary-statistics-standard

    # parse args
    pval_type = args.pval_type
    if pval_type == "log10p":
        pval_type = "minus_log10_p_value"
    elif pval_type == "pval":
        pval_type = "p_value"
    effect_type = args.effect_type
    delimter = args.delimter

    # get fields
    Mandatory_fields = {
        "chromosome": None,
        "base_pair_location": None,
        "effect_allele": None,
        "other_allele": None,
        effect_type: None,
        "standard_error": None,
        "effect_allele_frequency": None,
        pval_type: None,
        # "variant_id": None,
        # "rsid": None,
        # "ref_allele": None,
    }
    Encouraged_fields = {
        "ci_upper": None,
        "ci_lower": None,
        "rsid": None,
        "variant_id": None,
        "info": None,
        "ref_allele": None,
        "n": None,
    }

    default_col_indices = args.col_indices

    if len(default_col_indices) != 8:
        raise ValueError(
            "col_indices should containing 8 value, this means that you should specific these cols index: chromosome, base_pair_location, effect_allele, other_allele, beta/odds_ration/hazard_ratio, standard_error, effect_allele_frequency, p_value/minus_log10_p_value"
        )

    chr, pos, ea, oa, beta, se, ea_freq, pval = [i for i in default_col_indices]

    for key, key_idx in zip(Mandatory_fields.keys(), args.col_indices):
        if key_idx != "0":
            Mandatory_fields[key] = key_idx
    # for optional parameters
    for key, key_idx in zip(
        Encouraged_fields.keys(),
        [
            args.ci_upper,
            args.ci_lower,
            args.rsid,
            args.variant_id,
            args.info,
            args.ref_allele,
            args.n,
        ],
    ):
        if key_idx != "0" and key_idx is not None:
            Encouraged_fields[key] = key_idx

    column_mapping = {}
    column_mapping.update(Mandatory_fields)
    column_mapping.update(Encouraged_fields)

    line_idx = 1
    for line in sys.stdin:
        line = line.strip()  # remove \n
        ss = line.split(delimter)

        if line_idx == 1:
            # get user specified column index
            raw_header = ss
            # map column_mapping keys to index
            column_mapping = {
                key: header_mapper(key_idx, raw_header)
                for key, key_idx in column_mapping.items()
            }

            if args.other_cols:
                other_col_indices = [
                    header_mapper(i, raw_header) for i in args.other_cols
                ]
                user_defined_dict = {
                    ss[key_idx - 1]: key_idx for key_idx in other_col_indices
                }
                if (
                    len(
                        conflict := set(user_defined_dict.keys()).intersection(
                            set(column_mapping.keys())
                        )
                    )
                    > 0
                ):  # avoid conflict columns between user defined and default
                    conflict_list = ",".join(conflict)
                    raise ValueError(
                        f"User defined column index has conflict with default column index. {conflict_list}"
                    )

                column_mapping.update(user_defined_dict)
            # update header
            formated_ss = [key for key, key_idx in column_mapping.items()]
        else:
            # formated_ss = [
            #     ss[key_idx - 1] if key_idx is not None else "#NA"
            #     for key, key_idx in column_mapping.items()
            # ]
            formated_ss = []
            for key, key_idx in column_mapping.items():
                if key_idx is not None:
                    if key == "chromosome":
                        new_value = formatChr(ss[key_idx - 1])
                    elif key in ["effect_allele", "other_allele"]:
                        new_value = ss[key_idx - 1].upper()
                    else:
                        new_value = ss[key_idx - 1]
                else:
                    new_value = "#NA"

                formated_ss.append(new_value)

        formated_ss = "\t".join(formated_ss)  # \t delimter

        sys.stdout.write(f"{formated_ss}\n")
        line_idx += 1


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()

# end = time.time()
# time_str = "time elapsed: {:.2f} /min".format((end - start) / 60)

# with open("time.log", "w") as f:
#     f.write(time_str)

# zcat xxx.tsv | format.py -i 1 2 3 4 5 6 7 --beta haz --pval_type log10p --variant_id 9 --other_cols 21 22 "test"  | match_rsid.py -col 4 -c rsid | ref_match.py -col 4 -r GRCh37.fasta.gz | bgzip > xxx.formated.tsv.gz

# Example Code:
#     zcat xxx.tsv | format.py -i 1 2 3 4 5 6 7 --beta haz --pval_type log10p --variant_id 9 --other_cols 21 22 "test"  | resetID -i 2 1 3 4 5 --header

#     match_rsid.py -col 4 -c rsid | ref_match.py -col 4 -r GRCh37.fasta.gz | bgzip > xxx.formated.tsv.gz
