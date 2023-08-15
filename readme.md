# GWAS summary file format v0.1

GWAS summary file 存储按照[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)进行存储

meta file 部分按照[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)进行存储。

与[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)的区别：

1. 文件名按照我们定义
2. meta file 中的field增加了：`url`、`reference`、`project_shortname`

如果不了解文件格式[请阅读文件格式要求](#文件格式要求)

运行代码格式化自己的数据[请阅读格式化流程](#代码)

WangLabGWAS数据存储路径位于文件服务器：`/data/share/wanglab/GWAS-Summary-Statistics`

## 文件格式要求
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
| data_file_name               | cad_white_2022_GRCh37_AS | Data file name                              | Text string         |
| date_last_modified           | 2023-08-15 | Date last modified                         | Date format ('YYYY-MM-DD') |
| file_type                    | GWAS-SSF v0.1        | File type                                   | Text string (multiple possible) |
| genome_assembly              | GRCh37       | Genome assembly                            | GRCh/NCBI/UCSC      |
| genotyping_technology        | Genome-wide genotyping array        | Genotyping technology                      | Text string (multiple possible) |
| gwas_id                      | GCST90000123        | GWAS ID                                     | Text string (multiple possible) |
| is_harmonised                | false        | Flag whether the file is harmonised        | Boolean             |
| is_sorted                    | true         | Flag whether the file is sorted by genomic location | Boolean             |
| minor_allele_freq_lower_limit| 0.001        | Lowest possible minor allele frequency    | Numeric             |
| project_shortname            | AS           | Project shortname                          | Text string         |
| reference                    | GWAS Analysis on BMI        | Reference                                   | Text string (multiple possible) |
| samples_ancestry             | white        | Sample ancestry                            | Text string (multiple possible) |
| samples_size                 | 12345        | Sample size                                | Integer             |
| sex                          | M        | Indicate if and how the study was sex-stratified | "M", "F", "combined", or "#NA" |
| trait_description            | cad          | Author reported trait description         | Text string (multiple possible) |
| url                          | https://csg.sph.umich.edu/willer/public/glgc-lipids2021/        | URL                                         | Text string (URL format) |


## 代码

代码存放于[Wanglab_GWASFormat](https://github.com/WangLabBig/GWASFormat)，本地服务器路径如下：
1. 

运行流程建议：

step1 格式化原始数据成标准格式

`cat youfile | GWASFormat.py -i 1 3 5 4 7 8 6 9 | gzip > yourfile.tsv.gz`

step2 生成meta file

`generateMetaFile.py -i youfile.tsv.gz`

step3 (optional and coming soon) 增加ref列以及增加rsid与variant_id

## 代码帮助

`GWASFormat.py` 

## Options

- `-h, --help`: Show this help message and exit.

- `-i COL_INDICES [COL_INDICES ...], --col COL_INDICES [COL_INDICES ...]`: Specify the columns of the following data fields:
  - Chromosome
  - Position
  - Effect allele (EA)
  - Other allele (OA)
  - Effect size (beta)
  - Standard error (se)
  - Allele frequency of the effect allele (EA_freq)
  - P-value (pval)
  
  Column indices should start from 1. If you want to skip a column, set it to 0.

- `-d DELIMITER, --delimiter DELIMITER`: Specify the delimiter used in the input file.

- `--pval_type {pval,log10p}`: Specify the type of p-value column in the output file. Default: pval. Should be one of pval or log10p.

- `--effect_type {beta,odds_ratio,hazard_ratio}`: Specify the type of effect column in the output file. Default: beta. Should be one of beta, odds_ratio, or hazard_ratio.

- `--ci_upper CI_UPPER`: Specify the column index for the upper bound of the confidence interval. This is optional.

- `--ci_lower CI_LOWER`: Specify the column index for the lower bound of the confidence interval. This is optional.

- `--rsid RSID`: Specify the column index for rsid information. This is optional.

- `--variant_id VARIANT_ID`: Specify the column index for variant_id information. This is optional.

- `--info INFO`: Specify the column index for imputation information metric. This is optional.

- `--ref_allele REF_ALLELE`: Specify the column index for the reference allele information. This is optional.

- `-n N`: Specify the column index for the number of samples. This is optional.

- `--other_col OTHER_COL [OTHER_COL ...]`: Specify the column indices for other additional columns. This is optional.
