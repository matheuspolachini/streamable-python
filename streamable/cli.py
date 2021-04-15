#!/usr/bin/env python3
"""
streamable - command line utility for interacting with streamable.com
"""


import sys
import os.path
import argparse
import pyperclip
from getpass import getpass

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from streamable.client import StreamableClient
from streamable.errors import UserNotFoundError, IncorrectPasswordError


def make_argparser():
    parser = argparse.ArgumentParser(description="Interact With Streamable")

    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + metadata.version('streamable'))

    subparsers = parser.add_subparsers(dest='action', required=True)

    parser_upload = subparsers.add_parser('upload', help='Upload a video')
    parser_upload.add_argument('file', type=lambda file: is_valid_file(
        parser_upload, file), help='File to be uploaded')
    parser_upload.add_argument('-t', '--title', type=str, help='Video title')
    parser_upload.add_argument('-u', '--user', type=str,
                               help='Streamable username. If not provided, the upload will be anonymous')
    parser_upload.add_argument('-p', '--password', type=str,
                               help='Streamable password. If not provided and user is provided, it will prompt for the password')
    parser_upload.add_argument('-c', '--clipboard', action='store_true',
                               help='Copy video url to clipboard after upload')

    return parser


def is_valid_file(parser, file):
    if not os.path.exists(file):
        parser.error(f'File {file} does not exist')

    return file


def handle_login(client, user, password):
    if user is None:
        return

    if password is None:
        password = getpass()

    try:
        client.login(user, password)
    except UserNotFoundError:
        print(f'User not found')
        sys.exit(1)
    except IncorrectPasswordError:
        print('Incorrect password')
        sys.exit(2)
    except:
        print('An error ocurred during login')
        sys.exit(3)


def get_default_title(file):
    return os.path.splitext(os.path.basename(file))[0]


def main():
    parser = make_argparser()
    args = parser.parse_args()

    client = StreamableClient()
    handle_login(client, args.user, args.password)

    title = args.title or get_default_title(args.file)

    print(f'Uploading file {args.file}')

    result = client.upload(args.file, title=title)

    shortcode = result['shortcode']
    url = result['url']

    print(f'Shortcode: {shortcode}. URL: {url}')

    if args.clipboard:
        pyperclip.copy(url)
        print(f'URL copied to clipboard')


if __name__ == '__main__':
    main()
