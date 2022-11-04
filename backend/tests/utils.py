class _NotNull:
    """A helper object that compares equal to everything that isn't None."""

    def __eq__(self, other):
        return other is not None

    def __repr__(self):
        return "<NotNull>"


NotNull = _NotNull()
