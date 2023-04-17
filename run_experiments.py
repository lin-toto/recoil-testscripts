import subprocess
import json
import os
from typing import List
from loguru import logger
from config import *


def get_program_path(key: str) -> str:
    return os.path.join(EXECUTABLE_ROOT, EXECUTABLES[key])

def run_program(executable: str, args: List[str]) -> dict:
    output = subprocess.check_output([executable] + args).strip()
    if not output:
        return dict()
    else:
        return json.loads(output)


def run_encoding(encoder_name: str, dataset_name: str, n_splits: int, bitstream_file: str):
    executable = get_program_path(encoder_name)
    dataset_path = os.path.join(DATASET_ROOT, dataset_name)

    logger.info(f"Using {encoder_name} to encode {dataset_name} into {n_splits} splits")
    run_program(executable, [dataset_path, str(n_splits), bitstream_file])
    logger.info(f"Encoded {os.path.getsize(dataset_path)} bytes into {os.path.getsize(bitstream_file)} bytes")
    return os.path.getsize(dataset_path), os.path.getsize(bitstream_file)


def run_lic_encoding(encoder_name: str, dataset_name: str, n_splits: int, bitstream_file: str):
    executable = get_program_path(encoder_name)
    dataset_path = os.path.join(DATASET_ROOT, dataset_name + ".txt")
    indexes_path = os.path.join(DATASET_ROOT, dataset_name + "_indexes.txt")

    logger.info(f"Using {encoder_name} to encode {dataset_name} into {n_splits} splits")
    result = run_program(executable, [dataset_path, indexes_path, MBT2018_CDF, str(n_splits), bitstream_file])
    logger.info(f"Encoded {result['original_size_bytes']} bytes into {os.path.getsize(bitstream_file)} bytes")
    return result['original_size_bytes'], os.path.getsize(bitstream_file)

def run_splits_combine(dataset_name: str, bitstream_file: str, n_splits: int, new_bitstream_file: str):
    executable = get_program_path('combine_encoded_splits')

    logger.info(f"Combine encoded {dataset_name} into {n_splits} splits")
    run_program(executable, [bitstream_file, str(n_splits), new_bitstream_file])
    logger.info(f"Reduced {os.path.getsize(bitstream_file)} bytes into {os.path.getsize(new_bitstream_file)} bytes")
    return os.path.getsize(new_bitstream_file)


def run_decoding_experiment(experiment_name: str, attempts: int, dataset_name: str, bitstream_file: str, cdf_file: str = None):
    executable = get_program_path(experiment_name)
    dataset_path = os.path.join(DATASET_ROOT, dataset_name)
    if cdf_file is None:
        cdf_file = bitstream_file + ".cdf"

    logger.info(f"Running {experiment_name} on {dataset_name} for {attempts} attempts")

    sum_elapsed = 0
    original_size_bytes = 0
    for i in range(attempts):
        result = run_program(executable, [bitstream_file, cdf_file, dataset_path])
        original_size_bytes = result['original_size_bytes']

        if result['result_correct']:
            logger.info(f"Decode {i+1}/{attempts}: {result['throughput_mb']} MB/s")
        else:
            logger.error(f"Decode {i+1}/{attempts}: {result['throughput_mb']} MB/s, result INCORRECT")

        sum_elapsed += result['time']

    average_throughput = (original_size_bytes * attempts / (1024 * 1024)) / (sum_elapsed / 1000000)
    logger.info(f"Average throughput: {average_throughput} MB/s")
    return average_throughput


def run_lic_decoding_experiment(experiment_name: str, attempts: int, dataset_name: str, bitstream_file: str, cdf_file: str = None):
    executable = get_program_path(experiment_name)
    dataset_path = os.path.join(DATASET_ROOT, dataset_name + ".txt")
    indexes_path = os.path.join(DATASET_ROOT, dataset_name + "_indexes.txt")

    logger.info(f"Running {experiment_name} on {dataset_name} for {attempts} attempts")

    sum_elapsed = 0
    original_size_bytes = 0
    for i in range(attempts):
        result = run_program(executable, [bitstream_file, indexes_path, MBT2018_CDF, dataset_path])
        original_size_bytes = result['original_size_bytes']

        if result['result_correct']:
            logger.info(f"Decode {i+1}/{attempts}: {result['throughput_mb']} MB/s")
        else:
            logger.error(f"Decode {i+1}/{attempts}: {result['throughput_mb']} MB/s, result INCORRECT")

        sum_elapsed += result['time']

    average_throughput = (original_size_bytes * attempts / (1024 * 1024)) / (sum_elapsed / 1000000)
    logger.info(f"Average throughput: {average_throughput} MB/s")
    return average_throughput


def run_multians(attempts: int, dataset_name: str):
    executable = MULTIANS
    dataset_path = os.path.join(DATASET_ROOT, dataset_name)

    logger.info(f"Running multians on {dataset_name} for {attempts} attempts")

    sum_elapsed = 0
    original_size_bytes = 0
    compressed_size_bytes = 0
    for i in range(attempts):
        result = run_program(executable, ["0", "1", "1", dataset_path])
        if i == 0:
            original_size_bytes = result['original_size_bytes']
            compressed_size_bytes = result['compressed_size_bytes']
            logger.info(f"Encoded {result['original_size_bytes']} bytes into {result['compressed_size_bytes']} bytes")

        if result['result_correct']:
            logger.info(f"Decode {i + 1}/{attempts}: {result['throughput_mb']} MB/s")
        else:
            logger.error(f"Decode {i + 1}/{attempts}: {result['throughput_mb']} MB/s, result INCORRECT")

        sum_elapsed += result['time']

    average_throughput = (original_size_bytes * attempts / (1024 * 1024)) / (sum_elapsed / 1000000)
    logger.info(f"Average throughput: {average_throughput} MB/s")
    return compressed_size_bytes, average_throughput
