from loguru import logger
from cpufeature import CPUFeature
from subprocess import CalledProcessError

from run_experiments import *
from config import *


def detect_cpu():
    # If AVX is not supported on this platform, then we'll skip the AVX tests
    avx_version = None
    if CPUFeature['AVX512f']:
        avx_version = 512
    elif CPUFeature['AVX2']:
        avx_version = 2

    core_count = CPUFeature['num_physical_cores']

    return core_count, avx_version


def detect_cuda_occupancy():
    try:
        return run_program(get_program_path(11, 2, 'detect_cuda_occupancy'), [])['occupancy']
    except CalledProcessError as e:
        logger.error("Detecting CUDA max occupancy failed: " + str(e.stderr))
        return None
    except FileNotFoundError:
        logger.error("CUDA max occupancy detect program is not found")
        return None
