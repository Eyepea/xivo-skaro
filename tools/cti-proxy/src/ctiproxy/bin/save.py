# -*- coding: UTF-8 -*-

import argparse
import sys
from ctiproxy import core
from ctiproxy.bin import common


def _new_argument_parser():
    common_parser = common.new_argument_parser()
    parser = argparse.ArgumentParser(parents=[common_parser])
    parser.add_argument("-s", "--strip", action="append",
                        help="strip the given fields from messages")
    parser.add_argument("-i", "--include", action="store",
                        help="include only the given messages")
    parser.add_argument("clientfile",
                        help="file to save client messages")
    parser.add_argument("serverfile",
                        help="file to save server messages")
    return parser


def _parse_args(args):
    parser = _new_argument_parser()
    args = parser.parse_args(args)
    return args


def _new_proxy_establisher(args):
    bind_address = (args.listen_addr, args.listen_port)
    server_address = (args.hostname, args.port)
    return core.IPv4ProxyEstablisher(bind_address, server_address)


@common.hide_exception(KeyboardInterrupt)
def main():
    args = _parse_args(sys.argv[1:])
    common.init_logging(args.verbose)

    listener = core.FileWriterMsgListener(args.clientfile, args.serverfile)
    if args.strip:
        listener = core.StripListener(listener, args.strip)
    if args.include:
        key, value = args.include.split("=", 1)
        listener = core.IncludeListener(listener, key, value)
    listener = core.JsonDecoderListener(listener)
    listener = core.NewlineSplitListener(listener)

    proxy_establisher = _new_proxy_establisher(args)
    try:
        csocket, ssocket = proxy_establisher.establish_connections()
        socket_proxy = core.SocketProxy(csocket, ssocket, listener)
        socket_proxy.start()
    finally:
        proxy_establisher.close()


if __name__ == "__main__":
    main()
