import logging
from elasticsearch.helpers import bulk

from aleph.core import es
from aleph.util import is_list, unique_list

log = logging.getLogger(__name__)


def bulk_op(iter, chunk_size=500):
    bulk(es, iter, stats_only=True, chunk_size=chunk_size,
         request_timeout=200.0)


def merge_docs(old, new):
    """Exend the values of the new doc with extra values from the old."""
    old = remove_nulls(old)
    new = dict(remove_nulls(new))
    for k, v in old.items():
        if k in new:
            if is_list(v):
                v = new[k] + v
                new[k] = unique_list(v)
            elif isinstance(v, dict):
                new[k] = merge_docs(v, new[k])
        else:
            new[k] = v
    return new


def remove_nulls(data):
    """Remove None-valued keys from a dictionary, recursively."""
    if isinstance(data, dict):
        for k, v in data.items():
            if v is None:
                data.pop(k)
            data[k] = remove_nulls(v)
    elif is_list(data):
        data = [remove_nulls(d) for d in data if d is not None]
    return data
