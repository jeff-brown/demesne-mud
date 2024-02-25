def lucas(index, start=0):
    """
    return a pseudo-fibonacci sequence with an arbitrary starting value
    """
    if index <= 2:
        return [start, start + 1][:index]

    sequence = lucas(index - 1, start)

    sequence.append(sum(sequence[-2:]))

    return sequence
