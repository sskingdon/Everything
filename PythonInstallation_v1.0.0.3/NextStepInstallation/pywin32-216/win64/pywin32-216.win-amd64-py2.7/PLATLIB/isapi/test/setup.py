# setup_interp.py
# A distutils setup script for the ISAPI "redirector" sample.
import os
from distutils.core import setup
import py2exe

# Find the ISAPI sample - the redirector.
import isapi
script = os.path.join("extension_simple.py")

import winerror
win32_lib_dir = os.path.dirname(winerror.__file__)
tracer = dict(script = os.path.join(win32_lib_dir, "win32traceutil.py"),
              dest_base="tracer")

setup(name="ISAPI sample",
      # The ISAPI dll.
      isapi = [script],
      # command-line installation tool.
      console=[script, tracer],
)
