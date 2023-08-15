#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date     :2023/08/10 18:55:10
@Author      :Tingfeng Xu
@version      :1.0
'''
import time 
start = time.time()


import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal



warnings.filterwarnings("ignore")
signal(
    SIGPIPE, SIG_DFL
)  # prevent IOError: [Errno 32] Broken pipe. If pipe closed by 'head'.

column_mapping = {
    "chromosome": None,
    "position": None,
    "ref": None,
    "alt": None,
    "pval": None,
    "maf": None,
    "af": None,
    "case_af": None,
    "control_af": None,
    "ac": None,
    "beta": None,
    "sebeta": None,
    "or": None,
    "r2": None,
    "num_samples": None,
    "num_controls": None,
    "num_cases": None
}

def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog Set/Replace ID for any file. setID as : chr:pos:ref:alt
        @Author: xutingfeng@big.ac.cn

        Version: 1.0
        Example:zcat _crp.regenie.gz| pheweb_format.py -i 1 2 4 5 6 --log10P --beta '-5' --sebeta '-4' --af 6 --num_samples 7 | column -t


        Ohter format
            | Column Description                        | Name         | Command Line Argument | Other Allowed Column Names | Allowed Values                                        |
            |-------------------------------------------|--------------|-----------------------|----------------------------|--------------------------------------------------------|
            | Minor Allele Frequency                    | maf          | --maf                 |                            | Number in (0, 0.5]                                    |
            | Allele Frequency (of Alternate Allele)    | af           | --af                  | a1freq, frq                | Number in (0, 1)                                      |
            | AF among Cases                            | case_af      | --case_af             | af.cases                   | Number in (0, 1)                                      |
            | AF among Controls                         | control_af   | --control_af          | af.controls                | Number in (0, 1)                                      |
            | Allele Count                              | ac           | --ac                  |                            | Integer                                              |
            | Effect Size (of Alternate Allele)         | beta         | --beta                |                            | Number                                               |
            | Standard Error of Effect Size             | sebeta       | --sebeta              | se                         | Number                                               |
            | Odds Ratio (of Alternate Allele)          | or           | --or                  |                            | Number                                               |
            | R2                                        | r2           | --r2                  |                            | Number                                               |
            | Number of Samples                         | num_samples  | --num_samples         | ns, n                      | Integer, must be the same for every variant in its phenotype |
            | Number of Controls                        | num_controls | --num_controls        | ns.ctrl, n_controls         | Integer, must be the same for every variant in its phenotype |
            | Number of Cases                           | num_cases    | --num_cases           | ns.case, n_cases            | Integer, must be the same for every variant in its phenotype |
        """
        ),
    )
    parser.add_argument("-i", "--col", dest="col_indices", default=[], type=int, nargs= "+", help="Specify the columns of chrom pos EA OA beta se EA_freq pval v_id rsid ref_allele columns start from 1")


    # parser.add_argument("--log10P", dest="log10P", action="store_true", help="--log10P will think pval is log10P and convert it to pval")
    # parser.add_argument("--maf", dest="maf", type=int, help="Minor Allele Frequency. Number in (0, 0.5].")
    # parser.add_argument("--af", dest="af", type=int, help="Allele Frequency (of Alternate Allele). Number in (0, 1).")
    # parser.add_argument("--case_af", dest="case_af", type=int, help="AF among Cases. Number in (0, 1).")
    # parser.add_argument("--control_af", dest="control_af", type=int, help="AF among Controls. Number in (0, 1).")
    # parser.add_argument("--ac", dest="ac", type=int, help="Allele Count. Integer.")
    # parser.add_argument("--beta", dest="beta", type=int, help="Effect Size (of Alternate Allele). Number.")
    # parser.add_argument("--sebeta", dest="sebeta", type=int, help="Standard Error of Effect Size. Number.")
    # parser.add_argument("--or", dest="or_", type=int, help="Odds Ratio (of Alternate Allele). Number.")  # 'or' is a keyword, so I changed it to 'or_'
    # parser.add_argument("--r2", dest="r2", type=int, help="R2. Number.")
    # parser.add_argument("--num_samples", dest="num_samples", type=int, help="Number of Samples. Integer, must be the same for every variant in its phenotype.")
    # parser.add_argument("--num_controls", dest="num_controls", type=int, help="Number of Controls. Integer, must be the same for every variant in its phenotype.")
    # parser.add_argument("--num_cases", dest="num_cases", type=int, help="Number of Cases. Integer, must be the same for every variant in its phenotype.")

    return parser

def formatChr(x, nochr=False):
    if x.startswith("chr"):
        return x
    elif x.isdigit():
        if int(x) < 23:
            return "chr" + str(int(x))
        else:
            if x == "23":
                return "chrX"
            elif x == "24":
                return "chrY"
            elif x == "25":
                return "chrX"
            elif x == "26":
                return "chrMT"
    else:
        return x


# def resetID(line, orderList, IncludeOld=False, is_sort=False, delimter=None,addChr=False):
#     """
#     reset ID for any file.
#     setID as : chr:pos:ref:alt
#     return
#     """
#     # output results.
#     ss = line.split(delimter)
    
#     # orderList should contain at least one element, which is ID col
#     if len(orderList) ==1:
#         idCol = orderList[0]
#         oldID = ss[idCol]
#         chr, pos, A0, A1 = oldID.split(':') # this time A0 and A1 is not sure, and this mode should work for --sort or --add-chr or do nothing 
#     else:
#         idCol, chrCol, posCol, refCol, altCol = orderList

#         oldID, chr, pos, A0, A1 = ss[idCol], ss[chrCol], ss[posCol], ss[refCol], ss[altCol] # this time A0 is REF and A1 is ALT; this work for rename ID 
    
#     if is_sort:
#         stemp = sorted([A0, A1])
#     else:
#         stemp = [A0, A1]

#     # if addChr:
#     chr = formatChr(chr, not addChr) # addChr is True, then nochr is False, so formatChr will add chr for chr col of ID

#     newID = chr + ':' + pos + ':' + stemp[0] + ':' + stemp[1]
#     if IncludeOld:  # 是否包含oldID
#         newID = newID + ':' + oldID  
#     # 更新到ss中
#     ss[idCol] = newID

#     if delimter is None:
#         outputDelimter = "\t"
#     else:
#         outputDelimter = delimter
#     return outputDelimter.join(ss)
#     # sys.stdout.write('%s\n'%('\t'.join([ss[x] for x in idIndex])))

def turn1to0(x):
    if x >=0: # 1=>0 2=>1 
        return x-1
    else: # -5 => -5 不变
        return x

if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    column_mapping = {
        "chromosome": None,
        "base_pair_location": None,
        "effect_allele": None,
        "other_allele": None,
        "beta": None,
        "standard_error": None,
        "effect_allele_frequency": None,
        "p_value": None,
        "variant_id": None,
        "rsid": None,
        "ref_allele": None,
        # "sebeta": None,
        # "or": None,
        # "r2": None,
        # "num_samples": None,
        # "num_controls": None,
        # "num_cases": None
    }

    chr, pos, ea, oa, beta, se, ea_freq, pval, v_id, rsid, ref_allele = [i for i in args.col_indices]

    for key, key_idx in zip(column_mapping.keys(), args.col_indices):
        if key_idx !=0:
            column_mapping[key] = key_idx
            
    delimter = None 

    line_idx = 1
    for line in sys.stdin:
        ss = line.split(delimter) 

        if line_idx ==1:
            formated_ss = [key for key, key_idx in column_mapping.items()]
        else:
            formated_ss = [ss[key_idx -1 ] if key_idx !=0 else "#NA"  for key, key_idx in column_mapping.items()]

        formated_ss = "\t".join(formated_ss) # \t delimter
        
        sys.stdout.write(f"{formated_ss}\n")
        line_idx += 1


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()

end = time.time()
time_str = "time elapsed: {:.2f} /min".format((end - start) / 60)

with open("time.log", "w") as f:
    f.write(time_str)