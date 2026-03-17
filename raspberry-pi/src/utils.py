import subprocess

def has_internet():
    try:
        subprocess.check_output(["ping", "-c", "1", "8.8.8.8"], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False