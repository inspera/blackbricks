#!/usr/bin/bash
version="$(git describe --tags)"


echo "You are about to publish version ${version} (based on most recent git tag). Continue?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done


python setup.py bdist_wheel
twine upload dist/*
