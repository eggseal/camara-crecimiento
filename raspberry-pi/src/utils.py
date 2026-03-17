import subprocess


def has_internet() -> bool:
    """Returns the internet status as boolean by pinging the Google DNS at 8.8.8.8"""
    try:
        subprocess.check_output(
            ["ping", "-c", "1", "8.8.8.8"], stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False
