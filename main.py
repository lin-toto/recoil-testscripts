from detect_system import *
from run_experiments import *
from loguru import logger
import tempfile
import shutil
import csv

ATTEMPTS = 10

def main(workdir: str):
    num_cpu_threads, avx_version = detect_cpu()
    logger.info(f"Core Count: {num_cpu_threads}, AVX: {avx_version}")

    cuda_occupancy = detect_cuda_occupancy()
    logger.info(f"CUDA max occupancy: {cuda_occupancy}")

    logger.info(f"Opening throughput.csv and compression.csv for writing")
    throughput_csv = open('throughput.csv', 'w')
    compression_csv = open('compression.csv', 'w')
    throughput_csv_writer = csv.writer(throughput_csv)
    compression_csv_writer = csv.writer(compression_csv)
    throughput_csv_writer.writerow(['', f'Interleaved rANS AVX{avx_version}', 'Recoil CUDA', f"Recoil AVX{avx_version}", "Conventional CUDA", f"Conventional AVX{avx_version}", "multians"])
    compression_csv_writer.writerow(['', 'Uncompressed Size', 'Interleaved rANS', 'Recoil Large', 'Recoil Small', 'Conventional Large', 'Conventional Small', 'multians'])

    logger.info(f"Using {cuda_occupancy} splits for Recoil encoding, then combining to {num_cpu_threads} splitss")

    for dataset in TEXT_DATASETS:
        logger.info(f"Start Recoil experiment on dataset {dataset}")

        rans_bitstream_path = os.path.join(workdir, dataset + '.bin')

        dataset_size, rans_encoded_size = run_encoding('encode_textfile', dataset, 1, rans_bitstream_path)
        logger.info(f"Dataset size: {dataset_size}, rANS encoded size: {rans_encoded_size}")
        rans_avx_throughput = run_decoding_experiment('decode_textfile_avx', ATTEMPTS, dataset, rans_bitstream_path, rans_bitstream_path + '.cdf')


        large_bitstream_path = os.path.join(workdir, dataset + '_large.bin')
        small_bitstream_path = os.path.join(workdir, dataset + '_small.bin')

        _, large_encoded_size = run_encoding('encode_textfile', dataset, cuda_occupancy, large_bitstream_path)
        small_encoded_size = run_splits_combine(dataset, large_bitstream_path, num_cpu_threads, small_bitstream_path)
        logger.info(f"Recoil large encoded size: {large_encoded_size}, Recoil combined small encoded size: {small_encoded_size}")

        recoil_cuda_throughput = run_decoding_experiment('decode_textfile_cuda', ATTEMPTS, dataset, large_bitstream_path, large_bitstream_path + '.cdf')
        recoil_avx_throughput = run_decoding_experiment('decode_textfile_avx', ATTEMPTS, dataset, small_bitstream_path, large_bitstream_path + '.cdf')


        logger.info(f"Start Conventional Method experiment on dataset {dataset}")

        large_bitstream_path = os.path.join(workdir, dataset + '_large_conventional.bin')
        small_bitstream_path = os.path.join(workdir, dataset + '_small_conventional.bin')

        _, conv_large_encoded_size = run_encoding('encode_textfile_conventional', dataset, cuda_occupancy, large_bitstream_path)
        _, conv_small_encoded_size = run_encoding('encode_textfile_conventional', dataset, num_cpu_threads, small_bitstream_path)
        logger.info(f"Conventional large encoded size: {conv_large_encoded_size}, Conventional small encoded size: {conv_small_encoded_size}")

        conv_cuda_throughput = run_decoding_experiment('decode_textfile_conventional_cuda', ATTEMPTS, dataset, large_bitstream_path, large_bitstream_path + '.cdf')
        conv_avx_throughput = run_decoding_experiment('decode_textfile_conventional_avx', ATTEMPTS, dataset, small_bitstream_path, small_bitstream_path + '.cdf')

        # TODO: multians


        throughput_csv_writer.writerow([dataset, rans_avx_throughput, recoil_cuda_throughput, recoil_avx_throughput, conv_cuda_throughput, conv_avx_throughput])
        compression_csv_writer.writerow([dataset, dataset_size, rans_encoded_size, large_encoded_size, small_encoded_size, conv_large_encoded_size, conv_small_encoded_size])

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