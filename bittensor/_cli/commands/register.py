# The MIT License (MIT)
# Copyright © 2021 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of 
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import argparse
import bittensor
from rich.prompt import Prompt
from .utils import check_netuid_set, check_for_cuda_reg_config

console = bittensor.__console__

class RegisterCommand:

    @staticmethod
    def run( cli ):
        r""" Register neuron. """
        wallet = bittensor.wallet( config = self.config )
        subtensor = bittensor.subtensor( config = self.config )

        # Verify subnet exists
        if not subtensor.subnet_exists( netuid = self.config.netuid ):
            bittensor.__console__.print(f"[red]Subnet {self.config.netuid} does not exist[/red]")
            sys.exit(1)

        subtensor.register(
            wallet = wallet,
            netuid = self.config.netuid,
            prompt = not self.config.no_prompt,
            TPB = self.config.subtensor.register.cuda.get('TPB', None),
            update_interval = self.config.subtensor.register.get('update_interval', None),
            num_processes = self.config.subtensor.register.get('num_processes', None),
            cuda = self.config.subtensor.register.cuda.get('use_cuda', bittensor.defaults.subtensor.register.cuda.use_cuda),
            dev_id = self.config.subtensor.register.cuda.get('dev_id', None),
            output_in_place = self.config.subtensor.register.get('output_in_place', bittensor.defaults.subtensor.register.output_in_place),
            log_verbose = self.config.subtensor.register.get('verbose', bittensor.defaults.subtensor.register.verbose),
        )


    @staticmethod
    def add_args( parser: argparse.ArgumentParser ):
        register_parser = parser.add_parser(
            'register', 
            help='''Register a wallet to a network.'''
        )
        register_parser.add_argument( 
            '--no_version_checking', 
            action='store_true', 
            help='''Set false to stop cli version checking''', 
            default = False 
        )
        register_parser.add_argument(
            '--no_prompt', 
            dest='no_prompt', 
            action='store_true', 
            help='''Set true to avoid prompting the user.''',
            default=False,
        )
        register_parser.add_argument(
            '--netuid',
            type=int,
            help='netuid for subnet to serve this neuron on',
            default=argparse.SUPPRESS,
        )

        bittensor.wallet.add_args( register_parser )
        bittensor.subtensor.add_args( register_parser )

    @staticmethod   
    def check_config( config: 'bittensor.Config' ):
        if config.subtensor.get('network') == bittensor.defaults.subtensor.network and not config.no_prompt:
            config.subtensor.network = Prompt.ask("Enter subtensor network", choices=bittensor.__networks__, default = bittensor.defaults.subtensor.network)

        check_netuid_set( config )

        if config.wallet.get('name') == bittensor.defaults.wallet.name and not config.no_prompt:
            wallet_name = Prompt.ask("Enter wallet name", default = bittensor.defaults.wallet.name)
            config.wallet.name = str(wallet_name)

        if config.wallet.get('hotkey') == bittensor.defaults.wallet.hotkey and not config.no_prompt:
            hotkey = Prompt.ask("Enter hotkey name", default = bittensor.defaults.wallet.hotkey)
            config.wallet.hotkey = str(hotkey)

        if not config.no_prompt:
            check_for_cuda_reg_config(config)





      