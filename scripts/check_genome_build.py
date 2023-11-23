#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Description:       :
@Date     :2023/10/30 17:07
@Author      :Xingyu Chen
@version      :1.0
"""

import argparse

try:
    from pyfaidx import Fasta
except ImportError:
    import subprocess
    import sys

    print("缺少pyfaidx模块，开始安装...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyfaidx"], check=True)
        print("liftover模块安装完成。")
        from pyfaidx import Fasta
    except subprocess.CalledProcessError:
        print("安装liftover模块时出错。请手动安装liftover。")
        sys.exit(1)
###Define function
def getParser():
    parser = argparse.ArgumentParser(
        description="""
        A script to check genome build. Developed by Xingyu Chen(chenxy@big.ac.cn)

        Version:1.0

        *Tips:
            1.If input file contain header, --header should be specified.
            2.the chrname of fasta file should be consistent with input file. e.g.">chr1 GRCh37:1:1:249250621:1" for fasta header, and "chr1 12231 A T" for input file
            3.Before run this script, it is recommended to remove multiple base pair data. If the matching rate is under 0.9 but more than 0.7, you could try to remove Polymorphic Loci and increase --snp_num to get a solid result.
            4.No need to figure out which column is actually A1 and A2.
            5.You could use -i flag to specify a file with each line contain a file address that need to check genome build, or use -f flag to specify a single file to calculate.

        Example code:
            python check_genome_build.py -i testdata/index_file -c 1 -p 3 -r 4 -a 5 --header --ref GRCh38ref.fasta
            python check_genome_build.py -f input_file -c 1 -p 2 -r 3 -a 4 --header --ref Homo_sapiens_assembly19.fasta

        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--index_file",
        help="Require(or -f), Input index_file, one file address per line. Conflict with -f flag",
    )
    group.add_argument(
        "-f",
        "--file",
        dest="input_file",
        help="Require(or -i), Input file address. Conflict with -i flag",
    )
    parser.add_argument(
        "-c",
        "--column_chrom",
        required=True,
        help="Require, column number of chromosome, start from 1",
    )
    parser.add_argument(
        "-p",
        "--column_pos",
        required=True,
        help="Require, column number of SNP position, start from 1",
    )
    parser.add_argument(
        "-r",
        "--column_ref",
        required=True,
        help="Require, column number of reference allele, start from 1",
    )
    parser.add_argument(
        "-a",
        "--column_alt",
        required=True,
        help="Require, column number of alternative allele, start from 1",
    )
    parser.add_argument(
        "--ref",
        required=True,
        help="Require, input reference genome file (fasta format)",
    )
    parser.add_argument(
        "--header",
        action="store_true",
        help="Optional, use --header if the input file contain header. Default is False.",
    )
    parser.add_argument(
        "--snp_num",
        default=30000,
        type=int,
        help="Optional, set how many SNPs included in this calculation, default is 30000. As the parameter value set higher, the false rate will lower, but the calculation time will also grow higher.",
    )

    return parser


def parse_input_file(
    file_path: str,
    chr_idx: int,
    pos_idx: int,
    a1_idx: int,
    a2_idx: int,
    header: bool,
    max_lines: int,
):
    """
    Parse a single input file to extract specific columns and format the data for the get_ref_seq function.

    Args:
        file_path: Path to the input file that needs to be parsed.
        chr_idx: Index (1-based) of the column in the file that contains the chromosome or contig name.
        pos_idx: Index (1-based) of the column in the file that contains the position.
        a1_idx: Index (1-based) of the column in the file that contains allele 1 (reference allele).
        a2_idx: Index (1-based) of the column in the file that contains allele 2 (alternative allele).
        header: Boolean indicating whether the file contains a header row.
        max_lines: Maximum number of lines to process from the input file.

    Returns:
        A list of strings formatted as "CHR POS A1 A2", which can be used as input for the get_ref_seq function.

    Note:
        The function reads the input file line-by-line, extracts the specified columns, and formats the data.
        If the input file contains a header and the header argument is set to True, the header line will be skipped.

    Example:
        file_path_sample = "path_to_input_file.txt"
        results = parse_input_file(file_path_sample, 1, 2, 3, 4, True, 1000)
    """

    results = []
    line_count = 0

    with open(file_path, "r") as file:
        if header:
            headers = file.readline().strip().split()
        for line in file:
            parts = line.strip().split()
            result = [
                parts[int(chr_idx) - 1],
                parts[int(pos_idx) - 1],
                parts[int(a1_idx) - 1],
                parts[int(a2_idx) - 1],
            ]
            results.append(" ".join(result))
            line_count += 1
            if line_count >= max_lines:
                break

    return results


def get_ref_seq(pos_data: list, refSeq_path: str, max_lines: int) -> list:
    """
    Get reference seq for position from the specified fasta file and position data.

    Args:
        pos_data: A list of strings. Each string contains two values separated by whitespace.
                  The first value is the contig name(chromosome name) and the second value is the position.
        refSeq_path: Path to the fasta file for reference seq.
        max_lines: Maximum number of lines to process from pos_data. Default is 30000.

    Returns:
        A list of strings. Each string contains the original data from pos_data with an additional value
        appended that represents the reference sequence.

    Sample Usage:
    pos_data_sample = ["chr1 12345 A T", "chr2 67890 T A"]
    ref_seq_path = "path_to_refSeq.fasta"
    result = get_ref_seq(pos_data_sample, ref_seq_path)
    """

    genome_ref = Fasta(refSeq_path, rebuild=False)
    line_count = 0
    output_data = []

    for line in pos_data:
        line_count += 1
        ss = line.split()
        pos = int(ss[1])
        try:
            aa = genome_ref[ss[0]][pos - 1 : pos]
        except ValueError:
            output_data.append(
                f"WARNING: In contig[{ss[0]}], cannot find pos: {ss[1]}. SKIP: {line}"
            )
            continue
        except KeyError:
            output_data.append(f"WARNING: Cannot find contig: {ss[0]}. SKIP: {line}")
            continue
        if (
            str(aa) == "A"
            or str(aa) == "T"
            or str(aa) == "C"
            or str(aa) == "G"
            or str(aa) == "N"
        ):
            ss.append(str(aa))
        else:
            ss.append("NA")
        output_data.append("\t".join(ss))
        if line_count >= max_lines:
            break

    return output_data


def calculate_matching_rate(ref_seq_data: list, max_line: int):
    """
    Calculate the matching rate of SNPs to the reference fasta from the output of get_ref_seq.

    Args:
        ref_seq_data: A list of strings. Each string contains the original data from pos_data
                      (provided to get_ref_seq) with an additional value appended that represents
                      the reference sequence. The format for each string is:
                      "contig_name position ref_allele alt_allele ref_seq_from_fasta".
        max_line: The total number of SNPs considered for the matching rate calculation.
                  This should be the same as the number of lines in ref_seq_data.

    Returns:
        A float representing the matching rate. It is calculated as the number of SNPs
        that match the reference divided by max_line.

    Note:
        The function checks if either the ref_allele or alt_allele matches the reference sequence
        from the fasta file for each SNP. If either matches, the SNP is considered as matching
        the reference.

    Example:
        ref_seq_data_sample = ["chr1 12345 A T A", "chr2 67890 T A T"]
        result = calculate_matching_rate(ref_seq_data_sample, 2)
    """

    n = 0
    flag = 0
    for line in ref_seq_data:
        line = line.split()
        if line[4] == line[2][0] or line[4] == line[3][0]:
            n += 1
    matching_rate = n / max_line

    return matching_rate


###main
if __name__ == "__main__":
    # parse the args
    parser = getParser()
    args = parser.parse_args()

    # parse multiple file name into array
    input_file_array = []

    if args.index_file != None:
        with open(args.index_file, "r") as index_file:
            for line in index_file:
                input_file_array.append(line.strip())
    else:
        input_file_array.append(args.input_file)

    # read all files and reformat it into get_ref_seq() format. [[file1snp1,file1snp2],[file2snp1,file2snp2]]
    parse_file_array = []

    for Files in input_file_array:
        parse_file_array.append(
            parse_input_file(
                Files,
                args.column_chrom,
                args.column_pos,
                args.column_ref,
                args.column_alt,
                args.header,
                args.snp_num,
            )
        )

    # get reference sequence base pair.
    refseq_array = []

    for Files in parse_file_array:
        if len(Files) <= int(args.snp_num):
            new_max_lines = len(Files)
        else:
            new_max_lines = args.snp_num
        refseq_array.append(get_ref_seq(Files, args.ref, new_max_lines))

    # calculate genome matching rate.
    matching_rate_array = []

    for Files in refseq_array:
        if len(Files) <= int(args.snp_num):
            new_max_lines = len(Files)
        else:
            new_max_lines = args.snp_num
        matching_rate_array.append(calculate_matching_rate(Files, new_max_lines))

    # print output
    for n in range(len(parse_file_array)):
        if matching_rate_array[n] >= 0.9:
            print(
                "The matching rate of file "
                + str(input_file_array[n])
                + "is "
                + str(matching_rate_array[n])
            )
            print(
                "the genome build of this file is consistent with the reference genome build"
            )
        elif matching_rate_array[n] < 0.9 and matching_rate_array[n] >= 0.7:
            print(
                "The matching rate of file "
                + str(input_file_array[n])
                + "is "
                + str(matching_rate_array[n])
            )
            print(
                "the genome build of this file may consistent with the reference genome build. The low matching rate may due to too many Polymorphic Loci"
            )
        elif matching_rate_array[n] < 0.7:
            print(
                "The matching rate of file "
                + str(input_file_array[n])
                + "is "
                + str(matching_rate_array[n])
            )
            print(
                "the genome build of this file is not match with the reference genome build. please try other reference genome build"
            )
