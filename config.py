EXECUTABLE_ROOT = '/tmp/tmp.O7EvR8yCgW/cmake-build-release-server/examples'
DATASET_ROOT = '/home/dataset'

EXECUTABLES = {
    'detect_cuda_occupancy': '13_detect_cuda_occupancy/detect_cuda_occupancy',

    'encode_textfile': '10_encode_textfile/encode_textfile',
    'encode_textfile_conventional': '11_encode_textfile_symbolsplit/encode_textfile_symbolsplit',

    'combine_encoded_splits': '12_combine_encoded_splits/combine_encoded_splits',

    'decode_textfile_avx': '15_decode_textfile_split/decode_textfile_split',
    'decode_textfile_cuda': '16_decode_textfile_split_cuda/decode_textfile_split_cuda',
    'decode_textfile_conventional_avx': '17_decode_textfile_symbolsplit/decode_textfile_symbolsplit',
    'decode_textfile_conventional_cuda': '18_decode_textfile_symbolsplit_cuda/decode_textfile_symbolsplit_cuda',
}

MULTIANS = '/home/lin/multians/bin/demo'

TEXT_DATASETS = ['enwik9_10m',
                 #'rand_10m_5', 'rand_10m_20', 'rand_10m_100',
                 #'enwik9', 'mozilla', 'webster'
                ]