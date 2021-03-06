# Overview

Pulumi-based python solution for Packaging an AWS Lambda and its Layer.

## Directory Structure
```
├── README.md
├── example
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.yaml
│   ├── __main__.py
│   └── requirements.txt
├── lambda_packaging
│   ├── __init__.py
│   ├── components.py
│   ├── pip_requirements.py
│   ├── utils.py
│   └── zip_package.py
├── requirements.txt
├── setup.cfg
├── setup.py
└── tests
```

## Installation
```
$ pip install lambda-packaging
```
## Quick Start

### LambdaPackage
Creates a zip package of project files and install dependencies from requirements.txt.

Use "dockerize=True" to pip install requirements using lambda environment docker image.

Use "layer=True" to package dependencies and code seperately.

Example: 

```python

...

...


lambda_package = LambdaPackage(
    name='example-test',
    no_deploy=['pulumi', 'pulumi_aws', 'pulumi_docker'],
    exclude=['__main__.py']
)




# Create Lambda function
function = lambda_.Function(
    resource_name='function',
    role=role.arn,
    runtime='python3.6',
    description=f'Lambda function running the f`{pulumi.get_project()}` ({pulumi.get_stack()}) project',
    handler='handler.lambda_handler',
    code=lambda_package.package_archive
)

# path of package archive and dependencies package
# containing installed requirements
pulumi.export("package_archive_path", lambda_package.package_archive)
pulumi.export("layer_archive_path", lambda_package.layer_archive_path)

```

```bash
$ pulumi up
```

### Run Tests
```
$ python3 -m unittest discover
```