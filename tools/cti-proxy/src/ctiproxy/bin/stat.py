# -*- coding: UTF-8 -*-

import sys
from ctiproxy import core
from ctiproxy.bin import common


def _new_argument_parser():
    return common.new_argument_parser(add_help=True)


def _parse_args(args):
    parser = _new_argument_parser()
    parsed_args = parser.parse_args(args)
    return parsed_args


def _new_proxy_establisher(args):
    bind_address = (args.listen_addr, args.listen_port)
    server_address = (args.hostname, args.port)
    return core.IPv4ProxyEstablisher(bind_address, server_address)


@common.hide_exception(KeyboardInterrupt)
def main():
    args = _parse_args(sys.argv[1:])
    common.init_logging(args.verbose)
    
    stat_listener = core.StatisticListener()
    proxy_establisher = _new_proxy_establisher(args)
    try:
        csocket, ssocket = proxy_establisher.establish_connections()
        socket_proxy = core.SocketProxy(csocket, ssocket, stat_listener)
        socket_proxy.start()
    finally:
        proxy_establisher.close()
        stat_listener.print_stats()


if __name__ == "__main__":
    main()
