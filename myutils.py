import inspect
from typing import Callable, Union
from pathlib import Path
import warnings
from IPython.core.display import HTML

warnings.filterwarnings("ignore")


import json


class dotdict(dict):
    """
    a dictionary that supports dot notation
    as well as dictionary access notation
    usage: d = attrdict() or d = attrdict({'val1':'first'})
    set attributes: d.val2 = 'second' or d['val2'] = 'second'
    get attributes: d.val2 or d['val2']
    """

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        return json.dumps(self, indent=2, default=str)

    def __getitem__(self, index):
        if isinstance(index, (int, slice)):
            items = list(self.values())
            return items[index]
        else:
            return dict.__getitem__(self, index)

    def tolist(self):
        return list(self.keys())

    to_list = tolist

    def filter(self, key_filter: Union[str, Callable]):
        if callable(key_filter):
            return dotdict([(k, v) for k, v in self.items() if key_filter(k)])
        elif isinstance(key_filter, str):
            return dotdict([(k, v) for k, v in self.items() if key_filter in str(k)])

    def isupper(self):
        return dotdict([(k, v) for k, v in self.items() if k[0].isupper()])

    def islower(self):
        return dotdict([(k, v) for k, v in self.items() if k[0].islower()])

    def isin(self, keys):
        if isinstance(keys, dict):
            keys = list(keys.keys())
        else:
            keys = list(keys)
        return dotdict([(k, v) for k, v in self.items() if k in keys])

    def isnotin(self, keys):
        if isinstance(keys, dict):
            keys = list(keys.keys())
        else:
            keys = list(keys)
        return dotdict([(k, v) for k, v in self.items() if not k in keys])


def attr(obj):
    """Returns obj's state_types, callable_signatures, state_values, and callables_bounded"""
    all_attr = {}
    for attribute in dir(obj):
        if not attribute.startswith("_"):
            try:
                all_attr[attribute] = getattr(obj, attribute)
            except Exception as e:
                continue

    methods = dict([(k, v) for k, v in all_attr.items() if callable(v)])

    signatures = {}
    for k, v in all_attr.items():
        if callable(v):
            try:
                signatures[k] = inspect.signature(v)  # may occur ValueError
            except Exception as e:
                signatures[k] = "No signature available for built-in method"

    state_keys = sorted(list(set(all_attr.keys()) - set(methods.keys())))
    state_types = dict([(k, type(getattr(obj, k))) for k in state_keys])
    state_values = dict([(k, getattr(obj, k)) for k in state_keys])

    return dotdict(
        a=dotdict(state_types),
        b=dotdict(signatures),
        c=dotdict(state_values),
        d=dotdict(methods),
    )


def kv(obj):
    for k, v in obj.items():
        print(f"{k}:\n{v}")
        print()


def jd(obj: dict):
    print(json.dumps(obj, indent=2, default=str))


import yaml
import re


def read_yaml(filename):
    loader = yaml.SafeLoader
    loader.add_implicit_resolver(
        "tag:yaml.org,2002:float",
        re.compile(
            """^(?:
        [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |\\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
        |[-+]?\\.(?:inf|Inf|INF)
        |\\.(?:nan|NaN|NAN))$""",
            re.X,
        ),
        list("-+0123456789."),
    )

    with open(filename, "r") as f:
        args = yaml.load(f, Loader=loader)
    return args


HTML(
    r"""
<style>
    * {
        font-size: 14px !important;
        line-height: 1.2 !important;
    }
    .output-plaintext, .output-stream, .output {
        font-family: "Consolas" !important; # Any monospaced font should work
    }
</style>
"""
)
