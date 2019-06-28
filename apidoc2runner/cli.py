import argparse
import logging
import sys

from apidoc2runner import __version__
from apidoc2runner.core import apidocParser


def main():
    parser = argparse.ArgumentParser(
        description="Convert apidoc testcases to JSON testcases for HttpRunner.")
    parser.add_argument("-V", "--version", dest='version', action='store_true',
        help="show version")
    parser.add_argument('--log-level', default='INFO',
        help="Specify logging level, default is INFO.")

    parser.add_argument('apidoc_testset_file', nargs='?',
        help="Specify apidoc testset file.")

    parser.add_argument('--output_file_type', nargs='?',
        help="Optional. Specify output file type.")

    parser.add_argument('--output_dir', nargs='?',
        help="Optional. Specify output directory.")

    args = parser.parse_args()

    if args.version:
        print("{}".format(__version__))
        exit(0)

    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(level=log_level)

    apidoc_testset_file = args.apidoc_testset_file
    output_file_type = args.output_file_type
    output_dir = args.output_dir

    if not apidoc_testset_file or not apidoc_testset_file.endswith(".json"):
        logging.error("apidoc_testset_file file not specified.")
        sys.exit(1)
    
    if not output_file_type:
        output_file_type = "json"
    else:
        output_file_type = output_file_type.lower()
    if output_file_type not in ["json", "yml", "yaml"]:
        logging.error("output file only support json/yml/yaml.")
        sys.exit(1)
    
    if not output_dir:
        output_dir = '.'

    # 读取apidoc文件
    apidoc_parser = apidocParser(apidoc_testset_file)
    # 解析文件
    parse_result = apidoc_parser.parse_data()
    # 保存文件
    apidoc_parser.save(parse_result, output_dir, output_file_type=output_file_type)

    return 0







