# This custom resource is deprecated, please use the [AWS officially supported SAML resource provider](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-samlprovider.html)

# Overview
A CloudFormation custom resource provider for creating a SAML identity provider.

# Usage
The `Custom::SAMLProvider` creates IAM SAM Provider.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
  Type: Custom::SAMLProvider
  Properties:
    Name: String
    ServiceToken: !ImportValue
        'Fn::Sub': '${AWS::Region}-cfn-cr-saml-provider-FunctionArn'
    Metadata: String
    URL: String
```

It will create a SAML provider named `Name` using the `Metadata` literal or the content
of the metadata `URL`.

__Note__: The name of the saml provider cannot be changed once deployed because the
boto3 [update_saml_provider API](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.update_saml_provider)
does not support that.  The only way to rename is to remove then re-deploy the provider.


## Properties
You can specify the following properties:

    "Name" - of the SAML provider (required)
    "ServiceToken" - pointing to the function implementing this (required)
    "Metadata" - for the SAML Provider (required if URL is missing)
    "URL" - serving the metadata of the SAML Provider (required if Metadaga is missing)

## Return values
When you pass the logical ID of this resource to the intrinsic Ref function, Ref returns the resource ARN.

### Fn::GetAtt
The Fn::GetAtt intrinsic function returns:

    "Name" - Name of the SAML provider

## Install
Execute the below template snippet to deploy the SAML provider and associated role to an AWS account.

```yaml
  SandboxAdminSamlProvider:
    Type : Custom::SAMLProvider
    Properties:
      ServiceToken: !ImportValue
        'Fn::Sub': '${AWS::Region}-cfn-cr-saml-provider-FunctionArn'
      Name: "itsandbox-admin"
      Metadata: !Ref ItsandboxAdminMetadata
      URL: ""
  SandboxAdminSamlProviderRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !GetAtt SandboxAdminSamlProvider.Name
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AdministratorAccess
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Federated: !GetAtt SandboxAdminSamlProvider.Arn
            Action: sts:AssumeRoleWithSAML
            Condition:
              StringEquals:
                "SAML:aud": "https://signin.aws.amazon.com/saml"
```

__NOTE__: The `ManagedPolicyArns` in this example provider is associated to an admin role

## Development

### Contributions
Contributions are welcome.

### Requirements
Run `pipenv install --dev` to install both production and development
requirements, and `pipenv shell` to activate the virtual environment. For more
information see the [pipenv docs](https://pipenv.pypa.io/en/latest/).

After activating the virtual environment, run `pre-commit install` to install
the [pre-commit](https://pre-commit.com/) git hook.

### Create a local build

```shell script
$ sam build --use-container
```

### Run locally

```shell script
$ sam local invoke Function --event events/event.json
```

### Run unit tests
Tests are defined in the `tests` folder in this project. Use PIP to install the
[pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```shell script
$ python -m pytest tests/ -v
```

## Deployment

### Build

```shell script
sam build
```

## Deploy Lambda to S3
This requires the correct permissions to upload to bucket
`bootstrap-awss3cloudformationbucket-19qromfd235z9` and
`essentials-awss3lambdaartifactsbucket-x29ftznj6pqw`

```shell script
sam package --template-file .aws-sam/build/template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file .aws-sam/build/cfn-cr-saml-provider.yaml

aws s3 cp .aws-sam/build/cfn-cr-saml-provider.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/cfn-cr-saml-provider/master/
```

## Install Lambda into AWS
Create the following [sceptre](https://github.com/Sceptre/sceptre) file

config/prod/cfn-cr-saml-provider.yaml
```yaml
template_path: "remote/cfn-cr-saml-provider.yaml"
stack_name: "cfn-cr-saml-provider"
stack_tags:
  Department: "Platform"
  Project: "Infrastructure"
  OwnerEmail: "it@sagebase.org"
hooks:
  before_launch:
    - !cmd "curl https://s3.amazonaws.com/bootstrap-awss3cloudformationbucket-19qromfd235z9/cfn-cr-saml-provider/master/cfn-cr-saml-provider.yaml --create-dirs -o templates/remote/cfn-cr-saml-provider.yaml"
```

Install the lambda using sceptre:
```shell script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/cfn-cr-saml-provider.yaml
```

## Acknowledgements
This custom resource was inspired by the [bixio cfn-saml-provider](https://github.com/binxio/cfn-saml-provider).
The main difference with this one is that it usses the [crhelper](https://github.com/aws-cloudformation/custom-resource-helper)
library instead of bixio's [cfn_resource_provider](https://github.com/binxio/cfn-resource-provider) lib.
