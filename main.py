#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack
# from imports.aws.provider import AwsProvider
# from imports.aws.dynamodb import dynamodb
from cdktf_cdktf_provider_aws.dynamodb_table import DynamodbTable
from cdktf_cdktf_provider_aws.dynamodb_table_item import DynamodbTableItem
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.opensearch_domain import OpensearchDomain,OpensearchDomainClusterConfig,OpensearchDomainClusterConfigZoneAwarenessConfig,OpensearchDomainEbsOptions
import json

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here
        AwsProvider(self, 'Aws', region='us-east-1')
        
        table=DynamodbTable(
            self, 
            'Oslashtable',
            name='Oslashtable',
            read_capacity=1,
            write_capacity=1,
            hash_key='Id',
            # range_key='Date',
            attribute= [
              { 'name' :'Id', 'type' : 'S' },
            #   { 'name' :'Date', 'type' : 'N' },
            ],
            
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
            # range_key='Date',
            item = json.dumps(itemv1),
            )
            
            
            ############################opensearch##########
            
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
            )
            
            
            )
            
        


app = App()
MyStack(app, "cdktf-oslash")

app.synth()
