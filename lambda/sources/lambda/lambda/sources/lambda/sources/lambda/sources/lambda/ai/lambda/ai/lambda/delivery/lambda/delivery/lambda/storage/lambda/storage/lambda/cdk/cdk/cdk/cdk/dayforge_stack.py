"""
DayForge CDK Stack — Infrastructure as Code.
"""
import os
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_logs as logs,
    CfnOutput,
)
from constructs import Construct


class DayForgeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        briefs_table = dynamodb.Table(
            self, "DayForgeBriefs",
            table_name="DayForgeBriefs",
            partition_key=dynamodb.Attribute(
                name="date",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        agent_function = lambda_.Function(
            self, "DayForgeAgent",
            function_name="DayForgeAgent",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=lambda_.Code.from_asset("../lambda"),
            timeout=Duration.seconds(60),
            memory_size=256,
            environment={
                "CITY": os.environ.get("CITY", "New York"),
                "GITHUB_USERNAME": os.environ.get("GITHUB_USERNAME", ""),
                "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", ""),
                "OPENWEATHER_API_KEY": os.environ.get("OPENWEATHER_API_KEY", ""),
                "NEWS_API_KEY": os.environ.get("NEWS_API_KEY", ""),
                "EMAIL_TO": os.environ.get("EMAIL_TO", ""),
                "EMAIL_FROM": os.environ.get("EMAIL_FROM", ""),
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        agent_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"]
            )
        )

        agent_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail", "ses:SendRawEmail"],
                resources=["*"]
            )
        )

        briefs_table.grant_write_data(agent_function)

        rule = events.Rule(
            self, "DayForgeSchedule",
            rule_name="DayForgeDaily6AM",
            schedule=events.Schedule.cron(
                minute="0",
                hour="6",
                month="*",
                week_day="*",
                year="*"
            ),
        )
        rule.add_target(targets.LambdaFunction(agent_function))

        CfnOutput(self, "FunctionName", value=agent_function.function_name)
        CfnOutput(self, "TableName", value=briefs_table.table_name)
        CfnOutput(self, "ScheduleRule", value=rule.rule_name)
