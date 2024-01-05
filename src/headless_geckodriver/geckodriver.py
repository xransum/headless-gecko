import sys
import os
import logging
import urllib.request
import urllib.error
import logging
import tarfile
import zipfile
from glob import glob

from io import BytesIO


logger = logging.getLogger(__name__)

GECKODRIVER_DEFAULT_ROOT = os.path.abspath(os.path.dirname(__file__))
GECKODRIVER_RELATIVE_PATH = os.path.join("lib", "geckodriver")
GECKODRIVER_REPOSITORY_URL = (
    "https://github.com/mozilla/geckodriver/releases/download/{version}"
    "/geckodriver-{version}-{platform}{architecture}.{compression}"
)
GECKODRIVER_REPOSITORY_LATEST_URL = (
    "https://github.com/mozilla/geckodriver/releases/latest"
)


def get_sys_arch() -> str:
    """Returns the architecture of the current OS.
    Args:
        None
    Returns:
        str: The architecture of the current OS.
    """
    arch = "32"
    if sys.maxsize > 2**32:
        arch = "64"
    return arch


def get_sys_platform() -> str:
    """Returns the platform of the current OS.
    Args:
        None
    Returns:
        str: The platform of the current OS.
    """
    platform = "linux"

    if sys.platform.startswith("win"):
        platform = "win"

    elif sys.platform.startswith("darwin"):
        platform = "macos"

    return platform


def get_sys_name() -> str:
    """Returns the platform and architecture of the current OS.
    Args:
        None
    Returns:
        str: The platform and architecture of the current OS.
    """
    return "{platform}{architecture}".format(
        platform=get_sys_platform(), architecture=get_sys_arch()
    )


def get_compression_format() -> str:
    """Returns the compression format for the current platform.
    Args:
        None
    Returns:
        str: The compression format for the current platform.
    """
    comp = "tar.gz"
    if get_sys_platform() == "win":
        comp = "zip"

    return comp


def get_variable_separator() -> str:
    """Returns the separator for the PATH variable.
    Args:
        None
    Returns:
        str: The separator for the PATH variable.
    """
    sep = ":"
    if get_sys_platform() == "win":
        sep = ";"

    return sep


def get_geckodriver_filename() -> str:
    """Returns the filename of the binary for the current platform.
    Args:
        None
    Returns:
        str: The filename of the binary for the current platform.
    """
    name = "geckodriver"
    if get_sys_platform() == "win":
        name += ".exe"

    return name


def get_download_url(version: str) -> str:
    """Returns the download URL for the given version.
    Args:
        version (str): The version of the geckodriver binary.
    Returns:
        str: The download URL for the given version.
    """
    platform = get_sys_platform()
    architecture = get_sys_arch()
    compression = get_compression_format()

    return GECKODRIVER_REPOSITORY_URL.format(
        version=version,
        platform=platform,
        architecture=architecture,
        compression=compression,
    )


def get_latest_version() -> str:
    """Returns the latest version of the geckodriver binary.
    Args:
        None
    Returns:
        str: The latest version of the geckodriver binary.
    """
    url = GECKODRIVER_REPOSITORY_LATEST_URL
    logging.info("Fetching latest geckodriver version from %s", url)

    try:
        req = urllib.request.urlopen(url)
        final_url = req.geturl()
    except urllib.error.HTTPError as err:
        logger.error("Failed to fetch latest geckodriver version: %s", err)
        return None

    version = final_url.split("/")[-1]
    logging.info("Latest geckodriver version is %s", version)
    return version


def get_install_root() -> str:
    """Returns the installation root directory for the geckodriver binary.
    Args:
        None
    Returns:
        str: The installation root directory for the geckodriver binary.
    """
    return GECKODRIVER_DEFAULT_ROOT


def get_install_dir() -> str:
    """Returns the installation directory for the geckodriver binary.
    Args:
        None
    Returns:
        str: The installation directory for the geckodriver binary.
    """
    root = get_install_root()
    dir_path = os.path.join(root, GECKODRIVER_RELATIVE_PATH)
    return dir_path


def get_binary_path() -> str:
    """Returns the path to the geckodriver binary.
    Args:
        None
    Returns:
        str: The path to the geckodriver binary.
    """
    install_dir = get_install_dir()
    filename = get_geckodriver_filename()
    path = os.path.join(install_dir, filename)
    return path


def get_firefox_path() -> str:
    """Returns the path to the firefox binary.
    Args:
        None
    Returns:
        str: The path to the firefox binary.
    """
    firefox_install_dir = None
    if get_sys_platform() == "win":
        win_semi_paths = [
            "%s:\\Program Files\\Mozilla Firefox",
            "%s:\\Program Files (x86)\\Mozilla Firefox",
            "%s:\\Program Files\\Mozilla Thunderbird",
            "%s:\\Program Files\\mozilla.org\\Mozilla",
            "%s:\\Program Files\\mozilla.org\\SeaMonkey",
            "%s:\\Program Files\\SeaMonkey",
        ]
        # Add all letters of the alphabet to the paths
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            # Add all paths with the letter
            for semi_path in win_semi_paths:
                # If the drive exists, add the path
                if os.path.exists(f"{letter}:"):
                    path = os.path.join(semi_path % letter, "firefox*.exe")
                    for bins in glob(path):
                        if "firefox" in bins.lower():
                            firefox_install_dir = bins
                            break
                    if firefox_install_dir is not None:
                        break

    elif get_sys_platform() == "linux":
        linux_semi_paths = [
            "/usr/lib/",
            "/usr/lib64/",
            "/usr/lib/firefox/",
            "/usr/lib64/firefox/",
            "/usr/lib/firefox*/",
            "/usr/lib64/firefox*/",
        ]
        # Add all paths with the letter
        for semi_path in linux_semi_paths:
            # If the drive exists, add the path
            if os.path.exists(semi_path):
                path = os.path.join(semi_path, "firefox")
                for bins in glob(path):
                    if "firefox" in bins.lower():
                        firefox_install_dir = bins
                        break
                if firefox_install_dir is not None:
                    break

    elif get_sys_platform() == "macos":
        mac_semi_paths = [
            "/Applications/Firefox.app/Contents/MacOS/firefox",
        ]
        # Add all paths with the letter
        for semi_path in mac_semi_paths:
            # If the drive exists, add the path
            if os.path.exists(semi_path):
                path = os.path.join(semi_path, "firefox")
                for bins in glob(path):
                    if "firefox" in bins.lower():
                        firefox_install_dir = bins
                        break
                if firefox_install_dir is not None:
                    break

    return firefox_install_dir


def uncompress_file(file: BytesIO, directory: str) -> str:
    """Uncompresses the given file to the given directory.
    Args:
        file (file): The file to uncompress.
        directory (str): The directory to uncompress the file to.
    Returns:
        None
    """
    platform = get_sys_platform()

    if platform == "win":
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(directory)
    else:
        tar = tarfile.open(fileobj=file, mode="r:gz")
        tar.extractall(directory)
        tar.close()


def is_installed() -> bool:
    """Checks whether the geckodriver binary is downloaded.
    Args:
        None
    Returns:
        bool: Whether the geckodriver binary is downloaded.
    """
    path = get_binary_path()
    return os.path.exists(path)


def install() -> bool:
    """Downloads the latest geckodriver binary.
    Args:
        None
    Returns:
        bool: Whether the geckodriver binary was successfully downloaded.
    """
    version = get_latest_version()
    url = get_download_url(version)
    path = get_binary_path()

    logging.info("Downloading latest geckodriver archive from %s", url)
    try:
        resp = urllib.request.urlopen(url)
        status_code = resp.getcode()
        if status_code != 200:
            raise urllib.error.URLError("Not Found")

    except urllib.error.URLError:
        raise RuntimeError(f"Failed to download geckodriver archive: {url}")

    archive = BytesIO(resp.read())

    # Uncompress file to install dir
    logging.info("Uncompressing file to installation directory")
    try:
        uncompress_file(archive, os.path.dirname(path))
    except Exception as err:
        logger.error("Failed to uncompress file: %s", err)
        return False

    # Create the install directory if it doesn't exist
    if os.path.exists(os.path.dirname(path)) is False:
        logging.info("Creating installation directory")
        os.makedirs(os.path.dirname(path))
    else:
        logging.info("Installation directory already exists")

    # Make the binary executable
    logging.info("Making binary executable")
    try:
        os.chmod(path, 0o744)
    except Exception as err:
        logger.error("Failed to make binary executable: %s", err)
        return False

    return True


def main() -> None:
    """Main entry point for the script."""
    logging.basicConfig(level=logging.INFO)

    if is_installed() is False:
        logging.info("geckodriver is not installed")
        if install() is False:
            logging.error("Failed to install geckodriver")
            return
        else:
            logging.info("geckodriver was successfully installed")

    else:
        logging.info("geckodriver is already installed")

    install_dir = get_install_dir()
    binary_path = get_binary_path()
    print(f"Install directory: {install_dir}")
    print(f"Binary path: {binary_path}")


if __name__ == "__main__":
    main()
