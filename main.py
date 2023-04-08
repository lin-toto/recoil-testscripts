from detect_system import *
from run_experiments import *
from loguru import logger
import tempfile
import shutil


ATTEMPTS = 10


def main(workdir: str):
    num_cpu_threads, avx_version = detect_cpu()
    logger.info(f"Core Count: {num_cpu_threads}, AVX: {avx_version}")

    cuda_occupancy = detect_cuda_occupancy()
    logger.info(f"CUDA max occupancy: {cuda_occupancy}")

    for dataset in TEXT_DATASETS:
        logger.info(f"Start Recoil experiment on dataset {dataset}")

        large_bitstream_path = os.path.join(workdir, dataset + '_large.bin')
        small_bitstream_path = os.path.join(workdir, dataset + '_small.bin')

        dataset_size, large_encoded_size = run_encoding('encode_textfile', dataset, cuda_occupancy, large_bitstream_path)
        small_encoded_size = run_splits_combine(dataset, large_bitstream_path, num_cpu_threads, small_bitstream_path)
        logger.info(f"Dataset size: {dataset_size}, large encoded size: {large_encoded_size}, combined small encoded size: {small_encoded_size}")

        run_decoding_experiment('decode_textfile_cuda', ATTEMPTS, dataset, large_bitstream_path, large_bitstream_path + '.cdf')
        run_decoding_experiment('decode_textfile_avx', ATTEMPTS, dataset, small_bitstream_path, large_bitstream_path + '.cdf')


        logger.info(f"Start Conventional Method experiment on dataset {dataset}")

        large_bitstream_path = os.path.join(workdir, dataset + '_large_conventional.bin')
        small_bitstream_path = os.path.join(workdir, dataset + '_small_conventional.bin')

        dataset_size, large_encoded_size = run_encoding('encode_textfile_conventional', dataset, cuda_occupancy, large_bitstream_path)
        _, small_encoded_size = run_encoding('encode_textfile_conventional', dataset, num_cpu_threads, small_bitstream_path)
        logger.info(f"Dataset size: {dataset_size}, large encoded size: {large_encoded_size}, small encoded size: {small_encoded_size}")

        run_decoding_experiment('decode_textfile_conventional_cuda', ATTEMPTS, dataset, large_bitstream_path, large_bitstream_path + '.cdf')
        run_decoding_experiment('decode_textfile_conventional_avx', ATTEMPTS, dataset, small_bitstream_path, small_bitstream_path + '.cdf')




if __name__ == '__main__':
    workdir = tempfile.mkdtemp()
    logger.info(f"Created temporary working directory at {workdir}")
    try:
        main(workdir)
    finally:
        logger.info(f"Cleaning up {workdir}")
        shutil.rmtree(workdir)