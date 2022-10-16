#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack
from cdktf_cdktf_provider_aws.dynamodb_table import DynamodbTable,DynamodbTableServerSideEncryption
from cdktf_cdktf_provider_aws.dynamodb_table_item import DynamodbTableItem
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.opensearch_domain import OpensearchDomain,OpensearchDomainNodeToNodeEncryption,\
OpensearchDomainClusterConfig,OpensearchDomainClusterConfigZoneAwarenessConfig,OpensearchDomainEbsOptions,OpensearchDomainEncryptAtRest,\
OpensearchDomainAdvancedSecurityOptions,OpensearchDomainAdvancedSecurityOptionsMasterUserOptions
from cdktf_cdktf_provider_aws.sns_topic import SnsTopic
from cdktf_cdktf_provider_aws.sns_topic_subscription import SnsTopicSubscription
from cdktf_cdktf_provider_aws.kms_key import KmsKey
from cdktf_cdktf_provider_aws.cloudwatch_metric_alarm import CloudwatchMetricAlarm
from cdktf_cdktf_provider_aws.cloudwatch_log_metric_filter import CloudwatchLogMetricFilter
from cdktf_cdktf_provider_aws.data_aws_iam_role import DataAwsIamRole
import json

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)
        region='us-east-1'
        AwsProvider(self, 'Aws', region=region)
        tags={
                'Project':'Oslash'
            }
        
        ############ Dyanmo DB Table ###############
        ddbkmskey=KmsKey(self, 'KMSforDyanmoDB',description="KMS key to Encrypt the DyanmoDB")
        table=DynamodbTable(
            self, 
            'Oslashtable',
            name='Oslashtable',
            read_capacity=1,
            write_capacity=1,
            hash_key='Id',
            server_side_encryption=DynamodbTableServerSideEncryption(
                enabled=True,
                kms_key_arn=ddbkmskey.arn),
            replica= [{
                'regionName' : "us-east-2",
                'kms_key_arn' : ddbkmskey.arn
                
            }],
            attribute= [
              { 'name' :'Id', 'type' : 'S' },
            ],
            tags=tags
            )
            
            
        itemv1= {
                  "Id": {"S": "dsfjhdkhljsdh"},
                  "Date": {"N": "11111"},
                  "two": {"N": "22222"},
                  "three": {"N": "33333"},
                  "four": {"N": "44444"}
                }

        DynamodbTableItem(
            self, 
            'Oslashtableitem',
            hash_key='Id',
            table_name=table.name,
            item = json.dumps(itemv1),
            )
            
            
        ###########################opensearch##########
        OpenSearchkmskey=KmsKey(self, 'KMSforOpenSearch',description="KMS key to Encrypt the Open Search Domain")   
        OpenSearchMasterRole=DataAwsIamRole(self, 'MsterIAMUserforOS',name='AWSServiceRoleForAmazonOpenSearchService')
        OpensearchDomain(
            self, 
            'OpenseachDomain',
            domain_name = "akhilcdktfdomainname",
            count=1,
            ebs_options= OpensearchDomainEbsOptions(
                ebs_enabled= True,
                volume_size=10,
                volume_type='gp3',
                ),
            cluster_config= OpensearchDomainClusterConfig(
                instance_count=1,
                instance_type="t3.small.search",
                zone_awareness_config= OpensearchDomainClusterConfigZoneAwarenessConfig(
                    availability_zone_count=2,
                    )
            ),
            tags=tags,
            node_to_node_encryption=OpensearchDomainNodeToNodeEncryption(enabled=True),
            encrypt_at_rest=OpensearchDomainEncryptAtRest(enabled=True,kms_key_id=OpenSearchkmskey.key_id),
            engine_version="1.3",
            
            advanced_security_options=OpensearchDomainAdvancedSecurityOptions(
                enabled=True,
                anonymous_auth_enabled=True,
                internal_user_database_enabled=False,
                master_user_options=OpensearchDomainAdvancedSecurityOptionsMasterUserOptions(master_user_arn=OpenSearchMasterRole.arn))
            )
            
        ####################### Monitoring #############
        
        kmskey=KmsKey(self, 'KMSforSNS',description="KMS key to Encrypt the SNS Topic")
        snstopic=SnsTopic(self, 'OpenseachAlertTopic', display_name='OpenseachAlertTopic-oslash',name='OpenseachAlertTopic-oslash',kms_master_key_id=kmskey.key_id,tags=tags)
        SnsTopicSubscription(self, 'OpenseachAlertTopicSubcription',endpoint='emailid@emaildomain.com',protocol='email',topic_arn=snstopic.arn)
        
        # CloudwatchLogMetricFilter(self, 'opensearchMetricfilter', name='opensearchMetricfilter', metric_transformation=,pattern=)
        CloudwatchMetricAlarm(self, 'opensearchMetricfilter',alarm_name="opensearchMetricfilter",
        comparison_operator='GreaterThanOrEqualToThreshold',
        evaluation_periods=1,
        alarm_actions=[snstopic.arn],
        actions_enabled = True,
        alarm_description="will send an alert if threshold crosses 70",
        namespace='AWS/ES',
        metric_name='CPUUtilization',
        statistic="Average",
        period=60,
        threshold=70,
        )
        
        
            

app = App()
MyStack(app, "cdktf-oslash")

app.synth()
