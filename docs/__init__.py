#! /usr/bin/env python3


def get_version(data):
    def all_same(s):
        return all(x == s[0] for x in s)

    def has_digit(s):
        return any(x.isdigit() for x in s)

    data = data.splitlines()
    return list(
        line for line, underline in zip(data, data[1:])
        if (len(line) == len(underline) and
            all_same(underline) and
            has_digit(line) and
            "." in line)
    )[0]
