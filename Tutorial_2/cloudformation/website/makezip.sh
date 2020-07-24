#!/bin/sh

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

ORIGIN=`pwd`
ZIP="$ORIGIN/website_resources.zip"

rm -f $ZIP
zip -r9 $ZIP player.html words.json