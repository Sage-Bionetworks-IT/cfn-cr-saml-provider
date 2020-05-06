import boto3
import json
import logging
import requests

from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(
    json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

try:
    client = boto3.client("iam")
except Exception as e:
    helper.init_failure(e)

def get_parameters(event):
    name = event['ResourceProperties']['Name']
    url = event['ResourceProperties']['URL']
    if 'Metadata' in event['ResourceProperties']:
        metadata = event['ResourceProperties']['Metadata']
    else:
        metadata = get_metadata(url)

    return name, metadata, url

def get_metadata(url):
    response = requests.get(url)
    metadata = response.text
    logger.info("metadata = " + metadata)
    if response.status_code == 200:
        return metadata

def create_provider(name, metadata, url):
    response = client.create_saml_provider(
        Name=name,
        SAMLMetadataDocument=metadata
    )
    physical_resource_id = response['SAMLProviderArn']
    logger.info("created SAML provider " + physical_resource_id)
    return physical_resource_id

@helper.create
def create(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    return create_provider(*get_parameters(event))

@helper.delete
def delete(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    physical_resource_id = event['PhysicalResourceId']
    logger.info("deleting SAML provider " + physical_resource_id)
    client.delete_saml_provider(
        SAMLProviderArn=physical_resource_id
    )

@helper.update
def update(event, context):
    logger.debug("Received event: " + json.dumps(event, sort_keys=False))
    physical_resource_id = event['PhysicalResourceId']
    new_properties = event['ResourceProperties']

    if 'Metadata' in new_properties:
        metadata = new_properties['Metadata']
    else:
        metadata = get_metadata(new_properties['URL'])

    response = client.update_saml_provider(
        SAMLProviderArn=physical_resource_id,
        SAMLMetadataDocument=metadata
    )
    physical_resource_id = response['SAMLProviderArn']
    logger.info("updated SAML provider " + physical_resource_id)
    return physical_resource_id

def lambda_handler(event, context):
    helper(event, context)
