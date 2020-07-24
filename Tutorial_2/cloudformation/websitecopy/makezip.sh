#!/bin/sh

# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

ORIGIN=`pwd`
ZIP="$ORIGIN/websitecopy_resources.zip"

rm -f $ZIP
pip3 install --force-reinstall --target ./package requests crhelper
cd package
zip -r9 $ZIP .
cd $ORIGIN
zip -g $ZIP lambda_function.py
