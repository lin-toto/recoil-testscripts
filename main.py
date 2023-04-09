import sys

from detect_system import *
from run_experiments import *
from loguru import logger
from collections import OrderedDict
import tempfile
import shutil
import csv
import argparse

ATTEMPTS = 2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-cuda", help="Do not run CUDA experiments")
    parser.add_argument("--no-avx", help="Do not run AVX experiments")
    parser.add_argument("--nsplit-large", type=int, required=False,
                        help="Force nsplit_large (defaults to max CUDA occupancy)")
    parser.add_argument("--nsplit-small", type=int, required=False,
                        help="Force nsplit_small (defaults to CPU core count)")
    return parser.parse_args()


def main(workdir: str):
    args = parse_args()

    logger.info("Detecting environment")

    num_cpu_threads, avx_version = detect_cpu()
    logger.info(f"Core Count: {num_cpu_threads}, AVX: {avx_version}")
    if avx_version is None and not args.no_avx:
        logger.error("No AVX2/AVX512 support detected. To disable AVX tests, re-run with --no-avx.")
        sys.exit(1)

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
    throughput_csv_writer.writerow(['', f'Interleaved rANS AVX{avx_version}', 'Recoil CUDA', f"Recoil AVX{avx_version}",
                                    "Conventional CUDA", f"Conventional AVX{avx_version}", "multians"])
    compression_csv_writer.writerow(['', 'Uncompressed Size', 'Interleaved rANS', 'Recoil Large', 'Recoil Small',
                                     'Conventional Large', 'Conventional Small', 'multians'])

    for dataset in TEXT_DATASETS:
        throughput = OrderedDict({
            '_placeholder': '',
            'interleaved': 0, 'recoil_cuda': 0, 'recoil_avx': 0,
            'conv_cuda': 0, 'conv_avx': 0, 'multians': 0
        })

        compression = OrderedDict({
            '_placeholder': '',
            'uncompressed': 0,
            'interleaved': 0, 'recoil_large': 0, 'recoil_small': 0,
            'conv_large': 0, 'conv_small': 0, 'multians': 0
        })

        logger.info(f"Encoding dataset {dataset}")

        rans_bitstream_path = os.path.join(workdir, dataset + '.bin')
        recoil_large_bitstream_path = os.path.join(workdir, dataset + '_large.bin')
        recoil_small_bitstream_path = os.path.join(workdir, dataset + '_small.bin')
        conv_large_bitstream_path = os.path.join(workdir, dataset + '_large_conventional.bin')
        conv_small_bitstream_path = os.path.join(workdir, dataset + '_small_conventional.bin')

        compression['uncompressed'], compression['interleaved'] = run_encoding(
            'encode_textfile', dataset, 1, rans_bitstream_path)

        _, compression['recoil_large'] = run_encoding(
            'encode_textfile', dataset, nsplit_large, recoil_large_bitstream_path)
        _, compression['conv_large'] = run_encoding(
            'encode_textfile_conventional', dataset, nsplit_large, conv_large_bitstream_path)

        compression['recoil_small'] = run_splits_combine(
            dataset, recoil_large_bitstream_path, nsplit_small, recoil_small_bitstream_path)
        _, compression['conv_small'] = run_encoding(
            'encode_textfile_conventional', dataset, nsplit_small, conv_small_bitstream_path)

        logger.info(f"Decoding dataset {dataset}")

        if not args.no_avx:
            throughput['interleaved'] = run_decoding_experiment(
                'decode_textfile_avx', ATTEMPTS, dataset, rans_bitstream_path)
            throughput['recoil_avx'] = run_decoding_experiment(
                'decode_textfile_avx', ATTEMPTS, dataset, recoil_small_bitstream_path, recoil_large_bitstream_path + '.cdf')
            throughput['conv_avx'] = run_decoding_experiment(
                'decode_textfile_conventional_avx', ATTEMPTS, dataset, conv_small_bitstream_path)

        if not args.no_cuda:
            throughput['recoil_cuda'] = run_decoding_experiment(
                'decode_textfile_cuda', ATTEMPTS, dataset, recoil_large_bitstream_path)
            throughput['conv_cuda'] = run_decoding_experiment(
                'decode_textfile_conventional_cuda', ATTEMPTS, dataset, conv_large_bitstream_path)

            logger.info(f"Running multians")

            compression['multians'], throughput['multians'] = run_multians(ATTEMPTS, dataset)

        throughput_csv_writer.writerow(throughput.values())
        compression_csv_writer.writerow(compression.values())

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