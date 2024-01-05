#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: Convert Formated GWAS file to supported format
@Date     :2024/01/05 17:09:52
@Author      :Tingfeng Xu
@version      :1.0
'''





#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:       :
@Date     :2023/08/10 18:55:10
@Author      :Tingfeng Xu
@version      :1.0
"""
import argparse
import sys
import warnings
import textwrap
from signal import SIG_DFL, SIGPIPE, signal
import math


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
    "num_cases": None,
}


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog format for pheweb for any file. 
        @Author: xutingfeng@big.ac.cn

        Version: 1.0
        Example:zcat _crp.regenie.gz| pheweb_format.py -i 1 2 4 5 6 --log10P --beta '-5' --sebeta '-4' --af 6 --num_samples 7 | column -t
        
        If is by GWASFormat, then pheweb_format.py -i 1 2 4 3 8 --af 7

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

    parser.add_argument("-f", "--format", choices=["cojo", "pheweb"])

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



def turn1to0(x):
    if x >= 0:  # 1=>0 2=>1
        return x - 1
    else:  # -5 => -5 不变
        return x

cojo_mapping={
    "variant_id": "SNP",
    "effect_allele":"A1",
    "other_allele":"A2",
    "effect_allele_frequency":"freq",
    "beta":"b",  # GWASFormat 后这里可以是beta, or so if or will log or to beta 
    "standard_error":"se",
    "p_value":"p",
    "n":"n"
}

cojo_mapping={
    "SNP":10,
    "effect_allele":2,
    "other_allele":3,
    "effect_allele_frequency":6,
    "beta":4,
    "standard_error":5,
    "p_value":7,
    "n":14
}
cojo_mapping = {
    "SNP": 10,
    "A1": 2,
    "A2": 3,
    "freq": 6,
    "b": 4,
    "se": 5,
    "p": 7,
    "n": 14,
}


supported_format={"cojo":cojo_mapping}

def check_beta_cols(name):
    """
    beta return 1 
    or return 0 
    other raise error
    """
    if name == "beta":
        return 1
    elif name == "or":
        return 0
    else:
        raise ValueError("beta or or, but now is :",name)
    
def check_pvalue_cols(name):
    """
    log10P => 1 
    P => 0
    """
    if name == "minus_log10_p_value":
        return 1
    elif name == "p_value":
        return 0
    else:
        raise ValueError("minus_log10_p_value or p_value, but now is :",name)

import math 

if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()



    column_mapping = supported_format[args.format]


    line_idx = 1
    for line in sys.stdin:
        ss = line.split()
        format_ss = []
        if line_idx == 1:
            for k, v in column_mapping.items():
                if v ==4:
                    turn_beta_flag = check_beta_cols(ss[4]) # 1 means beta, 0 means or and 0 will log or to beta
                elif v == 7:
                    turn_pvalue_flag = check_pvalue_cols(ss[7]) # 1 means now is -log10p , will turn to p
            format_ss = [k for k in column_mapping.keys()]

        else:
            for k, v in column_mapping.items():
                if v == 4 and turn_beta_flag == 0: # log OR 
                    format_ss.append(str(math.log(float(ss[v]))))
                elif v == 7 and turn_pvalue_flag == 1:
                    format_ss.append(str(math.pow(10, -float(ss[v]))))
                else:
                    format_ss.append(ss[v])
        format_ss = "\t".join(format_ss)
        sys.stdout.write(f"{format_ss}\n")
        line_idx += 1
            

                                        
            


sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
