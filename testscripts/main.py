import sys

from detect_system import *
from run_experiments import *
from loguru import logger
from collections import OrderedDict
import tempfile
import shutil
import csv
import argparse

ATTEMPTS = 10


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=11, help="Probability quantization level")
    parser.add_argument("--no-cuda", help="Do not run CUDA experiments", action='store_true')
    parser.add_argument("--no-avx", help="Do not run AVX experiments", action='store_true')
    parser.add_argument("--nsplit-large", type=int, required=False,
                        help="Force nsplit_large (defaults to max CUDA occupancy)")
    parser.add_argument("--nsplit-small", type=int, required=False,
                        help="Force nsplit_small (defaults to CPU core count)")
    return parser.parse_args()


def run_experiment(workdir: str, dataset: str, dataset_type: str,
                   nsplit_large: int, nsplit_small: int, throughput_csv_writer, compression_csv_writer, args):
    throughput = OrderedDict({
        'name': dataset,
        'interleaved_avx512': 0, 'conv_avx512': 0, 'recoil_avx512': 0,
        'interleaved_avx2': 0, 'conv_avx2': 0, 'recoil_avx2': 0,
        'multians': 0, 'conv_cuda': 0, 'recoil_cuda': 0,
    })

    compression = OrderedDict({
        'name': dataset,
        'uncompressed': 0,
        'interleaved': 0, 'conv_small': 0, 'recoil_small': 0,
        'multians': 0, 'conv_large': 0, 'recoil_large': 0
    })

    logger.info(f"Encoding dataset {dataset}")

    rans_bitstream_path = os.path.join(workdir, dataset + '.bin')
    recoil_large_bitstream_path = os.path.join(workdir, dataset + '_large.bin')
    recoil_small_bitstream_path = os.path.join(workdir, dataset + '_small.bin')
    conv_large_bitstream_path = os.path.join(workdir, dataset + '_large_conventional.bin')
    conv_small_bitstream_path = os.path.join(workdir, dataset + '_small_conventional.bin')

    if dataset_type != 'lic':
        fn_enc = run_encoding
        fn_dec = run_decoding_experiment
    else:
        fn_enc = run_lic_encoding
        fn_dec = run_lic_decoding_experiment

    compression['uncompressed'], compression['interleaved'] = fn_enc(
        args.n, f'encode_{dataset_type}', dataset, 1, rans_bitstream_path)

    _, compression['recoil_large'] = fn_enc(
        args.n, f'encode_{dataset_type}', dataset, nsplit_large, recoil_large_bitstream_path)
    _, compression['conv_large'] = fn_enc(
        args.n, f'encode_{dataset_type}_conventional', dataset, nsplit_large, conv_large_bitstream_path)

    compression['recoil_small'] = run_splits_combine(
        args.n, dataset, recoil_large_bitstream_path, nsplit_small, recoil_small_bitstream_path)
    _, compression['conv_small'] = fn_enc(
        args.n, f'encode_{dataset_type}_conventional', dataset, nsplit_small, conv_small_bitstream_path)

    logger.info(f"Decoding dataset {dataset}")

    if not args.no_avx:
        if args.avx_version == 512:
            throughput['interleaved_avx512'] = fn_dec(
                args.n, 512, f'decode_{dataset_type}_avx', ATTEMPTS, dataset, rans_bitstream_path)
            throughput['recoil_avx512'] = fn_dec(
                args.n, 512, f'decode_{dataset_type}_avx', ATTEMPTS, dataset, recoil_small_bitstream_path,
                recoil_large_bitstream_path + '.cdf')
            throughput['conv_avx512'] = fn_dec(
                args.n, 512, f'decode_{dataset_type}_conventional_avx', ATTEMPTS, dataset, conv_small_bitstream_path)

        throughput['interleaved_avx2'] = fn_dec(
            args.n, 2, f'decode_{dataset_type}_avx', ATTEMPTS, dataset, rans_bitstream_path)
        throughput['recoil_avx2'] = fn_dec(
            args.n, 2, f'decode_{dataset_type}_avx', ATTEMPTS, dataset, recoil_small_bitstream_path,
            recoil_large_bitstream_path + '.cdf')
        throughput['conv_avx2'] = fn_dec(
            args.n, 2, f'decode_{dataset_type}_conventional_avx', ATTEMPTS, dataset, conv_small_bitstream_path)

    if not args.no_cuda:
        throughput['recoil_cuda'] = fn_dec(
            args.n, 2,f'decode_{dataset_type}_cuda', ATTEMPTS, dataset, recoil_large_bitstream_path)
        throughput['conv_cuda'] = fn_dec(
            args.n, 2,f'decode_{dataset_type}_conventional_cuda', ATTEMPTS, dataset, conv_large_bitstream_path)

        if dataset_type != 'lic':
            logger.info(f"Running multians")
            compression['multians'], throughput['multians'] = run_multians(ATTEMPTS, dataset)

    throughput_csv_writer.writerow(throughput.values())
    compression_csv_writer.writerow(compression.values())


def main(workdir: str):
    args = parse_args()

    logger.info("Detecting environment")

    num_cpu_threads, avx_version = detect_cpu()
    logger.info(f"Core Count: {num_cpu_threads}, AVX{avx_version}")
    if avx_version is None and not args.no_avx:
        logger.error("No AVX2/AVX512 support detected. To disable AVX tests, re-run with --no-avx.")
        sys.exit(1)
    args.avx_version = avx_version

    cuda_occupancy = detect_cuda_occupancy()
    logger.info(f"CUDA max occupancy: {cuda_occupancy}")
    if cuda_occupancy is None and not args.no_cuda:
        logger.error("CUDA occupancy detection failed. To disable CUDA tests, re-run with --no-cuda.")
        sys.exit(1)

    if cuda_occupancy is None and args.nsplit_large is None:
        logger.error("Argument --nsplit-large must be specified when CUDA occupancy detection fails.")
        sys.exit(1)

    nsplit_large = args.nsplit_large if args.nsplit_large is not None else cuda_occupancy
    nsplit_small = args.nsplit_small if args.nsplit_small is not None else num_cpu_threads

    logger.info(f"Using {nsplit_large} splits for Recoil encoding, then combining to {nsplit_small} splits")

    logger.info(f"Opening throughput.csv and compression.csv for writing")
    throughput_csv = open('throughput.csv', 'w')
    compression_csv = open('compression.csv', 'w')
    throughput_csv_writer = csv.writer(throughput_csv)
    compression_csv_writer = csv.writer(compression_csv)
    throughput_csv_writer.writerow(['',
                                    'Interleaved rANS AVX512', "Conventional AVX512", "Recoil AVX512",
                                    'Interleaved rANS AVX2', "Conventional AVX2", "Recoil AVX2",
                                    "multians", 'Conventional CUDA', "Recoil CUDA"])
    compression_csv_writer.writerow(['', 'Uncompressed Size', 'Interleaved rANS', 'Conventional Small', 'Recoil Small',
                                     'multians', 'Conventional Large', 'Recoil Large'])

    for dataset in TEXT_DATASETS:
        run_experiment(workdir, dataset, 'textfile', nsplit_large, nsplit_small, throughput_csv_writer, compression_csv_writer, args)

    for dataset in LIC_DATASETS:
        run_experiment(workdir, dataset, 'lic', nsplit_large, nsplit_small, throughput_csv_writer, compression_csv_writer, args)

    throughput_csv.close()
    compression_csv.close()


if __name__ == '__main__':
    workdir = tempfile.mkdtemp()
    logger.info(f"Created temporary working directory at {workdir}")
    try:
        main(workdir)
    finally:
        logger.info(f"Cleaning up {workdir}")
        shutil.rmtree(workdir)