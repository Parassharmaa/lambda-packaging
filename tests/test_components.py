from unittest import TestCase
from unittest.mock import patch
from lambda_packaging.components import LambdaPackage
import pulumi
import shutil
from pathlib import Path


class ResourceMock(pulumi.runtime.Mocks):
    def call(self, token, args, provider):
        return {}

    def new_resource(self, type_, name, inputs, provider, id_):
        return ["", {}]


pulumi.runtime.set_mocks(ResourceMock())

test_hash_1 = "3fboMxcOb49OZuu95c5i6yfI6VZ8bo7RbLeKTOlRHpo="
test_hash_2 = "hEnQV9VhzoU0v2r9EEfCQPx3htO3BYcWEdiQOzwp7Os="
test_hash_3 = "5yDFAKYBmDzD/xwf+qHihYSUhwaAanqDzp5ptBc1NNk="


class TestComponents(TestCase):
    @pulumi.runtime.test
    def test_lambda_package(self):
        with patch("lambda_packaging.components.os") as mock_os:
            mock_os.path.dirname.return_value = Path("tests/data")
            lambda_package = LambdaPackage(
                name="example-test",
                layer=False,
                exclude=["requirements*.txt"],
                requirements_path="requirements_test_1.txt",
            )

            self.assertEqual(
                lambda_package.package_archive,
                "tests/data/dist/stack-example-test-lambda.zip",
            )
            self.assertEqual(
                lambda_package.package_hash, test_hash_1,
            )

    @pulumi.runtime.test
    def test_lambda_package_with_layer(self):
        with patch("lambda_packaging.components.os") as mock_os:
            mock_os.path.dirname.return_value = Path("tests/data")
            lambda_package = LambdaPackage(
                name="example-test",
                layer=True,
                exclude=["**/requirements*.txt"],
                requirements_path="requirements_test_1.txt",
            )

            self.assertEqual(
                lambda_package.package_archive,
                "tests/data/dist/stack-example-test-lambda.zip",
            )

            self.assertEqual(
                lambda_package.layer_archive_path,
                "tests/data/dist/stack-example-test-requirements.zip",
            )
            self.assertEqual(lambda_package.package_hash, test_hash_2)

            self.assertEqual(lambda_package.layer_hash, test_hash_3)

    def tearDown(self):
        shutil.rmtree("tests/data/dist/", ignore_errors=True)
