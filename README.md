Add-on for user defined actions in guests
=========================================

This add-on enables user defined actions to be initiated using XML-RPC server
on OpenNebula and executed on Guest VM. Main purpose is to allow some
administrative tasks, when remote access over netwrok interfaces is not
available - such as reset root password, reset iptables or update
network settings.

User actions are defined with scripts on both virtualization cluster and on the
guest OS. Communication between OpenNebula and guest OS is via libvirt guest
agent and does not require working network interface or console on the VM.

This code is installed in the following locations:

1. /server - on OpenNebula server
2. /host   - on each QEMU/KVM hypervisor
3. /guest  - on guest OS.

Requirements
------------

1. Guest templates shall have enabled option GEST_AGENT.
2. Guests shall have installed qemu-guest-agent.
3. user-action scripts shall be installed on guest

Communication protocol
----------------------

1. User action script on quest

  - exit 0 if success, >0 if error
  - error message on stderr
  - output result, if any on stdout

2. User action scripts on hosts.

These scripts are executed over ssh.

  - exit 0 if success, >0 if error
  - error message on stderr
  - output result, if any on stdout

3. Server
