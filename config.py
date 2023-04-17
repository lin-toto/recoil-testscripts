EXECUTABLE_ROOT = '/tmp/tmp.O7EvR8yCgW/cmake-build-release-server/examples'
DATASET_ROOT = '/home/dataset'

EXECUTABLES = {
    'combine_encoded_splits': '01_combine_encoded_splits/combine_encoded_splits',
    'detect_cuda_occupancy': '02_detect_cuda_occupancy/detect_cuda_occupancy',

    'encode_textfile': '10_encode_textfile/encode_textfile',
    'encode_textfile_conventional': '11_encode_textfile_symbolsplit/encode_textfile_symbolsplit',

    'decode_textfile_avx': '15_decode_textfile_split/decode_textfile_split',
    'decode_textfile_cuda': '16_decode_textfile_split_cuda/decode_textfile_split_cuda',
    'decode_textfile_conventional_avx': '17_decode_textfile_symbolsplit/decode_textfile_symbolsplit',
    'decode_textfile_conventional_cuda': '18_decode_textfile_symbolsplit_cuda/decode_textfile_symbolsplit_cuda',

    'encode_lic': '20_encode_lic/encode_lic',
    'encode_lic_conventional': '21_encode_lic_symbolsplit/encode_lic_symbolsplit',

    'decode_lic_avx': '25_decode_lic_split/decode_lic_split',
    'decode_lic_cuda': '26_decode_lic_split_cuda/decode_lic_split_cuda',
    'decode_lic_conventional_avx': '27_decode_lic_symbolsplit/decode_lic_symbolsplit',
    'decode_lic_conventional_cuda': '28_decode_lic_symbolsplit_cuda/decode_lic_symbolsplit_cuda',

}

MULTIANS = '/home/lin/multians/bin/demo'
MBT2018_CDF = '/home/dataset/mbt2018_cdf.txt'

TEXT_DATASETS = [#'rand_10m_10', 'rand_10m_50', 'rand_10m_100',
                 #'mozilla', 'webster', 'enwik9',
                 #'dickens', 'enwik8'
                ]

LIC_DATASETS = ['div2k801', 'div2k803', 'div2k805']