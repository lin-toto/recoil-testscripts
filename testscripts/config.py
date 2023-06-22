ROOT = '/work'

EXECUTABLE_ROOT = ROOT
DATASET_ROOT = ROOT + '/dataset'
RESULT_ROOT = ROOT + '/result'

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

MULTIANS = ROOT + '/multians' # will call multians-n11 and multians-n16
MBT2018_CDF = DATASET_ROOT + '/mbt2018_cdf.txt'

TEXT_DATASETS = ['rand_10', 'rand_50', 'rand_100', 'rand_200', 'rand_500',
                 'dickens', 'webster', 'enwik8', 'enwik9']

LIC_DATASETS = ['div2k801', 'div2k803', 'div2k805']