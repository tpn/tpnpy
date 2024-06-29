#===============================================================================
# Imports
#===============================================================================
from math import floor

from .util import (
    SlotObject,
    is_power_of_2,
)

#===============================================================================
# Globals
#===============================================================================

DEFAULT_BLOCK_SIZE = 65536

#===============================================================================
# Classes
#===============================================================================

class Dd(SlotObject):
    __slots__ = [
        'bs',
        'skip',
        'seek',
        'count',
        'skipped_bytes',
        'seeked_bytes',
        'total_bytes',
    ]
    def __init__(self, bs, skip, seek, count):
        self.bs = int(bs)
        self.skip = int(skip)
        self.seek = int(seek)
        self.count = int(count)
        self.skipped_bytes = self.skip * self.count
        self.seeked_bytes = self.seek * self.count
        self.total_bytes = self.bs * self.count

    @classmethod
    def slice_blocks(cls, size, count):
        from math import floor
        block_size = floor(size / count)
        remainder = size - (block_size * count)
        blocks = [ block_size for _ in range(count) ]
        blocks[-1] += remainder
        return blocks

#===============================================================================
# Functions
#===============================================================================

def slice_blocks(size, count):
    block_size = floor(size / count)
    remainder = size - (block_size * count)
    blocks = [ block_size for _ in range(count) ]
    blocks[-1] += remainder
    return blocks

def get_dds(total_bytes, num_procs, block_size=65536, min_block_size=4096):
    assert min_block_size < block_size, (min_block_size, block_size)
    assert min_block_size > 0, (min_block_size)
    assert is_power_of_2(min_block_size), (min_block_size)
    assert block_size % min_block_size == 0

    remaining_bytes = total_bytes % block_size
    parallel_bytes = total_bytes - remaining_bytes

    is_perfect_fit = (remaining_bytes == 0)
    if is_perfect_fit:
        actual_procs = num_procs
        remaining_block_count = 0
        remaining_block_multiplier = 0
    else:
        actual_procs = num_procs + 1
        assert remaining_bytes % min_block_size == 0, (remaining_bytes % min_block_size)
        remaining_block_count = remaining_bytes / min_block_size
        remaining_block_multiplier = block_size / min_block_size

    assert actual_procs >= 1, actual_procs

    parallel_block_count = parallel_bytes / block_size
    slices = slice_blocks(parallel_block_count, num_procs)
    assert len(slices) == num_procs, (len(slices), num_procs)

    dds = list()
    start = 0
    end = 0
    for (i, slice) in enumerate(slices):
        if i == 0:
            offset = 0
        else:
            offset = sum(slices[:i])
        count = slices[i]
        dd = Dd(
            bs=block_size,
            skip=offset,
            seek=offset,
            count=count,
        )
        dds.append(dd)

    if not is_perfect_fit:
        offset = sum(slices)
        dd = Dd(
            bs=min_block_size,
            skip=offset,
            seek=offset,
            count=remaining_block_count
        )
        dds.append(dd)

    total_check = sum(dd.total_bytes for dd in dds)
    assert total_bytes == total_check, (total_bytes, total_check)

    return dds

def convert_dd_to_command(dd, input_file, output_file):
    cmd = (
        f'dd if={input_file} of={output_file} '
        f'bs={dd.bs} skip={dd.skip} seek={dd.seek} '
        f'count={dd.count} conv=noerror,sync status=progress &'
    )
    return cmd

def get_dd_commands(total_size_in_bytes, num_procs, src, dst):
    dds = get_dds(total_size_in_bytes, num_procs)
    lines = [
        convert_dd_to_command(dd, src, dst) for dd in dds
    ]
    return '\n'.join(lines)

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
