"""
This is dummy code showing how the minimal app could look like.
In his case we don't use a proxy, but directly a server
"""
import logging
import os
import click
from flask import request
from web3 import Web3, HTTPProvider

from microraiden.channel_manager import ChannelManager
from microraiden.make_helpers import make_channel_manager
from microraiden.config import CHANNEL_MANAGER_ADDRESS
from microraiden.proxy import PaywalledProxy
from microraiden.proxy.resources import Expensive


log = logging.getLogger(__name__)


class StaticPriceResource(Expensive):
    def get(self, url: str, param: str):
        log.info('Resource requested: {} with param "{}"'.format(request.url, param))
        return param


class DynamicPriceResource(Expensive):
    def get(self, url: str, param: int):
        log.info('Resource requested: {} with param "{}"'.format(request.url, param))
        return param

    def price(self):
        return int(request.view_args['param'])


@click.command()
@click.option(
    '--private-key',
    required=True,
    help='The server\'s private key in hex format.',
    type=str
)
def main(private_key: str):
    run(private_key)


def run(
        private_key: str,
        state_file_path: str = os.path.join(click.get_app_dir('microraiden'), 'echo_server.db'),
        channel_manager: ChannelManager = None,
        join_thread: bool = True
):
    dirname = os.path.dirname(state_file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    # set up a paywalled proxy
    # arguments are:
    #  - private key to use for receiving funds
    #  - file for storing state information (balance proofs)
    if channel_manager is None:
        channel_manager = make_channel_manager(
            private_key,
            CHANNEL_MANAGER_ADDRESS,
            state_file_path,
            Web3(HTTPProvider())
        )
    app = PaywalledProxy(channel_manager)

    # Add resource defined by regex and with a fixed price of 1 token.
    app.add_paywalled_resource(
        StaticPriceResource,
        "/echofix/<string:param>",
        price=5
    )
    # Resource with a price determined by the second parameter.
    app.add_paywalled_resource(
        DynamicPriceResource,
        "/echodyn/<int:param>"
    )

    # Start the app. proxy is a WSGI greenlet, so you must join it properly.
    app.run(debug=True)

    if join_thread:
        app.join()
    else:
        return app
    # Now use echo_client to get the resources.


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
