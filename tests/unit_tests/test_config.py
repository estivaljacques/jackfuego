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
from unittest.mock import MagicMock

def test_strict():
    parser = argparse.ArgumentParser()
    # Positional/mandatory arguments don't play nice with multiprocessing.
    # When the CLI is used, the argument is just the 0th element or the filepath.
    # However with multiprocessing this function call actually comes from a subprocess, and so there
    # is no positional argument and this raises an exception when we try to parse the args later.
    # parser.add_argument("arg", help="Dummy Args")
    parser.add_argument("--cov", help="Dummy Args")
    parser.add_argument("--cov-append", action='store_true', help="Dummy Args")
    parser.add_argument("--cov-config",  help="Dummy Args")
    bittensor.logging.add_args( parser )
    bittensor.wallet.add_args( parser )
    bittensor.subtensor.add_args( parser )
    bittensor.axon.add_args( parser )
    bittensor.config( parser, strict=False)
    bittensor.config( parser, strict=True)

def test_prefix():
    # Test the use of prefixes to instantiate all of the bittensor objects.
    parser = argparse.ArgumentParser()

    mock_wallet = MagicMock(
        spec=bittensor.wallet,
        coldkey=MagicMock(),
        coldkeypub=MagicMock(
            # mock ss58 address
            ss58_address="5DD26kC2kxajmwfbbZmVmxhrY9VeeyR1Gpzy9i8wxLUg6zxm"
        ),
        hotkey=MagicMock(
            ss58_address="5CtstubuSoVLJGCXkiWRNKrrGg2DVBZ9qMs2qYTLsZR4q1Wg"
        ),
    )

    bittensor.logging.add_args( parser )
    bittensor.logging.add_args( parser, prefix = 'second' )

    bittensor.wallet.add_args( parser )
    bittensor.wallet.add_args( parser, prefix = 'second' )

    bittensor.subtensor.add_args( parser )
    bittensor.subtensor.add_args( parser, prefix = 'second'  )

    bittensor.axon.add_args( parser )
    bittensor.axon.add_args( parser, prefix = 'second' )

    config_non_strict = bittensor.config( parser, strict=False)
    config_strict = bittensor.config( parser, strict=True)

    bittensor.axon( wallet=mock_wallet, config=config_strict ).stop()
    bittensor.axon( wallet=mock_wallet, config=config_non_strict ).stop()
    bittensor.axon( wallet=mock_wallet, config=config_strict.second ).stop()
    bittensor.axon( wallet=mock_wallet, config=config_non_strict.second ).stop()

    bittensor.wallet( config_strict )
    bittensor.wallet( config_non_strict )
    bittensor.wallet( config_strict.second )
    bittensor.wallet( config_non_strict.second )

    bittensor.logging( config_strict )
    bittensor.logging( config_non_strict )
    bittensor.logging( config_strict.second )
    bittensor.logging( config_non_strict.second )


if __name__  == "__main__":
    test_prefix()