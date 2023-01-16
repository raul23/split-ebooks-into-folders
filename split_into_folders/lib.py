import logging
import math
import os
import shutil
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from split_into_folders import __version__

# import ipdb

logger = logging.getLogger('split_lib')
logger.setLevel(logging.CRITICAL + 1)


# =====================
# Default config values
# =====================

# Misc options
DRY_RUN = False
REVERSE = False

# Input/Output options
# ====================
OUTPUT_FILENAME_TEMPLATE = "${d[AUTHORS]// & /, } - ${d[SERIES]:+[${d[SERIES]}] " \
                           "- }${d[TITLE]/:/ -}${d[PUBLISHED]:+ (${d[PUBLISHED]%%-*})}" \
                           "${d[ISBN]:+ [${d[ISBN]}]}.${d[EXT]}"
# This is the extension of the additional metadata file that is saved next to
# each newly renamed file
OUTPUT_METADATA_EXTENSION = 'meta'

# Split options
# =============
FILES_PER_FOLDER = 1000
FOLDER_PATTERN = '%05d000'
START_NUMBER = 0

# Logging options
# ===============
LOGGING_FORMATTER = 'only_msg'
LOGGING_LEVEL = 'info'

# ------
# Colors
# ------
COLORS = {
    'GREEN': '\033[0;36m',  # 32
    'RED': '\033[0;31m',
    'YELLOW': '\033[0;33m',  # 32
    'BLUE': '\033[0;34m',  #
    'VIOLET': '\033[0;35m',  #
    'BOLD': '\033[1m',
    'NC': '\033[0m',
}
_COLOR_TO_CODE = {
    'g': COLORS['GREEN'],
    'r': COLORS['RED'],
    'y': COLORS['YELLOW'],
    'b': COLORS['BLUE'],
    'v': COLORS['VIOLET'],
    'bold': COLORS['BOLD']
}


def color(msg, msg_color='y', bold_msg=False):
    msg_color = msg_color.lower()
    colors = list(_COLOR_TO_CODE.keys())
    assert msg_color in colors, f'Wrong color: {msg_color}. Only these ' \
                                f'colors are supported: {msg_color}'
    msg = bold(msg) if bold_msg else msg
    msg = msg.replace(COLORS['NC'], COLORS['NC']+_COLOR_TO_CODE[msg_color])
    return f"{_COLOR_TO_CODE[msg_color]}{msg}{COLORS['NC']}"


def blue(msg):
    return color(msg, 'b')


def bold(msg):
    return color(msg, 'bold')


def green(msg):
    return color(msg, 'g')


def red(msg):
    return color(msg, 'r')


def violet(msg):
    return color(msg, 'v')


def yellow(msg):
    return color(msg)


def mkdir(path):
    # Since path can be relative to the cwd
    path = os.path.abspath(path)
    dirname = os.path.basename(path)
    if os.path.exists(path):
        logger.debug(f"Folder already exits: {path}")
        logger.debug(f"Skipping it!")
    else:
        logger.debug(f"Creating folder '{dirname}': {path}")
        os.mkdir(path)
        logger.debug("Folder created!")


def move(src, dst, clobber=True):
    # TODO: necessary?
    # Since path can be relative to the cwd
    # src = os.path.abspath(src)
    # filename = os.path.basename(src)
    src = Path(src)
    dst = Path(dst)
    if dst.exists():
        logger.debug(f'{dst.name}: file already exists')
        logger.debug(f"Destination folder path: {dst.parent}")
        if clobber:
            logger.debug(f'{dst.name}: overwriting the file')
            shutil.move(src, dst)
            logger.debug("File moved!")
        else:
            logger.debug(f'{dst.name}: cannot overwrite existing file')
            logger.debug(f"Skipping it!")
    else:
        logger.debug(f"Moving '{src.name}'...")
        logger.debug(f"Destination folder path: {dst.parent}")
        shutil.move(src, dst)
        logger.debug("File moved!")


def namespace_to_dict(ns):
    namspace_classes = [Namespace, SimpleNamespace]
    # TODO: check why not working anymore
    # if isinstance(ns, SimpleNamespace):
    if type(ns) in namspace_classes:
        adict = vars(ns)
    else:
        adict = ns
    for k, v in adict.items():
        # if isinstance(v, SimpleNamespace):
        if type(v) in namspace_classes:
            v = vars(v)
            adict[k] = v
        if isinstance(v, dict):
            namespace_to_dict(v)
    return adict


def setup_log(quiet=False, verbose=False, logging_level=LOGGING_LEVEL,
              logging_formatter=LOGGING_FORMATTER):
    if not quiet:
        for logger_name in ['split_script', 'split_lib']:
            logger_ = logging.getLogger(logger_name)
            if verbose:
                logger_.setLevel('DEBUG')
            else:
                logging_level = logging_level.upper()
                logger_.setLevel(logging_level)
            # Create console handler and set level
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            # Create formatter
            if logging_formatter:
                formatters = {
                    'console': '%(name)-10s | %(levelname)-8s | %(message)s',
                    # 'console': '%(asctime)s | %(levelname)-8s | %(message)s',
                    'only_msg': '%(message)s',
                    'simple': '%(levelname)-8s %(message)s',
                    'verbose': '%(asctime)s | %(name)-10s | %(levelname)-8s | %(message)s'
                }
                formatter = logging.Formatter(formatters[logging_formatter])
                # Add formatter to ch
                ch.setFormatter(formatter)
            # Add ch to logger
            logger_.addHandler(ch)
        # =============
        # Start logging
        # =============
        logger.debug("Running {} v{}".format(__file__, __version__))
        logger.debug("Verbose option {}".format("enabled" if verbose else "disabled"))


def split(folder_with_books,
          output_folder=os.getcwd(),
          dry_run=DRY_RUN,
          files_per_folder=FILES_PER_FOLDER,
          folder_pattern=FOLDER_PATTERN,
          output_metadata_extension=OUTPUT_METADATA_EXTENSION,
          reverse=REVERSE,
          start_number=START_NUMBER,
          **kwargs):
    if not Path(output_folder).exists():
        msg = red("Output folder doesn't exist: ")
        logger.error(f'{msg} {output_folder}')
        return 1
    files = []
    for fp in Path(folder_with_books).rglob('*'):
        # File extension
        ext = fp.suffix.split('.')[-1]
        # Ignore directory, metadata and hidden files
        if Path.is_file(fp) and ext != output_metadata_extension and \
                not fp.name.startswith('.'):
            # TODO: debug logging
            # print(fp)
            files.append(fp)
        # TODO: debug logging skip directory/file
    # TODO: important sort within glob?
    logger.info("Files sorted {}".format("in desc" if reverse else "in asc"))
    files.sort(key=lambda x: x.name, reverse=reverse)
    current_folder_num = start_number
    start_index = 0
    # Get width of zeros for folder format pattern
    left, right = folder_pattern.split('%')[-1].split('d')
    width = int(left) + len(right)
    total_files = len(files)
    logger.info(f"Total number of files to be split into folders: {total_files}")
    logger.info(f"Number of files per folder: {files_per_folder}")
    number_splits = math.ceil(total_files / files_per_folder)
    logger.info(f"Number of splits: {number_splits}")
    logger.info("Starting splits...")
    while True:
        if start_index >= len(files):
            # TODO: debug logging
            logger.info(f"End of splits!")
            break
        chunk = files[start_index:start_index+files_per_folder]
        start_index += files_per_folder
        logger.debug(f"Found {len(chunk)} files...")
        current_folder_basename = '{0:0{width}}'.format(
            current_folder_num, width=width)
        current_folder = os.path.join(output_folder, current_folder_basename)
        current_folder_metadata = os.path.join(
            output_folder, current_folder_basename + '.' + output_metadata_extension)
        current_folder_num += 1
        if dry_run:
            logger.debug(f"Creating folder '{current_folder}'...")
        else:
            mkdir(current_folder)
        for file_to_move in chunk:
            # TODO: important, explain that files skipped if already exist (not overwritten)
            file_dest = os.path.join(current_folder, file_to_move.name)
            if dry_run:
                logger.debug(f"Moving file '{file_to_move}'...")
            else:
                move(file_to_move, file_dest, clobber=False)
            # Move metadata file if found
            # TODO: important, extension of metadata (other places too)
            # metadata_name = f'{file_to_move.stem}.{output_metadata_extension}'
            metadata_name = f'{file_to_move.name}.{output_metadata_extension}'
            metada_file_to_move = file_to_move.parent.joinpath(metadata_name)
            if metada_file_to_move.exists():
                logger.debug(f"Found metadata file: {metada_file_to_move}")
                # Create metadata folder only if there is at least a
                # metadata file
                if dry_run:
                    logger.debug(f"Creating folder '{current_folder_metadata}'...")
                    logger.debug(f"Moving file '{metadata_name}'...")
                else:
                    mkdir(current_folder_metadata)
                    metadata_dest = os.path.join(current_folder_metadata,
                                                 metadata_name)
                    move(metada_file_to_move, metadata_dest, clobber=False)
    return 0

