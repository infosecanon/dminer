import os

def build_filename_timestamp(regex_matcher, base_year=2000):
    """
    Given a `re.match` object, this function will return a formatted
    timestamp in the format of:

        "yyyy:MM:dd HH:mm:ss:SSS"

    This function will explicitly throw an error if the `re.match`
    object passed does not have the following named groups:

        year
        month
        day

    The explicit throwing of errors on these attributes prevents wierd
    indexing bugs across different storage backends.

    The following attributes of the `re.match` object will be normalized
    if they do not exist:

        hour -> 00
        minute -> 00
        second -> 00
        milisecond -> 000
    """

    # We don't normalize these values, as these are minimum necessary for indexing.
    timestamp = ":".join(
        [
            str(int(regex_matcher.group("year")) + base_year),
            str(regex_matcher.group("month")).zfill(2),
            str(regex_matcher.group("day")).zfill(2)
        ]
    )
    # Normalize the hour to be the afternoon, as we are only pulling to the day
    # if the values do not exist
    timestamp += " " + ":".join(
        [
            safe_named_group_value(regex_matcher, "hour", default="00"),
            safe_named_group_value(regex_matcher, "minute", default="00"),
            safe_named_group_value(regex_matcher, "second", default="00"),
            safe_named_group_value(regex_matcher, "milisecond", default="000")
        ]
    )
    print timestamp
    return timestamp

def safe_named_group_value(regex_matcher, name, default=None):
    """
    given a `re.match` object, this function will attempt to pull the value
    of a named group. If it does not exist (IndexError thrown), the `default`
    value will be returned.
    """
    try:
        return regex_matcher.group(name)
    except IndexError:
        return default

def get_files(directory):
    """
    Fetches file paths for a given directory. It returns the full paths to
    each file in the directory, based off of the directory given.
    """
    if os.path.exists(directory):
        return [os.path.join(directory, f) for f in os.listdir(directory)]
    else:
        raise Exception("Directory does not exist: %s" % directory)
