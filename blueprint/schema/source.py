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

from blueprint.lib import event

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

GitSourceType = "github"
CatalogSourceType = "catalog"

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

#========================================================================
class GitSource:
    def __init__(self,
                repo_url: str   = "https://github.com/Cloud-Schematics/blueprint-example-modules/tree/main/IBM-DefaultResourceGroup",
                branch: str     = None, 
                token: str      = None):
        """Git template source details.

        :param repo_url: Name of the template source
        :param branch: Git source details (type: source.GitSource)
        :param token: Catalog source details (type: source.CatalogSource)
        """

        self.git_repo_url = repo_url
        if branch!=None:
            self.git_branch = branch
        if token!=None:
            self.git_token = token

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.repo_url = "__init__"

    def __str__(self):
        return f'GitSource({self.git_repo_url}: {self.git_branch})'

    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if hasattr(self, 'git_repo_url') and self.git_repo_url == None:
            del self.git_repo_url
        if hasattr(self, 'git_branch') and self.git_branch == None:
            del self.git_branch
        if hasattr(self, 'git_token') and self.git_token == None:
            del self.git_token

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, data):
        try:
            git_repo_url = data['git_repo_url']
        except KeyError:
            git_repo_url = None
        
        try:
            git_branch = data['git_branch']
        except KeyError:
            git_branch = None

        return cls(git_repo_url, git_branch)

    def validate(self, level=event.BPError):
        source_errors = []
        # TODO: Add a GitSource validator
        return source_errors

#========================================================================
class CatalogSource:
    def __init__(self, 
                catalog_id: str         = "__init__",
                offering_id: str        = None, 
                offering_version: str   = None):
        """Catalog template source details.

        :param catalog_id: Id of the IBM Cloud Catalog (private catalog)
        :param offering_id: Id of the offering (software or template) in the catalog
        :param offering_version: Version of the offering (software or template) in the catalog
        """

        self.catalog_id = catalog_id
        self.offering_id = offering_id
        self.offering_version = offering_version

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.catalog_id = "__init__"

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
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, data):
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

    def validate(self, level=event.BPError):
        source_errors = []
        # TODO: Add a Catalog Source validator
        return source_errors

#========================================================================

class TemplateSource(dict):
    def __init__(self,
                type: str                   = GitSourceType, 
                git: GitSource          = None, 
                catalog: CatalogSource  = None):
        """Template source for the module.

        :param type: Name of the template source
        :param git: Git source details (type: source.GitSource)
        :param catalog: Catalog source details (type: source.CatalogSource)
        """

        self.source_type = type
        self.git = git
        if(catalog != None):
            self.catalog = catalog

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.type = GitSourceType

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
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, data):
        source_type = data['source_type']
        try:
            git = GitSource.from_yaml(data['git'])
        except KeyError:
            git = None
        try:
            catalog = CatalogSource.from_yaml(data['catalog'])
        except KeyError:
            catalog = None

        return cls(source_type, git, catalog)

    def validate(self, level=event.BPError):
        source_errors = []
        # TODO: Add a Source validator
        return source_errors

#========================================================================