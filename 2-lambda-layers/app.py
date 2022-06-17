from constructs import Construct
import aws_cdk as _cdk
from aws_cdk import (App, Stack, aws_lambda as _lambda)


class LambdaFunction(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Using PyJWT layer from amazing KLayers repository
        # https://github.com/keithrozario/Klayers
        layer_arn_pyjwt = "arn:aws:lambda:ap-southeast-1:770693421928:layer:Klayers-python38-PyJWT:6"

        fn_lambda_decode = _lambda.Function(
            self,
            "{}-function-decode".format(id),
            code=_lambda.AssetCode("./lambda-functions/function-decode"),
            handler="app.handler",
            timeout=_cdk.Duration.seconds(60),
            architecture=_lambda.Architecture.ARM_64,
            layers=[_lambda.LayerVersion.from_layer_version_arn(
                self, "LayerPyJwt", layer_version_arn=layer_arn_pyjwt)],
            runtime=_lambda.Runtime.PYTHON_3_8)


app = App()
LambdaFunction(app, "lambda-layers")
app.synth()
