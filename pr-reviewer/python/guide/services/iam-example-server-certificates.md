> This work is licensed under a Creative Commons
> Attribution-NonCommercial-ShareAlike 4.0 International License (the
> \"License\"). You may not use this file except in compliance with the
> License. A copy of the License is located at
> <http://creativecommons.org/licenses/by-nc-sa/4.0/>.
>
> This file is distributed on an \"AS IS\" BASIS, WITHOUT WARRANTIES OR
> CONDITIONS OF ANY KIND, either express or implied. See the License for
> the specific language governing permissions and limitations under the
> License.

# Working with IAM server certificates {#aws-boto3-iam-examples-server-certs}

This Python example shows you how to carry out basic tasks in managing
server certificates for HTTPS connections.

## The scenario

To enable HTTPS connections to your website or application on AWS, you
need an SSL/TLS server certificate. To use a certificate that you
obtained from an external provider with your website or application on
AWS, you must upload the certificate to IAM or import it into AWS
Certificate Manager.

In this example, python code is used to handle server certificates in
IAM. The code uses the Amazon Web Services (AWS) SDK for Python to
manage server certificates using these methods of the IAM client class:

-   [get_paginator(\'list_server_certificates\')](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.update_access_key).
-   [get_server_certificate](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.get_server_certificate).
-   [update_server_certificate](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.update_server_certificate).
-   [delete_server_certificate](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.delete_server_certificate).

All the example code for the Amazon Web Services (AWS) SDK for Python is
available [here on
GitHub](https://github.com/awsdocs/aws-doc-sdk-examples/tree/master/python/example_code).

For more information about server certificates, see [Working with Server
Certificates](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_server-certs.html)
in the *IAM User Guide*.

Prerequisite tasks =================

To set up and run this example, you must first configure your AWS
credentials, as described in `quickstart`{.interpreted-text role="doc"}.

## List your server certificates

List the server certificates stored in IAM. If none exist, the action
returns an empty list.

The example below shows how to:

-   List server certificates using
    [get_paginator(\'list_server_certificates\')](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.get_paginator).

For more information about paginators see,
`paginators`{.interpreted-text role="doc"}

### Example

``` python
import boto3

# Create IAM client
iam = boto3.client('iam')

# List server certificates through the pagination interface
paginator = iam.get_paginator('list_server_certificates')
for response in paginator.paginate():
    print(response['ServerCertificateMetadataList'])
```

## Get a server certificate

Get information about the specified server certificate stored in IAM.

The example below shows how to:

-   Get a server certificate using
    [get_server_certificate](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.get_server_certificate).

### Example

``` python
import boto3


# Create IAM client
iam = boto3.client('iam')

# Get the server certificate
response = iam.get_server_certificate(ServerCertificateName='CERTIFICATE_NAME')
print(response['ServerCertificate'])
```

## Update a server certificate

Update the name and/or the path of the specified server certificate
stored in IAM.

The example below shows how to:

-   Update a server certificate using
    [update_server_certificate](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.update_server_certificate).

### Example

``` python
import boto3

# Create IAM client
iam = boto3.client('iam')

# Update the name of the server certificate
iam.update_server_certificate(
    ServerCertificateName='CERTIFICATE_NAME',
    NewServerCertificateName='NEW_CERTIFICATE_NAME'
)
```

## Delete a server certificate

Delete the specified server certificate.

The example below shows how to:

-   Delete a server certificate using
    [delete_server_certificate](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.delete_server_certificate).

### Example

``` python
import boto3


# Create IAM client
iam = boto3.client('iam')

# Delete the server certificate
iam.delete_server_certificate(
    ServerCertificateName='CERTIFICATE_NAME'
)
```
