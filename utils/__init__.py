"""
utils
"""


def csv_to_dict(csv):
    """
    convert csv file to 2d array
    """
    with open(csv, "rb") as file:
        f = file.read()

    rows = f.decode().rstrip().split('\r\n')

    array = []
    for row in rows:
        array.append([y for y in row.rstrip(',').split(',')])

    return array


def dict_to_csv(array):
    """
    convert 2d array to csv
    """
    rows = []
    csv = ""
    for line in array:
        rows.append(','.join(str(x) for x in line) + ',')

    for row in rows:
        csv = csv + row + '\r\n'

    return csv



