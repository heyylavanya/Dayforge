#!/usr/bin/env python3
"""
DayForge CDK App — Deploys the entire agent infrastructure.
"""
import aws_cdk as cdk
from dayforge_stack import DayForgeStack

app = cdk.App()

DayForgeStack(app, "DayForgeStack",
    env=cdk.Environment(
        region="us-east-1"
    )
)

app.synth()
