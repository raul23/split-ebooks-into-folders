"""Splits the supplied ebook files (and the accompanying metadata files if
present) into folders with consecutive names where each contains the specified
number of files.

This is a Python port of `split-into-folders.sh` from `ebook-tools` written
in shell by `na--`.

Ref.: https://github.com/na--/ebook-tools
"""
import argparse
import logging
import os

from split_into_folders import __version__
from split_into_folders.lib import (namespace_to_dict, setup_log, split, blue,
                                    green, red, yellow, OUTPUT_METADATA_EXTENSION,
                                    FILES_PER_FOLDER, FOLDER_PATTERN, START_NUMBER,
                                    LOGGING_FORMATTER, LOGGING_LEVEL)

# import ipdb

logger = logging.getLogger('split_script')

# =====================
# Default config values
# =====================

# Misc options
# ============
QUIET = False
OUTPUT_FILE = 'output.txt'


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        print_(self.format_usage().splitlines()[0])
        self.exit(2, red(f'\nerror: {message}\n'))


class MyFormatter(argparse.HelpFormatter):
    """
    Corrected _max_action_length for the indenting of subactions
    """

    def add_argument(self, action):
        if action.help is not argparse.SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            current_indent = self._current_indent
            for subaction in self._iter_indented_subactions(action):
                # compensate for the indent that will be added
                indent_chg = self._current_indent - current_indent
                added_indent = 'x' * indent_chg
                invocations.append(added_indent + get_invocation(subaction))
            # print_('inv', invocations)

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    # Ref.: https://stackoverflow.com/a/23941599/14664104
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    # parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)


class OptionsChecker:
    def __init__(self, add_opts, remove_opts):
        self.add_opts = init_list(add_opts)
        self.remove_opts = init_list(remove_opts)

    def check(self, opt_name):
        return not self.remove_opts.count(opt_name) or \
               self.add_opts.count(opt_name)


class Result:
    def __init__(self, stdout='', stderr='', returncode=None, args=None):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.args = args

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'stdout={str(self.stdout).strip()}, ' \
               f'stderr={str(self.stderr).strip()}, ' \
               f'returncode={self.returncode}, args={self.args}'


# Options related to the input and output files
def add_input_output_options(parser, remove_opts=None, add_as_group=True):
    remove_opts = init_list(remove_opts)
    if add_as_group:
        parser_input_output = parser.add_argument_group(
            title='Options related to the output files')
    else:
        parser_input_output = parser
    if not remove_opts.count('output-filename-template'):
        parser_input_output.add_argument(
            '--oft', '--output-filename-template', dest='output_filename_template',
            metavar='TEMPLATE',
            help='''This specifies how the filenames of the organized files will
            look. It is a bash string that is evaluated so it can be very flexible
            (and also potentially unsafe).''' +
                 get_default_message(OUTPUT_FILENAME_TEMPLATE))
    if not remove_opts.count('output-metadata-extension'):
        parser_input_output.add_argument(
            '--ome', '--output-metadata-extension', dest='output_metadata_extension',
            metavar='EXTENSION',
            help='''If `keep_metadata` is enabled, this is the extension of the
            additional metadata file that is saved next to each newly renamed file.'''
                 + get_default_message(OUTPUT_METADATA_EXTENSION))
    return parser_input_output


# General options
def add_general_options(parser, add_opts=None, remove_opts=None,
                        program_version=__version__,
                        title='General options'):
    checker = OptionsChecker(add_opts, remove_opts)
    parser_general_group = parser.add_argument_group(title=title)
    if checker.check('help'):
        parser_general_group.add_argument('-h', '--help', action='help',
                                          help='Show this help message and exit.')
    if checker.check('version'):
        parser_general_group.add_argument(
            '-v', '--version', action='version',
            version=f'%(prog)s v{program_version}',
            help="Show program's version number and exit.")
    if checker.check('quiet'):
        parser_general_group.add_argument(
            '-q', '--quiet', action='store_true',
            help='Enable quiet mode, i.e. nothing will be printed.')
    if checker.check('verbose'):
        parser_general_group.add_argument(
            '--verbose', action='store_true',
            help='Print various debugging information, e.g. print traceback '
                 'when there is an exception.')
    if checker.check('dry-run'):
        parser_general_group.add_argument(
            '-d', '--dry-run', dest='dry_run', action='store_true',
            help='If this is enabled, no file rename/move/symlink/etc. '
                 'operations will actually be executed.')
    # TODO: implement more sort options, e.g. random sort
    if checker.check('reverse'):
        parser_general_group.add_argument(
            '-r', '--reverse', dest='reverse', action='store_true',
            help='If this is enabled, the files will be sorted in reverse (i.e. '
                 'descending) order. By default, they are sorted in ascending '
                 'order.')
    if checker.check('log-level'):
        parser_general_group.add_argument(
            '--log-level', dest='logging_level',
            choices=['debug', 'info', 'warning', 'error'], default=LOGGING_LEVEL,
            help='Set logging level.' + get_default_message(LOGGING_LEVEL))
    if checker.check('log-format'):
        parser_general_group.add_argument(
            '--log-format', dest='logging_formatter',
            choices=['console', 'only_msg', 'simple',], default=LOGGING_FORMATTER,
            help='Set logging formatter.' + get_default_message(LOGGING_FORMATTER))
    return parser_general_group


# Ref.: https://stackoverflow.com/a/14117511/14664104
def check_positive(value):
    try:
        # TODO: 2.0 rejected
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} is an invalid positive int value")
    else:
        return ivalue


def get_default_message(default_value):
    return green(f' (default: {default_value})')


def init_list(list_):
    return [] if list_ is None else list_


def print_(msg):
    global QUIET
    if not QUIET:
        print(msg)


def setup_argparser():
    width = os.get_terminal_size().columns - 5
    name_input = 'folder_with_books'
    name_output = 'output_folder'
    usage_msg = blue(f'%(prog)s [OPTIONS] {{{name_input}}} [{{{name_output}}}]')
    desc_msg = 'Split the supplied ebook files (and the accompanying metadata' \
               'files if present) into folders with consecutive names that each ' \
               'contain the specified number of files.\n' \
               'This script is based on the great ebook-tools written in shell ' \
               'by na-- (See https://github.com/na--/ebook-tools).'
    parser = ArgumentParser(
        description="",
        usage=f"{usage_msg}\n\n{desc_msg}",
        add_help=False,
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=50, width=width))
    general_group = add_general_options(
        parser,
        remove_opts=[],
        program_version=__version__,
        title=yellow('General options'))
    # =============
    # Split options
    # =============
    split_group = parser.add_argument_group(title=yellow('Split options'))
    split_group.add_argument(
        '-s', '--start-number', dest='start_number', type=int, default=START_NUMBER,
        help='The number of the first folder.'
             + get_default_message(START_NUMBER))
    # TODO: important explain why we don't use default arg in add_argument()
    split_group.add_argument(
        '-f', '--folder-pattern', dest='folder_pattern', metavar='PATTERN',
        default=FOLDER_PATTERN,
        help='''The print format string that specifies the pattern with which
            new folders will be created. By default it creates folders like
            00000000, 00001000, 00002000, .....'''
             + get_default_message(FOLDER_PATTERN).replace('%', '%%'))
    split_group.add_argument(
        '--fpf', '--files-per-folder', dest='files_per_folder',
        default=FILES_PER_FOLDER, type=check_positive,
        help='''How many files should be moved to each folder.'''
             + get_default_message(FILES_PER_FOLDER))
    # ====================
    # Input/Output options
    # ====================
    input_output_files_group = parser.add_argument_group(
        title=yellow('Input and output options'))
    input_output_files_group.add_argument(
        '--ome', '--output-metadata-extension', dest='output_metadata_extension',
        metavar='EXTENSION', default=OUTPUT_METADATA_EXTENSION,
        help=''' This is the extension of the metadata file associated with
        an ebook.''' + get_default_message(OUTPUT_METADATA_EXTENSION))
    input_output_files_group.add_argument(
        name_input,
        help='''Folder with books which will be recursively scanned for files.
                The found files (and the accompanying metadata files if present) will
                be split into folders with consecutive names that each contain the
                specified number of files.''')
    input_output_files_group.add_argument(
        '-o', '--output-folder', dest=name_output, metavar='PATH',
        default=os.getcwd(),
        help='''The output folder in which all the new consecutively named
                folders will be created. The default value is the current working
                directory.''' + get_default_message(os.getcwd()))
    return parser


def show_exit_code(exit_code):
    msg = f'Program exited with {exit_code}'
    if exit_code == 1:
        logger.error(red(f'{msg}'))
    else:
        logger.debug(msg)


def main():
    global QUIET
    try:
        parser = setup_argparser()
        args = parser.parse_args()
        QUIET = args.quiet
        setup_log(args.quiet, args.verbose, args.logging_level, args.logging_formatter)
        # Actions
        error = False
        args_dict = namespace_to_dict(args)
        exit_code = split(**args_dict)
    except KeyboardInterrupt:
        print_(yellow('\nProgram stopped!'))
        exit_code = 2
    except Exception as e:
        print_(yellow('Program interrupted!'))
        logger.exception(e)
        exit_code = 1
    if __name__ != '__main__':
        show_exit_code(exit_code)
    return exit_code


if __name__ == '__main__':
    retcode = main()
    show_exit_code(retcode)
