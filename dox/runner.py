# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = [
    'Runner',
]

import os
import shutil
import shlex
import tempfile

import sh


class Runner(object):

    def __init__(self, args):
        self.args = args

    def get_tagname(self, tag):
        project = os.path.basename(os.path.abspath('.'))
        return "%s/%s" % (project, tag)

    def build_test_image(self, image, commands):
        tempd = tempfile.mkdtemp()
        with open(os.path.join(tempd, 'Dockerfile'), 'w') as dockerfile:
            dockerfile.write("FROM %s\n" % image)
            for add_file in commands.get_add_files():
                shutil.copy(add_file, os.path.join(tempd, add_file))
                dockerfile.write("ADD %s /dox\n" % add_file)
            dockerfile.write("WORKDIR /dox\n")
            for command in commands.prep_commands():
                dockerfile.write("RUN %s\n" % command)
        r =sh.cat(os.path.join(tempd, 'Dockerfile'))
        print(r.stdout)
        sh.docker.build('-t', self.get_tagname("test"), tempd)
        try:
            pass
        except Exception as e:
            raise e
        finally:
            shutil.rmtree(tempd)

    def run_commands(self, command):
        sh.docker.run(
            '--rm',
            '-v', "%s:/src" % os.path.abspath('.'),
            '-w', '/src', self.get_tagname('test'), *command)

    def build_base_image(self):
        image_name = self.get_tagname("base")
        sh.docker.build('-t', image_name, '.')
        return image_name

    def run(self, image, command):
        print("Going to run {0} in {1}".format(command.test_command(), image))
        if self.args.rebuild:
            print("Need to rebuild")
        try:
            if image is None:
                image = self.build_base_image()
            print("Test image {0} with {1}".format(
                image, command.prep_commands()))
            self.build_test_image(image, command)
        except sh.ErrorReturnCode as e:
            print("build failed", e.message)
            return 1
        try:
            self.run_commands(shlex.split(command.test_command()))
        except sh.ErrorReturnCode as e:
            print("run failed")
            print(e.stderr)
            return 1
