#!/bin/sh -l
DIR=$(pwd)

# parse documentation
mkdir $DEST
python $DOCS_SRC/grep_docstrings.py
luke $DOCS_SRC -o $DEST --resources-with-file -t documentation.html --cdn
if [ $? -ne 0 ]; then
    echo "Could not parse Documentation successfully"
    echo "Exiting..."
    exit 1
fi

# remove all markdown files
find $DEST -name "*.md" -delete;

# overwrite gh-branch content with build output
cd $DIR
rm -rf $DOCS_SRC
mv $DEST/* .
