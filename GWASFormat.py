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
from re import A
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
        @Author: xutingfeng@big.ac.cn

        GWAS SSF: https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1
        GWAS Standard

        Version: 1.0
        
        Example Code:

        1. specific column index and format all 
            cat /pmaster/chenxingyu/chenxy/project/10algorithm/GWAS_summary_statistic/Asthma/v7new_version_file_uniq | ./GWASFormat.py -i 1 3 5 4 7 8 6 9
        2. specific beta is hazard ratio and pval is log10p; --pval_type log10p/pval --effect_type hazard_ratio/beta/odds_ratio
            cat /pmaster/chenxingyu/chenxy/project/10algorithm/GWAS_summary_statistic/Asthma/v7new_version_file_uniq | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --pval_type log10p --effect_type odds_ratio
        3. spcific other columns
         cat /pmaster/chenxingyu/chenxy/project/10algorithm/GWAS_summary_statistic/Asthma/v7new_version_file_uniq | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --other_col -2 -4

        """
        ),
    )
    parser.add_argument(
        "-i",
        "--col",
        dest="col_indices",
        default=[],
        type=int,
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
        "--pval_type",
        dest="pval_type",
        default="pval",
        choices=["pval", "log10p"],
        help="column 8 in output File type, default: pval, should be one of pval, log10p",
    )
    parser.add_argument(
        "--effect_type",
        dest="effect_type",
        default="beta",
        choices=["beta", "odds_ratio", "hazard_ratio"],
        help="column 5 in output File type, default: beta, should be one of beta, odds_ratio, hazard_ratio",
    )
    parser.add_argument(
        "--ci_upper",
        dest="ci_upper",
        type=int,
        help="Upper bound of confidence interval. Number of col index, optioanl",
        required=False,
    )
    parser.add_argument(
        "--ci_lower",
        dest="ci_lower",
        type=int,
        help="Lower bound of confidence interval. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--rsid",
        dest="rsid",
        type=int,
        help="rsid. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--variant_id",
        dest="variant_id",
        type=int,
        help="variant_id. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--info",
        dest="info",
        type=int,
        help="Imputation information metric. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--ref_allele",
        dest="ref_allele",
        type=int,
        help="ref_allele. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "-n",
        dest="n",
        type=int,
        help="Number of samples. Number of col index, optional",
        required=False,
    )
    parser.add_argument(
        "--other_col",
        dest="other_col",
        type=int,
        default=[],
        nargs="+",
        help="Other columns. Number of col index, optional",
        required=False,
    )
    return parser


def formatChr(x, nochr=False):
    x = x.lower()
    if x.startswith("chr"):
        x = x.lstrip("chr")
    if x == "x":
        x = "23"
    elif x == "y":
        x = "24"
    elif x == "mt":
        x = "25"
    else:
        raise ValueError(f"Unknown chromosome: {x}")
    return x




def header_mapper(idx_or_str, header_col):
    if isinstance(idx_or_str, str):
        string = idx_or_str
        idx = header_col.index(string) + 1
    elif isinstance(idx_or_str, int):
        idx = idx_or_str
        if idx < 0:
            idx = len(header_col) + idx + 1
    else:
        idx = None
    return idx


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
        if key_idx != 0:
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
        if key_idx != 0:
            Mandatory_fields[key] = key_idx

    column_mapping = {}
    column_mapping.update(Mandatory_fields)
    column_mapping.update(Encouraged_fields)

    line_idx = 1
    for line in sys.stdin:
        ss = line.split(delimter)

        if line_idx == 1:
            # get user specified column index
            raw_header = ss
            # map column_mapping keys to index
            column_mapping = {
                key: header_mapper(key_idx, raw_header)
                for key, key_idx in column_mapping.items()
            }

            if args.other_col:
                other_col_indices = [
                    header_mapper(i, raw_header) for i in args.other_col
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
            formated_ss = [
                ss[key_idx - 1] if key_idx is not None else "#NA"
                for key, key_idx in column_mapping.items()
            ]

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

# zcat xxx.tsv | format.py -i 1 2 3 4 5 6 7 --beta haz --pval_type log10p --variant_id 9 --other_col 21 22 "test"  | match_rsid.py -col 4 -c rsid | ref_match.py -col 4 -r GRCh37.fasta.gz | bgzip > xxx.formated.tsv.gz

# Example Code:
#     zcat xxx.tsv | format.py -i 1 2 3 4 5 6 7 --beta haz --pval_type log10p --variant_id 9 --other_col 21 22 "test"  | match_rsid.py -col 4 -c rsid | ref_match.py -col 4 -r GRCh37.fasta.gz | bgzip > xxx.formated.tsv.gz
