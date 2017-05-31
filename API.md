OpenNebula user-action API
==========================

This API provides a commands to execute specific actions on Guest OS 
in vrtual machines, using internal QEMU interface. It does not require
network or console access to vistual machines.

API is compatible with XMLRPC API and uses the same format of authentication,
input and output parameters.

Currently this API supports only QEMU/KVM and Linux guests.

URL
---

By default this API is accessible at the same host as OpenNebula XMLRPC API
at:

http://opennebula:2634/RPC2


Commands
--------

All commands have the same first two input parameters and the same output.
Some commands may have additional input parameters. They are listed 
below in the command description

Input:
  - auth: string, Authentication token in format 'username:password'
  - vmid: interger. VM ID

Output:
  - boolean: True on success, false on error
  - string: output of the command if success, or error message if failed
  - int: error code or exit status of external command. 0 on success

-----------------------
one.user_action.reset_password

Reset root password.

Input:
  - string: new password base64-encoded

-----------------------
one.user_action.reset_network_config

Reset all network settings. Regenerate interface configuration files, restarts
network service, Does not chnage iptables.

Input:
  - none

-----------------------
one.user_action.clear_firewall

Reset iptables settings to default. All tables and chains are reset to 
accept all traffic.

Input:
  - none

-----------------------
one.user_action.add_ip_alias

Add ip addres to existing network interface. It shall be used only for 
secondary addresses and not for the primary interface address. Does not verify 
if the address is available or used.

Input:
  - integer: interface index. First interface is 0. It is mapped to ETH0 in
      VM context
  - string: network address prefix. Format is X.X.X.X/MM e.g. 10.11.12.33/32

-----------------------
one.user_action.del_ip_alias

Delete existing ip addres from network interface. This method shall be used 
to delete addresses added by one.user_action.add_ip_alias only. It shall not be
used to remove primary interface addresses. The method 
does not check if the address was previously added. It does not release any 
reservation for the address. Address management shall be done externally.
Address prefix and interface index shall match the add request.

Input:
  - integer: interface index. First interface is 0. It is mapped to ETH0 in
    VM context
  - string: network address prefix. Format is X.X.X.X/MM e.g. 10.11.12.33/32

-----------------------
one.user_action.test

Checks if VM responds to user commands. Can be used to verify if required
qemu-guest-agent package is installed propperly and qemu-ga is running on 
the VM

Input:
  - string: test string. On success it is returned in the response together
    with some guest OS information.

-----------------------
one.user_action.exec

Execute any command on guest OS. Use with care!

Input:
  - string: base64-encoded command to be executed on the guest OS. 
    stdout is return if exit code is 0, 
    if exit code != 0 stderr is returned
