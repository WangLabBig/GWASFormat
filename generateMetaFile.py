#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:       :
@Date     :2023/08/15 15:37:07
@Author      :Tingfeng Xu
@version      :1.0
"""


import argparse
import os.path as osp
import os
import time
import textwrap
import hashlib
import yaml


DEFAULT_NA = "#NA"
FIELDS = [
    "gwas_id",
    "genotyping_technology",
    "samples_size",
    "samples_ancestry",
    "ancestry_method",
    "trait_description",
    "minor_allele_freq_lower_limit",
    "file_type",
    "data_file_md5sum",
    "data_file_name",
    "is_harmonised",
    "is_sorted",
    "date_last_modified",
    "genome_assembly",
    "coordinate_system",
    "sex",
    "year",
    "reference",
    "url",
    "project_shortname",
]


def open_file(file, mode=None):
    if file.endswith(".gz"):
        try:
            import gzip

            if mode is None:
                mode = "rt"
            return gzip.open(file, mode)
        except ImportError:
            raise ImportError("gzip is not installed")
    else:
        if mode is None:
            mode = "r"
        return open(file, mode)


def IsListSorted_fastk(
    file, key=lambda x, y: x <= y, sep="\t", cols=[0, 1], ele_key=int
):
    # source:https://www.cnblogs.com/clover-toeic/p/5600246.html

    with open_file(file) as f:
        header = f.readline()
        prev = f.readline().split(sep)
        prev = [ele_key(prev[i]) for i in cols]

        for line in f.readlines():
            line = line.split(sep)
            cur = [ele_key(line[i]) for i in cols]

            if not key(prev, cur):
                return False
            prev = cur
    return True


class metaGWAS:
    def __init__(self, **kwargs):
        self.keywords = FIELDS
        self.meta = {k: kwargs.get(k, DEFAULT_NA) for k in self.keywords}

    def write(self, filename):
        with open(filename, "w") as f:
            yaml.dump(self.meta, f, default_style="", default_flow_style=False)


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
        """
        ),
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        required=True,
        help="input meta file",
    )
    return parser


def parseGWASSummaryData(file):
    with open(file, "r") as f:
        header = f.readline()
        header = header.strip().split("\t")
def parseFileName(filename):
    parsedFileName = filename.split("_")
    if len(parsedFileName) == 5: # => standard 
        phenotype, ancestry, year, build, projectShortName = parsedFileName
        return phenotype, ancestry, year, build, projectShortName
    else:
        return None 
    

def checksum(filename, hash_factory=hashlib.md5, chunk_num_blocks=128):
    h = hash_factory()
    with open(filename, "rb") as f:
        while chunk := f.read(chunk_num_blocks * h.block_size):
            h.update(chunk)
    return h.hexdigest()


def getfilename(file):
    if file.endswith(".gz"):
        return osp.splitext(osp.splitext(file)[0])[0]
    else:
        return osp.splitext(file)[0]


def getLastModifyTime(file):
    file_stat = os.stat(file)
    time_string = time.ctime(file_stat.st_mtime)
    time_struct = time.strptime(time_string, "%a %b %d %H:%M:%S %Y")
    formatted_time = time.strftime("%Y-%m-%d", time_struct)
    return formatted_time


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    res_dict = {}
    file = args.input
    # get md5
    md5_start = time.time()
    filename = getfilename(file)
    metaFileName = filename + "-meta.yaml"
    md5 = checksum(file)
    md5_end = time.time()
    res_dict["data_file_name"] = filename
    res_dict["data_file_md5sum"] = md5
    print("md5 time: ", md5_end - md5_start)
    # get additional info
    getAdditonalInfo = parseFileName(filename)
    if getAdditonalInfo is not None:
        phenotype, ancestry, year, build, projectShortName = getAdditonalInfo
        res_dict["trait_description"] = phenotype
        res_dict["samples_ancestry"] = ancestry
        res_dict["year"] = year
        res_dict["genome_assembly"] = build
        res_dict["project_shortname"] = projectShortName

    # isSorted
    soted_start = time.time()
    isSorted = IsListSorted_fastk(
        file, key=lambda x, y: x <= y, sep="\t", cols=[0, 1], ele_key=int
    )
    res_dict["is_sorted"] = isSorted
    soted_end = time.time()
    print("sorted time: ", soted_end - soted_start)
    # last modified time
    stat_start = time.time()
    last_modified_time = getLastModifyTime(file)
    res_dict["date_last_modified"] = last_modified_time
    stat_end = time.time()
    print("stat time: ", stat_end - stat_start)
    gwas = metaGWAS(
        **res_dict
    )
    gwas.write(metaFileName)


# ---
# genotyping_technology:
#   - Genome-wide genotyping array
# gwas_id: GCST90000123
# samples:
# - sample_size: 12345
#   sample_ancestry:
#     - European
#   ancestry_method:
#     - self-reported
#     - genetically determined
# trait_description:
#   - breast carcinoma
# minor_allele_freq_lower_limit: 0.001
# data_file_name: 0000123.tsv
# file_type: GWAS-SSF v0.1
# data_file_md5sum: 32ce41c3dca4cd9f463a0ce7351966fd
# is_harmonised: false
# is_sorted: false
# date_last_modified: 2023-02-09
# genome_assembly: GRCh37
# coordinate_system: 1-based
# sex: combined
