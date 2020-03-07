import zipfile
import glob
import os
import pulumi
from os import path
import stat
import fnmatch
from .utils import format_resource_name, format_file_name


IGNORE_PATTERNS = ['*.py[c|o]', '*/__pycache__*', '*.dist-info*']


class ZipPackage:
    """
    Creates Zip archive and injects requirements into the zip archive.
    """

    def __init__(self,
                 resource_name,
                 project_root,
                 include=["**"],
                 exclude=[],
                 target_folder='.plp/',
                 install_folder='requirements/'
                 ):
        self.resource_name = resource_name
        self.project_root = project_root
        self.target_folder = target_folder
        self.install_folder = path.join(target_folder, install_folder)
        self.zipfile_name = format_file_name(resource_name, 'lambda.zip')
        self.zip_path = self.get_path(self.zipfile_name)
        self.include = include
        self.exclude = exclude
        self.install_path = path.join(self.project_root, self.install_folder)

        self.exclude.append(path.join(self.target_folder, "**"))
        self.installed_requirements = path.join(
            self.project_root, self.install_folder)

        # create temporary directory if not exists
        if not os.path.isdir(self.installed_requirements):
            os.makedirs(self.installed_requirements, exist_ok=True)

    def get_path(self, file_name):
        """Return absolute file path"""
        return path.join(self.project_root, self.target_folder, file_name)

    def _match_glob_files(self, patterns: list):
        """
        Returns list of files matching the glob pattern
        """
        return [f for pattern in patterns
                for f in glob.glob(os.path.join(self.project_root, pattern), recursive=True)
                ]

    def filter_package(self):
        """
        Filters files based on exclude and include option
        """
        self.exclude_files = self._match_glob_files(self.exclude)
        self.include_files = self._match_glob_files(self.include)

        filtered_package = []
        if "**" in self.exclude:
            filtered_package = set(self.include_files)
        else:
            filtered_package = set(self.include_files) - \
                set(self.exclude_files)
        return filtered_package

    def zip_package(self, requirements=True):
        """
        Creates zip archive of file and folders
        and inject requirements into the zip package when "requirements=True"
        """
        self._add_files(self.zip_path, self.filter_package(),
                        'w', self.project_root)
        if requirements:
            self._inject_requirements()
        return self.zip_path

    def zip_requirements(self):
        """
        Creates zip archive of dependencies requirements
        """
        requirement_files = glob.glob(os.path.join(
            self.installed_requirements, '**'), recursive=True)
        requirements_zip_path = self.get_path(
            format_file_name(self.resource_name, 'requirements.zip'))
        self._add_files(requirements_zip_path, requirement_files,
                        base_path=self.installed_requirements)
        return requirements_zip_path

    def _add_files(self, zip_path, files, mode='w', base_path=""):
        """
        Utility function to add new files in existing/new zip
        """
        zip_file = zipfile.ZipFile(zip_path, mode)

        for file in sorted(files):
            if self.is_file_allowed(file):
                zip_path = os.path.relpath(file, base_path)
                permission = 0o555 if os.access(file, os.X_OK) else 0o444
                zip_info = zipfile.ZipInfo.from_file(file, zip_path)
                zip_info.date_time = (2020, 1, 1, 0, 0, 0)
                zip_info.external_attr = (stat.S_IFREG | permission) << 16

                if os.path.isfile(file):
                    with open(file, "rb") as fp:
                        zip_file.writestr(
                            zip_info,
                            fp.read(),
                            compress_type=zipfile.ZIP_DEFLATED
                        )

        zip_file.close()

    def is_file_allowed(self, file_name):
        for pattern in IGNORE_PATTERNS:
            if fnmatch.fnmatch(file_name, pattern):
                return False
        return True

    def _inject_requirements(self):
        """
        Inject requirements into the package archive.
        """
        requirement_files = glob.glob(os.path.join(
            self.installed_requirements, '**'), recursive=True)
        self._add_files(
            zip_path=self.zip_path,
            files=requirement_files,
            mode='a',
            base_path=self.installed_requirements
        )
