# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yaml
import sys

from blueprint.lib.validator import BPError
from blueprint.lib import event

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

#========================================================================
class Source(dict):
    def __init__(self, type, git, catalog=None):
        self.source_type = type
        self.git = git
        if(catalog != None):
            self.catalog = catalog

    def __str__(self):
        return f'Git({self.source_type}: {self.git})'

    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if self.source_type == None:
            del self.source_type
        if self.git == None:
            del self.git
        if self.catalog == None:
            del self.catalog

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        eprint(errors)
        return yaml.dump(self, sort_keys=False)

    @classmethod
    def from_json(cls, data):
        source_type = data['source_type']
        try:
            git = GitSource.from_json(data['git'])
        except KeyError:
            git = None
        try:
            catalog = CatalogSource.from_json(data['catalog'])
        except KeyError:
            catalog = None

        return cls(source_type, git, catalog)

    def validate(self, level=BPError):
        source_errors = []
        # TODO: Add a Source validator
        return source_errors

#========================================================================

class GitSource:
    def __init__(self, repo_url, branch=None, token=None):
        self.git_repo_url = repo_url
        if branch!=None:
            self.git_branch = branch
        if token!=None:
            self.git_token = token

    def __str__(self):
        return f'GitSource({self.git_repo_url}: {self.git_branch})'

    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if self.git_repo_url == None:
            del self.git_repo_url
        if self.git_branch == None:
            del self.git_branch
        if self.git_token == None:
            del self.git_token

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        eprint(errors)
        return yaml.dump(self, sort_keys=False)

    @classmethod
    def from_json(cls, data):
        try:
            git_repo_url = data['git_repo_url']
        except KeyError:
            git_repo_url = None
        
        try:
            git_branch = data['git_branch']
        except KeyError:
            git_branch = None

        return cls(git_repo_url, git_branch)

    def validate(self, level=BPError):
        source_errors = []
        # TODO: Add a GitSource validator
        return source_errors

#========================================================================
class CatalogSource:
    def __init__(self, catalog_id, offering_id, offering_version):
        self.catalog_id = catalog_id
        self.offering_id = offering_id
        self.offering_version = offering_version

    def __str__(self):
        return f'Git({self.catalog_id}: {self.offering_id}, {self.offering_version})'

    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if self.catalog_id == None:
            del self.catalog_id
        if self.offering_id == None:
            del self.offering_id
        if self.offering_version == None:
            del self.offering_version

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        eprint(errors)
        return yaml.dump(self, sort_keys=False)

    @classmethod
    def from_json(cls, data):
        try:
            catalog_id = data['catalog_id']
        except KeyError:
            catalog_id = None

        try:
            offering_id = data['offering_id']
        except KeyError:
            offering_id = None

        try:
            offering_version = data['offering_version']
        except KeyError:
            offering_version = None

        return cls(catalog_id, offering_id, offering_version)

    def validate(self, level=BPError):
        source_errors = []
        # TODO: Add a Catalog Source validator
        return source_errors

#========================================================================
