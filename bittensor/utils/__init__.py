import numbers
from typing import Callable, Union, List, Optional, Dict, Literal, Type, Any

import bittensor
import pandas
import requests
import torch
import scalecodec
import argparse
from substrateinterface.utils import ss58
from bittensor_wallet.utils import *

from .registration import create_pow, __reregister_wallet as reregister

RAOPERTAO = 1e9
U16_MAX = 65535
U64_MAX = 18446744073709551615


def indexed_values_to_dataframe(
    prefix: Union[str, int],
    index: Union[list, torch.LongTensor],
    values: Union[list, torch.Tensor],
    filter_zeros: bool = False,
) -> "pandas.DataFrame":
    # Type checking.
    if not isinstance(prefix, str) and not isinstance(prefix, numbers.Number):
        raise ValueError("Passed prefix must have type str or Number")
    if isinstance(prefix, numbers.Number):
        prefix = str(prefix)
    if not isinstance(index, list) and not isinstance(index, torch.Tensor):
        raise ValueError("Passed uids must have type list or torch.Tensor")
    if not isinstance(values, list) and not isinstance(values, torch.Tensor):
        raise ValueError("Passed values must have type list or torch.Tensor")
    if not isinstance(index, list):
        index = index.tolist()
    if not isinstance(values, list):
        values = values.tolist()

    index = [idx_i for idx_i in index if idx_i < len(values) and idx_i >= 0]
    dataframe = pandas.DataFrame(columns=[prefix], index=index)
    for idx_i in index:
        value_i = values[idx_i]
        if value_i > 0 or not filter_zeros:
            dataframe.loc[idx_i] = pandas.Series({str(prefix): value_i})
    return dataframe


def unbiased_topk(values, k, dim=0, sorted=True, largest=True):
    r"""Selects topk as in torch.topk but does not bias lower indices when values are equal.
    Args:
        values: (torch.Tensor)
            Values to index into.
        k: (int):
            Number to take.

    Return:
        topk: (torch.Tensor):
            topk k values.
        indices: (torch.LongTensor)
            indices of the topk values.
    """
    permutation = torch.randperm(values.shape[dim])
    permuted_values = values[permutation]
    topk, indices = torch.topk(
        permuted_values, k, dim=dim, sorted=sorted, largest=largest
    )
    return topk, permutation[indices]


def version_checking():
    response = requests.get(bittensor.__pipaddress__)
    latest_version = response.json()["info"]["version"]
    version_split = latest_version.split(".")
    latest_version_as_int = (
        (100 * int(version_split[0]))
        + (10 * int(version_split[1]))
        + (1 * int(version_split[2]))
    )

    if latest_version_as_int > bittensor.__version_as_int__:
        print(
            "\u001b[33mBittensor Version: Current {}/Latest {}\nPlease update to the latest version at your earliest convenience\u001b[0m".format(
                bittensor.__version__, latest_version
            )
        )


def strtobool_with_default(
    default: bool,
) -> Callable[[str], Union[bool, Literal["==SUPRESS=="]]]:
    """
    Creates a strtobool function with a default value.

    Args:
        default(bool): The default value to return if the string is empty.

    Returns:
        The strtobool function with the default value.
    """
    return lambda x: strtobool(x) if x != "" else default


def strtobool(val: str) -> Union[bool, Literal["==SUPRESS=="]]:
    """
    Converts a string to a boolean value.

    truth-y values are 'y', 'yes', 't', 'true', 'on', and '1';
    false-y values are 'n', 'no', 'f', 'false', 'off', and '0'.

    Raises ValueError if 'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def get_explorer_root_url_by_network_from_map(
    network: str, network_map: Dict[str, str]
) -> Optional[str]:
    r"""
    Returns the explorer root url for the given network name from the given network map.

    Args:
        network(str): The network to get the explorer url for.
        network_map(Dict[str, str]): The network map to get the explorer url from.

    Returns:
        The explorer url for the given network.
        Or None if the network is not in the network map.
    """
    explorer_url: Optional[str] = None
    if network in network_map:
        explorer_url = network_map[network]

    return explorer_url


def get_explorer_url_for_network(
    network: str, block_hash: str, network_map: Dict[str, str]
) -> Optional[str]:
    r"""
    Returns the explorer url for the given block hash and network.

    Args:
        network(str): The network to get the explorer url for.
        block_hash(str): The block hash to get the explorer url for.
        network_map(Dict[str, str]): The network map to get the explorer url from.

    Returns:
        The explorer url for the given block hash and network.
        Or None if the network is not known.
    """

    explorer_url: Optional[str] = None
    # Will be None if the network is not known. i.e. not in network_map
    explorer_root_url: Optional[str] = get_explorer_root_url_by_network_from_map(
        network, network_map
    )

    if explorer_root_url is not None:
        # We are on a known network.
        explorer_url = "{root_url}/query/{block_hash}".format(
            root_url=explorer_root_url, block_hash=block_hash
        )

    return explorer_url


def ss58_address_to_bytes(ss58_address: str) -> bytes:
    """Converts a ss58 address to a bytes object."""
    account_id_hex: str = scalecodec.ss58_decode(
        ss58_address, bittensor.__ss58_format__
    )
    return bytes.fromhex(account_id_hex)


def U16_NORMALIZED_FLOAT(x: int) -> float:
    return float(x) / float(U16_MAX)


def U64_NORMALIZED_FLOAT(x: int) -> float:
    return float(x) / float(U64_MAX)


def u8_key_to_ss58(u8_key: List[int]) -> str:
    r"""
    Converts a u8-encoded account key to an ss58 address.

    Args:
        u8_key (List[int]): The u8-encoded account key.
    """
    # First byte is length, then 32 bytes of key.
    return scalecodec.ss58_encode(bytes(u8_key).hex(), bittensor.__ss58_format__)


def type_or_suppress(
    type_func: Callable[[str], Any]
) -> Callable[[str], Union[Any, Literal["==SUPRESS=="]]]:
    def _type_or_suppress(value: str) -> Union[Any, Literal["==SUPRESS=="]]:
        return value if value == argparse.SUPPRESS else type_func(value)

    return _type_or_suppress
