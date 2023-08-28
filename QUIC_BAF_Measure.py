import argparse
import asyncio
import logging
import pickle
import socket
import ipaddress
from typing import Optional, cast, AsyncGenerator, Callable
from contextlib import asynccontextmanager

from aioquic.asyncio.protocol import QuicConnectionProtocol, QuicStreamHandler
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.connection import QuicConnection
from aioquic.tls import SessionTicketHandler
from dnslib.dns import DNSRecord

logger = logging.getLogger("client")


class MyClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ack_waiter: Optional[asyncio.Future[DNSRecord]] = None


def save_session_ticket(ticket):
    """
    Callback which is invoked by the TLS engine when a new session ticket
    is received.
    """
    logger.info("New session ticket received")
    if args.session_ticket:
        with open(args.session_ticket, "wb") as fp:
            pickle.dump(ticket, fp)


@asynccontextmanager
async def connect(
        host: str,
        port: int,
        *,
        configuration: Optional[QuicConfiguration] = None,
        create_protocol: Optional[Callable] = QuicConnectionProtocol,
        session_ticket_handler: Optional[SessionTicketHandler] = None,
        stream_handler: Optional[QuicStreamHandler] = None,
        wait_connected: bool = True,
        local_port: int = 0,
) -> AsyncGenerator[QuicConnectionProtocol, None]:
    loop = asyncio.get_event_loop()
    local_host = "::"

    # if host is not an IP address, pass it to enable SNI
    try:
        ipaddress.ip_address(host)
        server_name = None
    except ValueError:
        server_name = host

    # lookup remote address
    infos = await loop.getaddrinfo(host, port, type=socket.SOCK_DGRAM)
    addr = infos[0][4]
    if len(addr) == 2:
        addr = ("::ffff:" + addr[0], addr[1], 0, 0)

    # prepare QUIC connection
    if configuration is None:
        configuration = QuicConfiguration(is_client=True)
    if configuration.server_name is None:
        configuration.server_name = server_name
    connection = QuicConnection(
        configuration=configuration, session_ticket_handler=session_ticket_handler
    )

    # explicitly enable IPv4/IPv6 dual stack
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    completed = False
    try:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        sock.bind((local_host, local_port, 0, 0))
        completed = True
    finally:
        if not completed:
            sock.close()
    # connect
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: create_protocol(connection, stream_handler=stream_handler),
        sock=sock,
    )
    protocol = cast(QuicConnectionProtocol, protocol)
    try:
        protocol.connect(addr)
        if wait_connected:
            await protocol.wait_connected()
        yield protocol
    finally:
        transport.close()


async def main(
        configuration: QuicConfiguration,
        host: str,
        port: int,
) -> None:
    logger.debug(f"Connecting to {host}:{port}")
    async with connect(
            host,
            port,
            configuration=configuration,
            session_ticket_handler=save_session_ticket,
            create_protocol=MyClientProtocol,
            wait_connected=False,
    ) as client:
        print('init send success', host)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS over QUIC client")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="The remote peer's host name or IP address",
    )
    parser.add_argument(
        "--port", type=int, default=784, help="The remote peer's port number"
    )
    parser.add_argument(
        "--ca-certs", type=str, help="load CA certificates from the specified file"
    )
    parser.add_argument(
        "--server-name", type=str, default=None, help="h3 protocol necessary"
    )

    args = parser.parse_args()

    configuration = QuicConfiguration(
        alpn_protocols=["h3", "doq"],
        is_client=True,
        server_name=args.server_name
    )

    if args.ca_certs:
        configuration.load_verify_locations(args.ca_certs)

    asyncio.run(
        main(
            configuration=configuration,
            host=args.host,
            port=args.port,
        )
    )
