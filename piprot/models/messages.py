class Messages:
    NOT_ROTTEN: str = "{package} ({version}) is up to date"
    IGNORED: str = "Ignoring updates for {package}."
    CANNOT_FETCH: str = "Skipping {package} ({version}). Cannot fetch info from PyPI"
    NO_DELAY_INFO: str = (
        "{package} ({current_version}) is out of date. "
        "No delay info available. "
        "Latest version is: {latest_version}"
    )
    ROTTEN_NOT_DIRECT_SUCCESSOR: str = (
        "{package} ({current_version}) "
        "is {rotten_days} days out of date. "
        "Latest version is: {latest_version} "
        "({days_since_last_release} days old)."
    )
    ROTTEN_DIRECT_SUCCESSOR: str = (
        "{package} ({current_version}) "
        "is {rotten_days} days out of date. "
        "Latest version is: {latest_version}"
    )
