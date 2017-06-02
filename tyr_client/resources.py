import os

class strings(object):
    """
    This class contains a collection of string literals
    used throughout the tyr test suite

    """
    DIR_SOURCE = "../src"
    OPTARGS = "hi:c:o:CET"

    # Filesystem
    FS_HOME = "HOME"
    FS_KNOWN_HOSTS = ".ssh/known_hosts"
    FS_TYRRC = os.path.join(os.getenv(FS_HOME), ".tyrrc")

    # Compilers
    COMPILER_PYTHON = "python"
    COMPILER_C = "gcc"
    COMPILER_CPP = "g++"
    COMPILER_JAVA = "javac"

    # Languages
    LANG_PYTHON = "python"
    LANG_C = "c"
    LANG_CPP = "c++"
    LANG_JAVA = "java"

    # Error statuses
    ERR_NO_LANG = "Error: no language matches "
    ERR_DIR_NOT_FOUND = "Error: directory not found"
    ERR_OPT_ITER = "Error: iterations must be greater than 1"
    ERR_OPT_COMP_ONLY = "Error: compile only cannot be used with option -E"
    ERR_OPT_EXEC_ONLY = "Error: execute only cannot be used with option -C"
    ERR_SFTP = "Error: failed sending files to server"
    ERR_SOCK_CONN_REFUSED = "Error: socket connection refused"

    # Test statuses
    TEST_SEND = "Sending source code to server."

    # Conf strings
    CONF_LOKI = "loki"
    CONF_ADDR = "address"
    CONF_PORT = "port"
    CONF_USER = "username"
    CONF_RPATH = "remotepath"
    CONF_FILES = "files"
    CONF_DIR = "testdir"
    CONF_BUILD = "build"
    CONF_LANG = "language"
    CONF_INPUT = "input"
    CONF_OUTPUT = "output"
    CONF_TEST = "test"
    CONF_EXEC = "exec"
    CONF_LIBS = "libs"

    # Tar helpers
    TAR_CMD = "tar xvf "
    TAR_EXT = ".tar.gz"
    TAR_W = "w:gz"
