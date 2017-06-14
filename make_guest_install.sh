#!/bin/bash

LICENSE=$(cat <<EOF_LICENSE

# Copyright 2017 Telera www.telera.eu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

EOF_LICENSE
)

OUT_FILE=guest_install.sh

CUR_DIR=`dirname $0`

tmpfile=`mktemp`
tar czf $tmpfile -C $CUR_DIR/guest .

cat <<EOF > $OUT_FILE
#!/bin/bash

$LICENSE

######################################################################
#
# This installer installs scripts needed by OpenNebula
# User Action extentions for guest OS.
# All scripts are installed in /etc/one-user-action.
#
# User Action functions require qemu-guest-agent ver >= 2.5 
# to be installed in guest OS.
#
######################################################################

set -e

INSTALL_DIR=/etc/one-user-action

mkdir -p \$INSTALL_DIR
cat <<TAR_FILE | base64 -d | tar xzf - -C \$INSTALL_DIR
EOF
base64 < $tmpfile >>$OUT_FILE
cat <<EOF >>$OUT_FILE
TAR_FILE

echo "Installation successful. Scripts are installed in \$INSTALL_DIR"
EOF
rm $tmpfile

chmod a+x $OUT_FILE
echo "New installation file created: $OUT_FILE"
