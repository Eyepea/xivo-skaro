# -*- coding: UTF-8 -*-

import argparse
import itertools
import sys
from ctiproxy import core
from ctiproxy.bin import common


def _new_argument_parser():
    common_parser = common.new_argument_parser()
    parser = argparse.ArgumentParser(parents=[common_parser])
    parser.add_argument("--loop", action="store_true", default=False,
                        help="wait for another connection when one is closed")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--no-client", action="store_true", default=False,
                       help="don't display messages from client")
    group.add_argument("--no-server", action="store_true", default=False,
                       help="don't display messages from server")
    parser.add_argument("--raw", action="store_true", default=False,
                        help="display raw messages")
    parser.add_argument("--pretty-print", action="store_true", default=False,
                        help="pretty print messages")
    parser.add_argument("-s", "--strip", action="append",
                        help="strip the given fields from messages")
    parser.add_argument("-i", "--include", action="store",
                        help="include only the given messages")
    return parser


def _parse_args(args):
    parser = _new_argument_parser()
    parsed_args = parser.parse_args(args)
    return parsed_args


def _new_proxy_establisher(args):
    bind_address = (args.listen_addr, args.listen_port)
    server_address = (args.hostname, args.port)
    return core.IPv4ProxyEstablisher(bind_address, server_address)


def _new_listener(args):
    if args.raw:
        listener = core.RawPrintListener()
    else:
        listener = core.PrintMsgListener(args.pretty_print)
        if args.strip:
            listener = core.StripListener(listener, args.strip)
        if args.include:
            key, value = args.include.split("=", 1)
            listener = core.IncludeListener(listener, key, value)
        listener = core.JsonDecoderListener(listener)
        listener = core.NewlineSplitListener(listener)
    if args.no_client:
        listener = core.NoClientListener(listener)
    elif args.no_server:
        listener = core.NoServerListener(listener)
    return listener


def _new_loop_ctrl(args):
    if args.loop:
        return itertools.repeat(True)
    else:
        return [True]


@common.hide_exception(KeyboardInterrupt)
def main():
    args = _parse_args(sys.argv[1:])
    common.init_logging(args.verbose)

    loop_ctrl = _new_loop_ctrl(args)
    proxy_establisher = _new_proxy_establisher(args)
    try:
        for _ in loop_ctrl:
            listener = _new_listener(args)
            try:
                csocket, ssocket = proxy_establisher.establish_connections()
            except Exception:
                listener.close()
                raise
            else:
                socket_proxy = core.SocketProxy(csocket, ssocket, listener)
                socket_proxy.start()
    finally:
        proxy_establisher.close()


if __name__ == "__main__":
    main()
