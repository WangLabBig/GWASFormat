
# GWAS summary file format v0.1





## Updated 20241230

`versionConvert.py` change the params of `--one-base` to `--zero-based` as most users's input files are gwas summstats which are one-based, so set this as default.


## Main


:point_right: [使用流程请点这里](#pipline)
 
GWAS summary file与meta file部分按照[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)进行存储

与[GWAS SSF v1.0](https://github.com/EBISPOT/gwas-summary-statistics-standard)的区别：

1. 重新定义了文件名
2. meta file 中的field增加了：`url`、`reference`、`project_shortname`

如果不了解文件格式[请阅读文件格式要求](#introduction)

运行代码格式化自己的数据[请阅读格式化流程](#pipline)

WangLabGWAS数据存储路径位于文件服务器：`/data/share/wanglab/GWAS-Summary-Statistics`

## Introduction
对于一个表型的GWAS summary，我们应当保存两个文件：
1. `phenotype_ancestry_year_build_projectName.tsv.gz`  （summary text format，GWAS文件）
2. `phenotype_ancestry_year_build-meta.yaml ` （meta file，记录其他额外的信息）

文件存储结构：
```
GWAS-Summary-Statistics/
└── trait/
    ├── phenotype_ancestry_year_build_projectName1.tsv.gz
    ├── phenotype_ancestry_year_build_projectName-meta.yaml
    ├── phenotype_ancestry_year_build_projectName2.tsv.gz
    └── phenotype_ancestry_year_build_projectName-meta.yaml
```

下面进行详细介绍
### GWAS summary file
文件名命名应当按照以下标准进行命名：
`phenotype_ancestry_year_build_projectName.tsv.gz`

- `phenotype` 对应数据的表型，该值也对应`meta file`中的`trait_description` field.
- `ancestry` 对应数据的族裔来源，该值也对应`meta file`中的`samples_ancestry` field.
- `year` 对应数据的发布的时间，该值也对应`meta file`中的`year` field.
- `build` 对应数据的采用的基因组版本，该值也对应`meta file`中的`genome_assembly` field.
- `project_shortname` 对应数据的项目来源缩写，用于区分前四个文件名field相同的情况，该值也对应`meta file`中的`project_shortname` field.

Example Name: `cad_white_2022_GRCh38_NG.tsv.gz`

### GWAS summary meta file
目前采用[yaml]()存储meta 信息，命名规则为：`filename`+`-meta.yaml`。`filename`为GWAS summary file的文件名。

:warning:  Note:**使用generateMetaFile.py** 可以快速生成！！！

该文件主要用于存放相关的样本大小、md5、是否sort等信息，具体[field](#field)请点击链接。

此部分可以通过`generateMetaFile.py` 读取GWAS summary meta file
>GWAS summary meta file最好是采用我们的方法格式化后的文件；但若是未格式化的文件不会影响meta file生成。

如果**任何Field是不确认**的请填写`NA`








#### `Field`

| Key                           | Value                                   | Description                                                                        | Accepted Value                  |
| ----------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------- |
| ancestry_method               | genetically determined                  | Method used to determine sample ancestry e.g. self reported/genetically determined | Text string (multiple possible) |
| coordinate_system             | 1-based                                 | Coordinate System                                                                  | 1-based/0-based                 |
| data_file_md5sum              | c4fcf2ef404f36cd3bbb2301fda94a1c        | Data file MD5 checksum                                                             | Alphanumeric hash               |
| data_file_name                | cad_white_2022_GRCh37_CardiogramPlusC4D | Data file name                                                                     | Text string                     |
| date_last_modified            | 2023-08-15                              | Date last modified                                                                 | Date format ('YYYY-MM-DD')      |
| file_type                     | GWAS-SSF v0.1                           | File type                                                                          | Text string (multiple possible) |
| genome_assembly               | GRCh37                                  | Genome assembly                                                                    | GRCh/NCBI/UCSC                  |
| genotyping_technology         | Genome-wide genotyping array            | Genotyping technology                                                              | Text string (multiple possible) |
| gwas_id                       | GCST90000123                            | GWAS ID                                                                            | Text string (multiple possible) |
| is_harmonised                 | false                                   | Flag whether the file is harmonised                                                | Boolean                         |
| is_sorted                     | true                                    | Flag whether the file is sorted by genomic location                                | Boolean                         |
| minor_allele_freq_lower_limit | 0.001                                   | Lowest possible minor allele frequency                                             | Numeric                         |
| project_shortname             | AS                                      | Project shortname                                                                  | Text string                     |
| reference                     | Global GWAS Meta Analysis on CAD        | Reference                                                                          | Text string (multiple possible) |
| samples_ancestry              | white                                   | Sample ancestry                                                                    | Text string (multiple possible) |
| samples_size                  | 12345                                   | Sample size                                                                        | Integer                         |
| sex                           | M                                       | Indicate if and how the study was sex-stratified                                   | "M", "F", "combined", or "#NA"  |
| trait_description             | cad                                     | Author reported trait description                                                  | Text string (multiple possible) |
| url                           | https:your_file_download_url.com        | URL                                                                                | Text string (URL format)        |


## Usage

### Installation

**Requirments**: `python>3.7` `liftover`

> run `pip install liftover`

**下载源码**

`git clone git@github.com:WangLabBig/GWASFormat.git`

直接添加`scripts`到环境变量

`export PATH=$PATH:/PATH_TO_GWASFORMAT/scripts`

### Pipline

代码存放于[Wanglab_GWASFormat](https://github.com/WangLabBig/GWASFormat)，本地服务器路径如下：

`/pmaster/xutingfeng/share/GWASFormatter/scripts`

>[详细参数介绍](#API)

运行流程建议：

**step1:** [GWASFormat.py](#gwasformatpy) 格式化原始数据成标准格式

`cat youfile | GWASFormat.py -i 1 3 5 4 7 8 6 9 | bgzip > yourfile.tsv.gz`

**step2:** 使用 [generateMetaFile.py](#generatemetafilepy) 生成meta file

`generateMetaFile.py -i youfile.tsv.gz`

**step3:** (optional and coming soon) 修改variant_id，pos的版本转换等，详细信息请跳转到[step3操作](#step3操作)

**step4:** 采用bgzip（**请注意对step3做完的数据重新bgzip**）和tabix进行数据压缩。

`tabix -b 2 -e 2 -s 1 -c c -f youfile.tsv.gz` 
>[tabix](https://www.htslib.org/doc/tabix.html)的简单操作指南请[点击该链接跳转](#step4-tabix简易指南)

**step5:** 构建pheweb需要的格式: `pheweb_format.py -i 1 2 4 3 8 --af 7 --beta 5 --sebeta 6`
>必须要完成step1，然后直接接上该代码既可。


### 示例代码：

#### 示例1：格式化bolt-lmm的输出，且基因组版本为GRCh38。

bolt-lmm输出包含这些列：SNP     CHR     BP      GENPOS  ALLELE1 ALLELE0 A1FREQ  INFO    CHISQ_LINREG    P_LINREG        BETA    SE      CHISQ_BOLT_LMM_INF      P_BOLT_LMM_INF  CHISQ_BOLT_LMM  P_BOLT_LMM GWASTrait

code:`zcat raw/invnorm_lvef.tsv.gz  |GWASFormat.py -i 2 3 5 6 11 12 7 P_BOLT_LMM --rsid 1 --variant-id 1| resetID2.py -i variant_id 1 2 3 4 -s | versionConvert.py -c hg19 hg38 /pmaster/xutingfeng/share/liftover_chain/hg19 -i 1 2 | sort -k1n -k2n | bgzip > invnorm_lvef.tsv.gz `

（1）这里`GWASFormat.py`首先`-i`指定chr,pos,effect_allele, other_allele,beta, se, effect_allele_freq, p_value，然后`--rsid`以及`--variant-id` 指定snpID列

（2）然后`resetID2.py` `-i` 传入需要更名的ID列的列名为`variant_id`，chr，pos，EA和OA。`-s`对id中的两个allele排序，并且加上`sorted_alleles`列名后缀在原始的`variant_id`上。

（3）基因组版本转换`versionConvert.py`，`-c` 指定从hg19=>hg38，并在后面附上hg19转换至hg38的chain文件目录。`-i` 指定chr和pos为第1列和第2列，并且第二列会加上基因组版本(`_hg38`)的后缀；然后接上sort进行排序 ，最后bgzip保存

现在产生meta file。`generateMetaFile.py -i yourfile` 

#### 示例2：regenie输出

`zcat youfule|GWASFormat.py -i 1 2 5 4 BETA SE A1FREQ LOG10P --pval-type log10p -n N --variant-id ID` 

> 是否需要resetID以及versionConvert取决于你的数据。
> 如果需要转成pheweb format：
`zcat yourfile|pheweb_format.py -i 1 2 4 3 8 --af 7 --beta 5 --sebeta 6 --log10p|bgzip > outputfile`

### 上述操作部分注释

#### step3操作

[resetID2.py](#resetid2py) 用于重命名variant_id

`cat yourfile | resetID2.py -i variant_id 1 2 ref alt -s --add-chr`
> **⚠️注意：** `-s` 会添加 `_sorted_alleles`到原始的列名之后

#### 基因组版本转换
[versionConvert.py](#versionconvertpy)

`cat yourfile | versionConvert.py -c hg19 hg38 chainFileDir -i 1 2`

这条代码会根据-i输入的列号把第一列处理成染色体，第二列处理成对应的位置，这些信息组成了一个variants的坐标，`-c hg19 hg38 chainFileDir`就指明了从hg19=>hg38的版本转换
>**⚠️注意：** 
> 
>1. 默认是会把没匹配的、匹配到多个位置的行的pos丢掉，`-k/--keep-unmapped` 可以保留这些
>
>2. liftover后的新位置信息会在原位置替换旧的信息，并在标题上加上后缀：`_hg38`。`--no-suffix`会去掉后缀，`--add-last`会不覆盖旧的位置信息，而在最后面加上新的位置信息列

#### step4 tabix简易指南

**一条龙创建index：**`tabix -s chr -b start -e end -c comment yourfile.tsv.gz`

下面进行参数介绍与指北~

`-s`, `-b`, `-e` 三个参数用于指定索引的坐标信息。比如我们的基因组数据有：染色体和基因组Position，-c指定Chr，Position用于指定染色体上对应的位置。其实从这里我们就可以知道我们的行有三个索引：Chr，posStart，posEnd，利用这三个索引我们可以根据指定的区间如：`chr1:123-5687`的索引从我们的数据中取出数据。

`-c` 用于指定comment，这个comment其实就是header。比如对于vcf文件，第一列是：`#chr`，`-c #`即可。对于如我们的格式化后的数据第一列是`chromosome`，`-c c`即可。
> 请注意一定要采用-c来处理header，这样子索引的时候：`tabix -h yourfile.tsv.gz 1` 进行查询，输出的时候会包括header；如果采用`-S `强行跳过则会丢失。

因此衍生出来的几种管理数据的思路如下

##### 第一种情况：

| chromosome | base_pair_location | effect_allele | other_allele |
| ---------- | ------------------ | ------------- | ------------ |
| 1          | 785910             | G             | C            |
| 1          | 788511             | G             | C            |
| 1          | 804185             | G             | C            |
| 1          | 804863             | T             | C            |

这里就是标准的基因组相关的文件格式

基于此可以通过这种方式创建索引：`tabix  -s 1 -b 2 -e 2 -c c yourfile.tsv.gz`

索引数据的方式如下：

1. 索引染色体的所有variants：`tabix yourfile.tsv.gz -h chromose_id`

2. 索引指定区间：`tabix yourfile.tsv.gz -h chromosome:begin-end`

>注意这里的chromosome的写法，如果用于构建索引的数据文件中chromosome的编号格式是chr1、chr2这样的形式，在索引时也需要使用：
>`tabix yourfile.tsv.gz -h chr1:123-12345`
>对于使用[GWASFormat.py](#gwasformatpy)格式化后的数据，需使用1-25的数字作为染色体编号，23、24、25表示X染色体、Y染色体、MT染色体。因此对于我们格式化后的数据创建的tabix查询：
》`tabix yourfile.tsv.gz -h 1:123-12345`



##### 第二种情况：


| #fid | eid   | 1000017 | 1000025 |
| ---- | ----- | ------- | ------- |
| 3    | 3-0.0 | 260     | 918     |
| 3    | 3-1.0 | NA      | NA      |
| 4    | 4-0.0 | 455     | 582     |
| 4    | 4-1.0 | NA      | NA      |

`tabix -s chr -b start -e end -c comment yourfile.tsv.gz`，这里我们查询只需要查询fid，因此我们可以把eid当作我们虚假的pos，实际上我们索引的时候不能用到这部分信息。

基于此可以通过这种方式创建索引：`tabix  -s 1 -b 2 -e 2 -c # yourfile.tsv.gz`

索引数据的方式如下：`tabix yourfile.tsv.gz -h query_fid`



## API

### `GWASFormat.py` 
**用法:** GWASFormat.py [-h] -i COL_INDICES [COL_INDICES ...] [-d DELIMITER]
                     [--pval_type {pval,log10p}]
                     [--effect_type {beta,odds_ratio,hazard_ratio}]
                     [--ci_upper CI_UPPER] [--ci_lower CI_LOWER] [--rsid RSID]
                     [--variant_id VARIANT_ID] [--info INFO]
                     [--ref_allele REF_ALLELE] [-n N]
                     [--other_col OTHER_COL [OTHER_COL ...]]

**选项**
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
1. 指定列索引并进行格式化，支持列名、索引混合输入：

```bash
cat yourfile | GWASFormat.py -i "CHR" 0 A1 A2 A1_FREQ -6 -5 9 
```

2. 指定 beta 为odds_ratio，pval 为 log10p；--pval_type log10p/pval --effect_type hazard_ratio/beta/odds_ratio

```bash
cat yourfile | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --pval_type log10p --effect_type odds_ratio
```

3. 指定其他特定列：

```bash
cat yourfile | ./GWASFormat.py -i 1 3 5 4 7 8 6 9 --other_col -2 -4
```


### `generateMetaFile.py`

**用法:** generateMetaFile.py [-h] -i INPUT [-s]

**选项:**

- `-h`, `--help`: 显示帮助信息并退出。
- `-i INPUT`, `--input INPUT`: 输入的元数据文件。
- `-s`, `--check_sort`: 检查文件是否已排序。

**描述:**

本脚本用于为GWAS总结文件生成元数据文件。

**作者:** xutingfeng@big.ac.cn

GWAS SSF: [https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1](https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1)
GWAS SSF 版本: GWAS-SSF v0.1

**版本:** 1.0

**示例代码:**

1. 简单使用如下：

`generateMetaFile.py -i yourfile`

2. -s 会检查文件是否已排序：

`generateMetaFile.py -i yourfile -s`

### resetID2.py

**用法:** resetID2.py [-h] [-i COL_ORDER [COL_ORDER ...]] [-k] [-s]
                     [-d DELIMITER] [--add-chr] [-I ID_DELIMITER]

**选项:**

- `-h`, `--help`: 显示帮助信息并退出。
- `-i COL_ORDER [COL_ORDER ...]`, `--col_order COL_ORDER [COL_ORDER ...]`:
指定ID、chr、pos、ref、alt的列顺序。默认为ID列=2，chr列=1，pos列=4，ref列=5，alt列=6。列索引从1开始。如果格式已经按照这个顺序排列，您可以直接使用 `-i 3` 进行后续操作。您可以在此处指定索引或列名。
- `-k`, `--keep`: 在输出中保留原始rsID。
- `-s`, `--sort`: 使用 `sorted([ref, alt])` 对ref和alt等位基因进行排序，并且会添加 `_sorted_alleles`到原始的列名之后
- `-d DELIMITER`, `--delimiter DELIMITER`:
输入文件的分隔符。默认为任意空白字符。
- `--add-chr`: 在ID的chr列添加'chr'前缀。
- `-I ID_DELIMITER`, `--id-delimiter ID_DELIMITER`:
ID的分隔符。默认为':'。这会控制输出ID的分隔符。如果`-i`只有一个参数，并且应用了'chr'或排序操作，则此分隔符将用于将旧ID分割为chr、pos、ref、alt。

**描述:**

本脚本用于设置或替换任意文件的variant_id。默认的ID格式为chr:pos:ref:alt。

**作者:** wavefancy@gmail.com（原始代码）和 xutingfeng@big.ac.cn（根据本版本进行修改）

**版本:** 2.0

该脚本可以基于原始ID列生成新的ID。默认情况下，新的ID格式为chr:pos:ref:alt。

默认情况下，假设输入文件包含标题。
- `-s` 选项会使用 `sorted([ref, alt])` 对ref和alt等位基因进行排序。默认情况下不进行排序。
- `-k` 选项会保留原始ID，并使用 `-I/--id-delimter` 作为分隔符将其附加在新ID之后（默认为':'），且会添加 `_sorted_alleles`到原始的列名之后。
- `-d` 选项用于指定输入文件的分隔符（默认为任意空白字符）。
- `--add-chr` 选项会在ID的chr列添加'chr'前缀，以保留或添加'chr'到ID中。

**示例:**

1. 重命名 'variant_id' 列：`cat test.txt | resetID2.py -i variant_id 1 2 3 4`
这将会将 'variant_id' 列重命名为格式：1:2:3:4 => chr:pos:ref:alt。

2. 重命名 'variant_id' 列，并使用排序和'chr'前缀进行格式化：`cat test.txt | resetID2.py -i variant_id 1 2 3 4 -s --add-chr`
这将会重命名 'variant_id' 列，并将其格式化为chr:pos:ref:alt，对ref和alt等位基因进行排序，并且添加 `_sorted_alleles`到原始的列名之后，然后在chr列添加'chr'前缀，

3. 重命名 'variant_id' 列，使用排序和'chr'前缀，并使用'\_'作为id_delimiter：`cat test.txt | resetID2.py -i variant_id 1 2 3 4 -I _ -s --add-chr`这将会重命名 'variant_id' 列，并将其格式化为chr:pos:ref:alt，对ref和alt等位基因进行排序，并且添加 `_sorted_alleles`到原始的列名之后，然后在chr列添加'chr'前缀，同时使用'_'作为分隔符。

### versionConvert.py

**用法：**

```bash
versionConvert.py [-h] [-c CHAIN [CHAIN ...]] -i INPUT_COLS [INPUT_COLS ...] [-l] [-s DELIMTER] [-d]
```

**选项：**

- `-h`, `--help`: 显示帮助信息并退出。
- `-c CHAIN [CHAIN ...]`, `--chain CHAIN [CHAIN ...]`: 指定要从哪个基因组版本转换到哪个基因组版本（例如从'hg19'到'hg38'）。可选的 'cache' 参数指定缓存文件夹（默认为~/.liftover）。链文件可从以下网址下载：https://hgdownload.soe.ucsc.edu/downloads.html
- `-i INPUT_COLS [INPUT_COLS ...]`, `--input_cols INPUT_COLS [INPUT_COLS ...]`: 指定要转换的基因组位置。您可以提供多个列。第一列应为染色体索引，然后是位置列。示例：-i 1 2 3 4（用于转换列2、3和4中的染色体和位置）。
- `-l`, `--add-last`: 将转换后的位置添加为新列添加到末尾。
- `-s DELIMTER`, `--sep DELIMTER`: 指定输入文件中使用的分隔符。默认为制表符。
- `-k`, `--keep_unmapped`: KEEP未映射位置的行，两类：未匹配上和匹配到多个位置的。对于匹配到其他染色体的情况，参考`--drop`
- `-n`, `--no-suffix`：不加后缀到列名上
- `--drop`, 对于匹配到其他染色体的variants，也选择丢掉；默认不丢掉并且更新。

1. 默认是会把没匹配的、匹配到多个位置的行的pos输出成NA，`-k/--keep-unmapped` 可以自动过滤掉这些

2. 默认是新的pos替换原来的并且加上后缀：`_hg38`;`--no-suffix`会去掉后缀，`--add-last`会不覆盖转而在最后面加上新的列

**描述：**

本工具通过Liftover进行基因组位置转换。

**作者:** Tingfeng Xu (xutingfeng@big.ac.cn)
**版本:** 1.0

此工具允许您使用Liftover将基因组位置从一种版本转换为另一种版本。

默认情况下，输入文件假定具有标题。

**使用示例：**
1. 将位置从hg19转换为hg38并自动下载链文件：

```bash
cat yourfile | versionConvert.py -c hg19 hg38 -i 1 2 3 4
```

2. 使用特定链目录将位置从hg19转换为hg38，这将使用本地缓存文件作为'{target}To{query}.over.chain.gz'：

```bash
cat yourfile | versionConvert.py -c hg19 hg38 chainFilePath -i 1 2 3 4
```
