# GWAS summary file format v0.1

GWAS summary file 存储按照[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)进行存储

meta file 部分按照[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)进行存储。

与[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)的区别：

1. 文件名按照我们定义
2. meta file 中的field增加了：`url`、`reference`、`project_shortname`

如果不了解文件格式[请阅读文件格式要求](#文件格式要求)

运行代码格式化自己的数据[请阅读格式化流程](#代码)

WangLabGWAS数据存储路径位于文件服务器：`/data/share/wanglab/GWAS-Summary-Statistics`

## Introduction
对于一个表型的GWAS summary，我们应当保存两个文件：
1. `phenotype_ancestry_year_build_projectName.tsv.gz`  summary text foramat
2. `phenotype_ancestry_year_build-meta.yaml ` meta file， 记录其他额外的信息

文件存储结构：
```
GWAS-Summary-Statistics/
└── trait/
    ├── phenotype_ancestry_year_build_projectName1.tsv.gz
    ├── phenotype_ancestry_year_build_projectName-meta1.yaml
    ├── phenotype_ancestry_year_build_projectName2.tsv.gz
    └── phenotype_ancestry_year_build_projectName-meta2.yaml
```

下面进行详细介绍
### GWAS summary file
文件名命名应当按照以下标准进行命名
`phenotype_ancestry_year_build_projectName.tsv.gz`  summary text foramat

- `phenotype` 对应数据的表型，该值也对应`meta file`中的`trait_description` field.
- `ancestry` 对应数据的族裔来源，该值也对应`meta file`中的`samples_ancestry` field.
- `year` 对应数据的发布的时间，该值也对应`meta file`中的`year` field.
- `build` 对应数据的采用的基因组版本，该值也对应`meta file`中的`genome_assembly` field.
- `project_shortname` 对应数据的项目来源缩写，用于区分前四个文件名field相同的情况，该值也对应`meta file`中的`project_shortname` field.


### GWAS summary meta file
目前采用[yaml]()存储meta 信息，命名规则为：`filename`+`-meta.yaml`。`filename`为GWAS summary file的文件名。

该文件主要用于存放相关的样本大小、md5、是否sort等信息，具体[field](#field)请点击链接。

此部分可以通过`generateMetaFile.py` 读取GWAS summary meta file
>GWAS summary meta file最好是采用我们的方法格式化后的文件；但若是未格式化的文件不会影响meta file生成。

如果**任何Field是不确认**的请填写`NA`








#### `Field`

| Key                          | Value        | Description                                 | Accepted Value      |
|------------------------------|--------------|---------------------------------------------|---------------------|
| ancestry_method              | genetically determined        | Method used to determine sample ancestry e.g. self reported/genetically determined  | Text string (multiple possible) |
| coordinate_system            | 1-based        | Coordinate System                           | 1-based/0-based     |
| data_file_md5sum             | c4fcf2ef404f36cd3bbb2301fda94a1c | Data file MD5 checksum                      | Alphanumeric hash  |
| data_file_name               | cad_white_2022_GRCh37_CardiogramPlusC4D | Data file name                              | Text string         |
| date_last_modified           | 2023-08-15 | Date last modified                         | Date format ('YYYY-MM-DD') |
| file_type                    | GWAS-SSF v0.1        | File type                                   | Text string (multiple possible) |
| genome_assembly              | GRCh37       | Genome assembly                            | GRCh/NCBI/UCSC      |
| genotyping_technology        | Genome-wide genotyping array        | Genotyping technology                      | Text string (multiple possible) |
| gwas_id                      | GCST90000123        | GWAS ID                                     | Text string (multiple possible) |
| is_harmonised                | false        | Flag whether the file is harmonised        | Boolean             |
| is_sorted                    | true         | Flag whether the file is sorted by genomic location | Boolean             |
| minor_allele_freq_lower_limit| 0.001        | Lowest possible minor allele frequency    | Numeric             |
| project_shortname            | AS           | Project shortname                          | Text string         |
| reference                    | Global GWAS Meta Analysis on CAD        | Reference                                   | Text string (multiple possible) |
| samples_ancestry             | white        | Sample ancestry                            | Text string (multiple possible) |
| samples_size                 | 12345        | Sample size                                | Integer             |
| sex                          | M        | Indicate if and how the study was sex-stratified | "M", "F", "combined", or "#NA" |
| trait_description            | cad          | Author reported trait description         | Text string (multiple possible) |
| url                          |https://csg.sph.umich.edu/willer/public/glgc-lipids2021/results/ancestry_specific/HDL_INV_AFR_HRC_1KGP3_others_ALL.meta.singlevar.results.gz        | URL                                         | Text string (URL format) |


## Usage

### Installation

**Requirments**: `python>3.7`

下载源码

`git clone git@github.com:WangLabBig/GWASFormat.git`



直接添加`scripts`到环境变量

`export PATH=$PATH:yourpath/scripts`

### Pipline

代码存放于[Wanglab_GWASFormat](https://github.com/WangLabBig/GWASFormat)，本地服务器路径如下：

>[详细参数介绍](#API)

运行流程建议：

step1 格式化原始数据成标准格式

`cat youfile | GWASFormat.py -i 1 3 5 4 7 8 6 9 | bgzip > yourfile.tsv.gz`

step2 生成meta file

`generateMetaFile.py -i youfile.tsv.gz`

step3 (optional and coming soon) 增加ref列以及增加rsid与variant_id

#### 重命名variant_id
`cat yourfile | resetID2.py -i variant_id 1 2 ref alt -s --add-chr`



## API

### `GWASFormat.py` 
**用法:** GWASFormat.py [-h] -i COL_INDICES [COL_INDICES ...] [-d DELIMITER]
                     [--pval_type {pval,log10p}]
                     [--effect_type {beta,odds_ratio,hazard_ratio}]
                     [--ci_upper CI_UPPER] [--ci_lower CI_LOWER] [--rsid RSID]
                     [--variant_id VARIANT_ID] [--info INFO]
                     [--ref_allele REF_ALLELE] [-n N]
                     [--other_col OTHER_COL [OTHER_COL ...]]


- `-h, --help`: 显示帮助信息并退出。

- `-i COL_INDICES [COL_INDICES ...], --col COL_INDICES [COL_INDICES ...]`: 指定以下数据字段的列：
  - 染色体
  - 位置
  - 效应等位基因 (EA)
  - 其他等位基因 (OA)
  - 效应大小 (beta)
  - 标准误差 (se)
  - 效应等位基因频率 (EA_freq)
  - P 值 (pval)
  
  列索引应从 1 开始。如果要跳过某列，请将其设置为 0。如: `-i 1 2 3 4 5 6 7 8`，对应染色体信息在第一列，基因组位置在第二列等。

- `-d DELIMITER, --delimiter DELIMITER`: 指定输入文件中使用的分隔符。

- `--pval_type {pval,log10p}`: 指定输出文件中 P 值列的类型。默认为 pval。应选择 pval 或 log10p 中的一个。

- `--effect_type {beta,odds_ratio,hazard_ratio}`: 指定输出文件中效应列的类型。默认为 beta。应选择 beta、odds_ratio 或 hazard_ratio 中的一个。

- `--ci_upper CI_UPPER`: 指定置信区间的上限列索引。这是可选的。

- `--ci_lower CI_LOWER`: 指定置信区间的下限列索引。这是可选的。

- `--rsid RSID`: 指定 rsid 信息的列索引。这是可选的。

- `--variant_id VARIANT_ID`: 指定 variant_id 信息的列索引。这是可选的。

- `--info INFO`: 指定修复信息度量的列索引。这是可选的。

- `--ref_allele REF_ALLELE`: 指定参考等位基因信息的列索引。这是可选的。

- `-n N`: 指定样本数量的列索引。这是可选的。

- `--other_col OTHER_COL [OTHER_COL ...]`: 指定其他附加列的列索引。这是可选的。

**作者:** xutingfeng@big.ac.cn

**版本:** 1.0

**示例代码**
1. specific column index and format all 
    `cat yourfile | GWASFormat.py -i "CHR" 0 A1 A2 A1_FREQ -6 -5 9 `
2. specific beta is hazard ratio and pval is log10p; --pval_type log10p/pval --effect_type hazard_ratio/beta/odds_ratio
    `cat yourfile | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --pval_type log10p --effect_type odds_ratio`
3. spcific other columns
    `cat yourfile | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --other_col -2 -4`

### `generateMetaFile.py`

**用法:** generateMetaFile.py [-h] -i INPUT [-s]

**描述:**

本脚本用于为GWAS总结文件生成元数据文件。

**作者:** xutingfeng@big.ac.cn

GWAS SSF: [https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1](https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1)
GWAS SSF 版本: GWAS-SSF v0.1

**代码版本:** 1.0

**示例代码:**

1. 简单使用如下：

`generateMetaFile.py -i yourfile`

2. -s 会检查文件是否已排序：

`generateMetaFile.py -i yourfile -s`


**选项:**

- `-h`, `--help`: 显示帮助信息并退出。
- `-i INPUT`, `--input INPUT`: 输入的元数据文件。
- `-s`, `--check_sort`: 检查文件是否已排序。


### resetID2.py

**用法:** resetID2.py [-h] [-i COL_ORDER [COL_ORDER ...]] [-k] [-s]
                     [-d DELIMITER] [--add-chr] [-I ID_DELIMITER]

**描述:**

本脚本用于设置或替换任意文件的variant_id。默认的ID格式为chr:pos:ref:alt。

**作者:** wavefancy@gmail.com（原始代码）和 xutingfeng@big.ac.cn（根据本版本进行修改）

**版本:** 2.0

该脚本可以基于原始ID列生成新的ID。默认情况下，新的ID格式为chr:pos:ref:alt。

默认情况下，假设输入文件包含标题。
- `-s` 选项会使用 `sorted([ref, alt])` 对ref和alt等位基因进行排序。默认情况下不进行排序。
- `-k` 选项会保留原始ID，并使用 `-I/--id-delimter` 作为分隔符将其附加在新ID之后（默认为':'）。
- `-d` 选项用于指定输入文件的分隔符（默认为任意空白字符）。
- `--add-chr` 选项会在ID的chr列添加'chr'前缀，以保留或添加'chr'到ID中。

**示例:**

1. 重命名 'variant_id' 列：`cat test.txt | resetID2.py -i variant_id 1 2 3 4`
这将会将 'variant_id' 列重命名为格式：1:2:3:4 => chr:pos:ref:alt。

2. 重命名 'variant_id' 列，并使用排序和'chr'前缀进行格式化：`cat test.txt | resetID2.py -i variant_id 1 2 3 4 -s --add-chr`
这将会重命名 'variant_id' 列，并将其格式化为chr:pos:ref:alt，对ref和alt等位基因进行排序，并在chr列添加'chr'前缀。

3. 重命名 'variant_id' 列，使用排序和'chr'前缀，并使用'_'作为id_delimiter：`cat test.txt | resetID2.py -i variant_id 1 2 3 4 -I _ -s --add-chr`

这将会重命名 'variant_id' 列，并将其格式化为chr:pos:ref:alt，对ref和alt等位基因进行排序，并在chr列添加'chr'前缀，同时使用'_'作为分隔符。

**选项:**

- `-h`, `--help`: 显示帮助信息并退出。
- `-i COL_ORDER [COL_ORDER ...]`, `--col_order COL_ORDER [COL_ORDER ...]`:
指定ID、chr、pos、ref、alt的列顺序。默认为ID列=2，chr列=1，pos列=4，ref列=5，alt列=6。列索引从1开始。如果格式已经按照这个顺序排列，您可以直接使用 `-i 3` 进行后续操作。您可以在此处指定索引或列名。
- `-k`, `--keep`: 在输出中保留原始rsID。
- `-s`, `--sort`: 使用 `sorted([ref, alt])` 对ref和alt等位基因进行排序。
- `-d DELIMITER`, `--delimiter DELIMITER`:
输入文件的分隔符。默认为任意空白字符。
- `--add-chr`: 在ID的chr列添加'chr'前缀。
- `-I ID_DELIMITER`, `--id-delimiter ID_DELIMITER`:
ID的分隔符。默认为':'。这会控制输出ID的分隔符。如果`-i`只有一个参数，并且应用了'chr'或排序操作，则此分隔符将用于将旧ID分割为chr、pos、ref、alt。
