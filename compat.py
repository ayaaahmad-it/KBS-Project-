

import collections
import collections.abc

getattr(collections, "Mapping", None) or setattr(
    collections, "Mapping", collections.abc.Mapping
)
