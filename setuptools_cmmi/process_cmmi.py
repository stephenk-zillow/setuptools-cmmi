import os
import sys

import logging
from distutils.errors import DistutilsSetupError
from distutils.spawn import find_executable

LOG = logging.getLogger(__name__)


def _find_source_root_dir(temp_source_dir):
    """Look through subdirs until we find actual files."""
    next_dir = temp_source_dir
    lst_entries = os.listdir(temp_source_dir)

    while len(lst_entries) == 1:
        next_dir = os.path.join(next_dir, lst_entries[0])
        print("next_dir: {}".format(next_dir))
        if os.path.isdir(next_dir):
            lst_entries = os.listdir(next_dir)
        else:
            break
    return next_dir

def _run(root_path, exec_name, description, args):
    """Run the specified path after making sure it exists."""
    print('CMMI RUN roto_path={} exec_name={} desc={} args={}'
          .format(root_path, exec_name, description, args))
    sys.stdout.flush()

    if os.path.exists(os.path.join(root_path, exec_name)):
        exec_path = os.path.join(root_path, exec_name)
    else:
        exec_path = find_executable(exec_name)

    if not exec_path:
        raise DistutilsSetupError("{0} path ({1}) could not be found."
                                  .format(description, exec_name))
    if args:
            exec_path = exec_path + " " + args
    LOG.info("Running {}".format(exec_path))
    print('CMMI RUNNING EXEC_PATH={}'.format(exec_path))
    sys.stdout.flush()
    rc = os.system(exec_path)
    print('CMMI DONE RUNNING EXEC_PATH={}, rc={}'.format(exec_path, rc))
    sys.stdout.flush()
    if rc != 0:
        raise DistutilsSetupError("{0} exited with return code: {1}."
                                  .format(exec_path, rc))


def process_cmmi(dest_dir, temp_source_dir, config_options, autogen, config_name=None):
    """Run through the CMMI process with the given parameters."""
    print('PROCESS CMMI FOR DEST DIR {}'.format(dest_dir))
    sys.stdout.flush()
    LOG.debug("Making dir {}".format(dest_dir))
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    try:
        pushd = os.getcwd()

        src_root = _find_source_root_dir(temp_source_dir)
        os.chdir(src_root)

        print('AUTOGEN? {}'.format(autogen))
        sys.stdout.flush()
        if autogen:
            print('RUN: AUTOGEN')
            sys.stdout.flush()
            _run(src_root, autogen, "Autogen")
        print('RUN: CONFIGURE')
        sys.stdout.flush()
        _run(src_root, config_name or "configure", "Configure", config_options)
        print('RUN: MAKE')
        sys.stdout.flush()
        _run(src_root, "make", "make", None)
        print('RUN: MAKE INSTALL')
        sys.stdout.flush()
        _run(src_root, "make", "make install", "install")
        print('END OF process_cmmi')
        sys.stdout.flush()
    finally:
        print('FINALLY! process_cmmi')
        sys.stdout.flush()
        os.chdir(pushd)
