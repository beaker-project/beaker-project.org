#!/bin/bash

set -e

if [ -z "$1" ] ; then
    echo "Must pass destination branch in arg 1" >&2
    echo "(Don't invoke this script directly, use the Makefile)" >&2
    exit 1
fi

# This is the SHA of the current tip of the destination branch,
# on top of which we will commit our new version.
parent=$(git rev-parse refs/heads/$1)

if [ "$(git rev-parse HEAD)" = "$parent" ] ; then
    echo "Don't checkout the published branch!" >&2
    exit 1
fi

# Sanity check: the commit from which the current destination branch was built,
# must be an ancestor of the commit we are building from now.
if ! git rev-list HEAD | grep -q $(git show $parent:git-rev) ; then
    echo "Error: tip of '$1' was built from" >&2
    git show $parent:git-rev >&2
    echo "which is not an ancestor of HEAD" >&2
    exit 1
fi

D=$(mktemp -d)
# check out HEAD of beaker-project.org into $D
GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish GIT_WORK_TREE="$D" git read-tree HEAD
GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish GIT_WORK_TREE="$D" git checkout-index -a -f
# check out the submodule revision of beaker into $D/beaker
GIT_DIR=$BEAKER/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish-beaker GIT_WORK_TREE="$D/beaker" git read-tree $(git rev-parse HEAD:beaker)
GIT_DIR=$BEAKER/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish-beaker GIT_WORK_TREE="$D/beaker" git checkout-index -a -f
# record SHAs in the published version
GIT_DIR=$(pwd)/.git git rev-parse HEAD >"$D/git-rev"
GIT_DIR="$BEAKER/.git" git rev-parse HEAD >"$D/git-rev-beaker"

# Carry existing release artifacts and RPMs over to the build directory,
# because they are quite expensive to build/fetch and they never change.
# This is purely an optimisation so ignore failures.
mkdir -p "$D/releases" || :
cp -p --reflink=auto releases/*.tar.* releases/*.patch "$D/releases/" || :
mkdir -p "$D/yum/rpms" || :
cp -p --reflink=auto yum/rpms/*.rpm "$D/yum/rpms/" || :

make -j4 -C "$D" all

# Clean out junk that we don't want to publish.
rm -rf "$D/man/.doctrees" "$D/docs/.doctrees" "$D/dev/.doctrees"

GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish GIT_WORK_TREE="$D" git add -f -A "$D"
tree=$(GIT_DIR=$(pwd)/.git GIT_INDEX_FILE=$(pwd)/.git/index-publish git write-tree)
commit=$(git commit-tree $tree -p $parent -p $(git rev-parse HEAD) <<EOF
Automatic commit of generated web site from $(git rev-parse HEAD)
EOF
)
git update-ref refs/heads/$1 $commit $parent

rm -rf "$D"
