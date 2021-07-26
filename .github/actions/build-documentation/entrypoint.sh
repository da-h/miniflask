#!/bin/sh -l

# parse documentation
mkdir $DEST
cd $DOCS_SRC
python grep_docstrings.py
luke $DOCS_SRC -o $DEST --resources-with-file -t documentation.html --cdn
if [ $? -ne 0 ]; then
    echo "Could not parse Documentation successfully"
    echo "Exiting..."
    exit 1
fi

# remove all markdown files
find $DEST -name "*.md" -delete;

rm -rf $DOCS_SRC
mv $DEST/* .
