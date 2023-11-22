def firstForCondition(iterable, condition = lambda x: True, default = None):
    """
    Returns the first item in the `iterable` that satisfies the `condition`.

    If the condition is not given, returns the first item of the iterable.

    If the `default` argument is given and the iterable is empty, or if it has
    no items matching the condition, the `default` argument is returned.

    Raises `StopIteration` if no item satisfying the condition is found and
    default is not given.
    """

    try:
        return next(x for x in iterable if condition(x))
    except StopIteration:
        if default is not None:
            return default
        else:
            raise
