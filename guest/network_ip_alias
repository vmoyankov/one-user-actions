#!/bin/bash

COMMAND=$1
IF_IDX=$2
ADDRESS=$3

LOCK_FILE="/var/run/one-context.lock"
CONTEXT_FILE="/tmp/context.$$"

function get_new_context
{
    CONTEXT_DEV=`blkid -l -t LABEL="CONTEXT" -o device`
    if [ -e "$CONTEXT_DEV" ]; then
        mount -t iso9660 -L CONTEXT -o ro /mnt
        if [ -f /mnt/context.sh ]; then
            cp /mnt/context.sh ${CONTEXT_FILE}
        fi
        umount /mnt
    elif curl -o ${CONTEXT_FILE} http://169.254.169.254/latest/user-data ; then
        echo -n ""
    fi
}

function read_eth_context
{
    if [ -f $CONTEXT_FILE ] ; then
        ONE_VARS=`cat $CONTEXT_FILE | egrep -e '^ETH[0-9]*=' | sed 's/=.*$//'`

        . $CONTEXT_FILE

        for v in $ONE_VARS; do
            export $v
        done
    fi
}

function get_interface_mac
{
    ip link show | awk '/^[0-9]+: [A-Za-z0-9]+:/ { device=$2; gsub(/:/, "",device)} /link\/ether/ { print device " " $2 }'
}

function get_context_interfaces
{
    env | grep -E "^ETH[0-9]+_MAC=" | sed 's/_.*$//' | sort
}

function get_dev
{
    list="$1"
    mac="$2"

    echo "$list" | grep "$mac" | cut -d' ' -f1 | tail -n1
}

function get_interface_name
{
    var_name="ETH${1}_MAC"
    MAC=$(eval "echo \"\${$var_name}\"")

    if [ -z "$MAC" ]; then
        return
    fi
    IF_MAC_LIST=$(get_interface_mac)
    DEV=$(get_dev "$IF_MAC_LIST" "$MAC")

    echo $DEV
}

function check_iface_addr
{
    if [ -z "$IF_IDX" ]; then
        >&2 echo "Missing interface index"
        exit 1
    fi
    get_new_context
    read_eth_context
    IFACE=$(get_interface_name "$IF_IDX")
    if [ -z "$IFACE" ]; then
        >&2 echo "Interface not found"
        exit 1
    fi
    if ! ip link show dev "$IFACE" >/dev/null 2>&1 ; then
        >&2 echo "Incorrect interface $IFACE"
        exit 1
    fi
    if [ -z "$ADDRESS" ]; then
        >&2 echo "Missing address"
        exit 1
    fi
}

function add_addr
{
    check_iface_addr
    ip addr add "$ADDRESS" dev "$IFACE"
}

function del_addr
{
    check_iface_addr
    ip addr del "$ADDRESS" dev "$IFACE"
}

case $COMMAND in
    add)
        add_addr
        ;;
    delete)
        del_addr
        ;;
    *)
        >&2 echo "Usage $0 {add|delete} <iface idx> <address/mask>"
        exit 1
esac
