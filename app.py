from flask import Flask
from apis import api
import os

app = Flask(__name__)
api.init_app(app)

# This can be used to set file system monitoring for a core directory.
# It would be better to have the real logic separated out so we can
# be testing properly.
extra_files = []
#extra_dirs = ['core', ]
#extra_files = extra_dirs[:]
# for extra_dir in extra_dirs:
#    for dirname, dirs, files in os.walk(extra_dir):
#        for filename in files:
#            filename = os.path.join(dirname, filename)
#            if os.path.isfile(filename):
#                extra_files.append(filename)

app.run(extra_files=extra_files, debug=True)
