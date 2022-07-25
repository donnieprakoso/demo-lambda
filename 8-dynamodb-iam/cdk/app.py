from constructs import Construct
import aws_cdk as core
from aws_cdk import (App, Stack, aws_lambda as _lambda, aws_dynamodb as
                     _ddb, aws_iam as _iam, aws_lambda_event_sources as _lambdasources)


class DynamoDbIam(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Model all required resources
        ddb_table = _ddb.Table(
            self,
            id='{}-data'.format(id),
            table_name='{}-data'.format(id),
            partition_key=_ddb.Attribute(name='ID',
                                         type=_ddb.AttributeType.STRING),
            removal_policy=core.RemovalPolicy.
            DESTROY,  # THIS IS NOT RECOMMENDED FOR PRODUCTION USE
            read_capacity=1,
            write_capacity=1)

        # IAM Roles
        lambda_role = _iam.Role(
            self,
            id='{}-lambda-role'.format(id),
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
            "{}-function-saveData".format(id),
            code=_lambda.AssetCode("../lambda-functions/save-data"),
            handler="app.handler",
            timeout=core.Duration.seconds(60),
            role=lambda_role,
            tracing=_lambda.Tracing.ACTIVE,
            runtime=_lambda.Runtime.PYTHON_3_8)
        fnLambda_saveData.add_environment("TABLE_NAME", ddb_table.table_name)

        core.CfnOutput(self,
                       "{}-output-dynamodbTable".format(id),
                       value=ddb_table.table_name,
                       export_name="{}-ddbTable".format(id))
        core.CfnOutput(self,
                       "{}-output-lambda".format(id),
                       value=fnLambda_saveData.function_name,
                       export_name="{}-lambdaFunctionName".format(id))


app = App()
DynamoDbIam(app, "dynamodb-iam")
app.synth()
