#!/usr/bin/env python3
from constructs import Construct
from aws_cdk import App, Stack
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_dynamodb as _ddb
# from aws_cdk import aws_apigatewayv2 as _agv2
# TODO: Be mindful that it's using Alpha version of CDK. Need to migrate into stable.
from aws_cdk import aws_apigatewayv2_alpha as _agv2
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
import aws_cdk as core


class CdkStack(Stack):
    def __init__(self, scope: Construct, id: str, stack_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Model all required resources
        ddb_table = _ddb.Table(
            self,
            id='{}-data'.format(stack_prefix),
            table_name='{}-data'.format(stack_prefix),
            partition_key=_ddb.Attribute(name='ID',
                                         type=_ddb.AttributeType.STRING),
            removal_policy=core.RemovalPolicy.
            DESTROY,  # THIS IS NOT RECOMMENDED FOR PRODUCTION USE
            billing_mode=_ddb.BillingMode.PROVISIONED)

        # Setting up autoscaling for DynamoDB
        read_scaling = ddb_table.auto_scale_read_capacity(min_capacity=1, max_capacity=100)
        read_scaling.scale_on_utilization(target_utilization_percent=10)

        write_scaling = ddb_table.auto_scale_write_capacity(min_capacity=1, max_capacity=100)
        write_scaling.scale_on_utilization(target_utilization_percent=10)

    # IAM Roles
        lambda_role = _iam.Role(
            self,
            id='{}-lambda-role'.format(stack_prefix),
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))

        cw_policy_statement = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        cw_policy_statement.add_actions("logs:CreateLogGroup")
        cw_policy_statement.add_actions("logs:CreateLogStream")
        cw_policy_statement.add_actions("logs:PutLogEvents")
        cw_policy_statement.add_actions("logs:DescribeLogStreams")
        cw_policy_statement.add_resources("*")
        lambda_role.add_to_policy(cw_policy_statement)

        # Add role for DynamoDB
        dynamodb_policy_statement = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW)
        dynamodb_policy_statement.add_actions("dynamodb:PutItem")
        dynamodb_policy_statement.add_actions("dynamodb:GetItem")
        dynamodb_policy_statement.add_actions("dynamodb:UpdateItem")
        dynamodb_policy_statement.add_actions("dynamodb:DeleteItem")
        dynamodb_policy_statement.add_actions("dynamodb:Scan")
        dynamodb_policy_statement.add_actions("dynamodb:Query")
        dynamodb_policy_statement.add_actions("dynamodb:ConditionCheckItem")
        dynamodb_policy_statement.add_resources(ddb_table.table_arn)
        lambda_role.add_to_policy(dynamodb_policy_statement)

        # AWS Lambda Functions
        fnLambda_saveData = _lambda.Function(
            self,
            "{}-function-saveData".format(stack_prefix),
            code=_lambda.AssetCode("../lambda-functions/save-data"),
            handler="app.handler",
            timeout=core.Duration.seconds(60),
            role=lambda_role,
            tracing=_lambda.Tracing.ACTIVE,
            runtime=_lambda.Runtime.PYTHON_3_8)
        fnLambda_saveData.add_environment("TABLE_NAME", ddb_table.table_name)

        fnLambda_listData = _lambda.Function(
            self,
            "{}-function-listData".format(stack_prefix),
            code=_lambda.AssetCode("../lambda-functions/list-data"),
            handler="app.handler",
            timeout=core.Duration.seconds(60),
            role=lambda_role,
            tracing=_lambda.Tracing.ACTIVE,
            runtime=_lambda.Runtime.PYTHON_3_8)
        fnLambda_listData.add_environment("TABLE_NAME", ddb_table.table_name)

        http_api = _agv2.HttpApi(self,
                                 id="{}-api-gateway".format(stack_prefix),
                                 description="HTTP API Gateway")

        int_saveData = HttpLambdaIntegration(
            "{}-httpint-save".format(stack_prefix), fnLambda_saveData)
        int_listData = HttpLambdaIntegration(
            "{}-httpint-list".format(stack_prefix), fnLambda_listData)

        http_api.add_routes(path="/data",
                            methods=[_agv2.HttpMethod.GET],
                            integration=int_listData)

        # This route is using GET method just to make it easier testing using Artillery tool. In practice, you should change this to POST method.
        http_api.add_routes(path="/data/save",
                            methods=[_agv2.HttpMethod.GET],
                            integration=int_saveData)

        core.CfnOutput(self,
                       "{}-output-dynamodbTable".format(stack_prefix),
                       value=ddb_table.table_name,
                       export_name="{}-ddbTable".format(stack_prefix))
        core.CfnOutput(self,
                       "{}-output-apiEndpointURL".format(stack_prefix),
                       value=http_api.url,
                       export_name="{}-apiEndpointURL".format(stack_prefix))


stack_prefix = 'lambda-dynamodb-autoscale'
app = core.App()
stack = CdkStack(app, stack_prefix, stack_prefix=stack_prefix)
core.Tags.of(stack).add('Name', stack_prefix)

app.synth()
