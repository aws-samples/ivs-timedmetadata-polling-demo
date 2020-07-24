#!/usr/bin/env bash

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

PROJECT_NAME="ivs-timedmetadata-polling-demo"
PROJECT_VERSION="v1"
BUCKET_NAME="CHANGEME!!"
CF_TEMPLATE="cf.template"

array=("webapi" "website" "websitecopy")

for i in "${array[@]}"
do
	echo $i
    pushd $i
    pwd
    ./makezip.sh
    popd
    pwd
    aws s3 cp ${i}/${i}_resources.zip s3://$BUCKET_NAME/$PROJECT_NAME/$PROJECT_VERSION/${i}_resources.zip --acl public-read
done


YAML_FILE=${PROJECT_NAME}.yaml
cp $CF_TEMPLATE $YAML_FILE

echo "Updating code source bucket in template with $BUCKET_NAME"

replace="s/%%BUCKET_NAME%%/${BUCKET_NAME}/g"
echo "sed -i '' -e $replace $YAML_FILE"
sed -i '' -e $replace $YAML_FILE

replace="s/%%PROJECT_NAME%%/${PROJECT_NAME}/g"
echo "sed -i '' -e $replace $YAML_FILE"
sed -i '' -e $replace $YAML_FILE

replace="s/%%PROJECT_VERSION%%/${PROJECT_VERSION}/g"
echo "sed -i '' -e $replace $YAML_FILE"
sed -i '' -e $replace $YAML_FILE

cat $YAML_FILE
aws s3 cp $YAML_FILE s3://$BUCKET_NAME/$PROJECT_NAME/$PROJECT_VERSION/$YAML_FILE --acl public-read

rm $YAML_FILE