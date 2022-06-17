#!/usr/bin/env python3

from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_destinations as _lambdadest
from aws_cdk import core


class CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, stack_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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

        # IAM Roles
        lambda_role_dest = _iam.Role(
            self,
            id='{}-lambda-role-dest'.format(stack_prefix),
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))

        cw_policy_statement = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        cw_policy_statement.add_actions("logs:CreateLogGroup")
        cw_policy_statement.add_actions("logs:CreateLogStream")
        cw_policy_statement.add_actions("logs:PutLogEvents")
        cw_policy_statement.add_actions("logs:DescribeLogStreams")
        cw_policy_statement.add_resources("*")
        lambda_role_dest.add_to_policy(cw_policy_statement)
        # AWS Lambda Functions
        fnLambda_main = _lambda.Function(
            self,
            "{}-fn-main".format(stack_prefix),
            function_name="{}-fn-main".format(stack_prefix),
            code=_lambda.AssetCode("../lambda-functions/main/"),
            handler="main.handler",
            timeout=core.Duration.seconds(60),
            role=lambda_role,
            runtime=_lambda.Runtime.PYTHON_3_8)

        fnLambda_success = _lambda.Function(
            self,
            "{}-fn-success".format(stack_prefix),
            function_name="{}-fn-success".format(stack_prefix),
            code=_lambda.AssetCode("../lambda-functions/success/"),
            handler="success.handler",
            role=lambda_role_dest,
            timeout=core.Duration.seconds(60),
            runtime=_lambda.Runtime.PYTHON_3_8)

        fnLambda_failure = _lambda.Function(
            self,
            "{}-fn-failure".format(stack_prefix),
            function_name="{}-fn-failure".format(stack_prefix),
            code=_lambda.AssetCode("../lambda-functions/failure/"),
            handler="failure.handler",
            role=lambda_role_dest,
            timeout=core.Duration.seconds(60),
            runtime=_lambda.Runtime.PYTHON_3_8)

        dest_success = _lambdadest.LambdaDestination(fnLambda_success)

        dest_failure = _lambdadest.LambdaDestination(fnLambda_failure)

        fnLambda_main.configure_async_invoke(on_success=dest_success,
                                             on_failure=dest_failure)


stack_prefix = 'lambda-async'
app = core.App()
stack = CdkStack(app, stack_prefix, stack_prefix=stack_prefix)
core.Tags.of(stack).add('Name', stack_prefix)

app.synth()
