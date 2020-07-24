#!/usr/bin/env bash

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

ZIP="webapi_resources.zip"

rm -f $ZIP
cd env/lib/python3.7/site-packages
zip -r9 ${OLDPWD}/$ZIP .
cd $OLDPWD
zip -g $ZIP lambda_function.py
