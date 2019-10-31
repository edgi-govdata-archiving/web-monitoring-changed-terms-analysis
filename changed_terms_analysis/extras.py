# Extra Bits that were left out of the ultimate script, but might be useful.
class IntersectionCounter(Counter):
    """
    Like a counter, but when you update it, it only considers what's in common.

    Examples
    --------
    >>> counter = IntersectionCounter(a=5, b=3)
    >>> counter.update(dict(a=4, b=6))
    IntersectionCounter(a=4, b=3)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialized = len(args) > 0 or len(kwargs) > 0

    def update(self, other=None):
        if not other:
            super().update(other)
            return self

        if not self._initialized:
            self._initialized = True
            super().update(other)
            return self

        for key, value in list(self.items()):
            if key in other:
                if abs(other[key]) < abs(value):
                    self[key] = other[key]
            else:
                del self[key]

        return self


def find_common_changes(changes, grams):
    common_grams = [(IntersectionCounter(), IntersectionCounter())
                    for _ in range(grams)]

    for change in changes:
        for gram, common in enumerate(common_grams):
            for index in range(2):
                common[index].update(change['terms'][gram][index])

    return common_grams


def subset_dict(original, keys):
    return {key: original[key] for key in keys if key in original}
