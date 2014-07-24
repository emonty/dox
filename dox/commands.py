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
    'get_commands',
    'Commands',
]

import dox.config.dox_yaml
import dox.config.tox_ini
import dox.config.travis_yaml


def get_commands():
    '''Examine the local environment and figure out what we should run.'''

    dox_yaml = dox.config.dox_yaml.get_dox_yaml()
    tox_ini = dox.config.tox_ini.get_tox_ini()
    travis_yaml = dox.config.travis_yaml.get_travis_yaml()

    commands = None
    for source in (dox_yaml, tox_ini, travis_yaml):
        if commands is None and source.exists():
            commands = source.get_commands(commands)
    return commands


class Commands(object):

    def __init__(self):
        self.commands = get_commands()
        self.args = []

    def __str__(self):
        if hasattr(self.commands, 'append'):
            return "\n".join(self.commands)
        return self.commands + ' ' + ' '.join(self.args)

    def append(self, args):
        self.args = args