
# Table of Contents

- /export/cob/rootfs/ldmx
  - common2021 <- created following notes and SLAC instructions linked below
  - from-hps   <- tar-balls created WITHOUT sudo privileges and downloaded from SLAC
  - DTM        <- unpacked tar-ball WITHOUT sudo privileges
  - dataDPM    <- unpacked tar-ball WITHOUT sudo privileges
  - ctrlDPM    <- unpacked tar-ball WITHOUT sudo privileges

Further notes about how we got to this point are below.

# "Image" Construction

Adapted from RCE "diskless" booting:
https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=212764256

1. downloaded arm-linux and RCE SDK using wget
```
wget http://www.slac.stanford.edu/projects/CTK/SDK/rce-sdk-V3.4.1.tar.gz
wget http://os.archlinuxarm.org/os/ArchLinuxARM-zedboard-latest.tar.gz
```

2. unpacked SDK in some home directory
```
cd ~/cob
tar xzvf <path-to-tar>/rce-sdk-V3.4.1.tar.gz
```

3. unpacked arm-linux in subdirectory of NFS export
```
cd /export/cob/rootfs/ldmx
sudo mkdir my-name
cd my-name
sudo tar xzvf <path-to-tar>/ArchLinuxARM-zedboard-latest.tar.gz
```

  NOTE: With only 'cobadmin' privileges, unpacking the arm-linux image returns a failure
        status because 'tar' cannot preserve the UIDs (some of which are root == 0).

4. prepare arm-linux installation by copying necessary files from SDK

```
# still inside /export/cob/rootfs/ldmx/my-name
sudo cp ~/cob/V3.4.1/arm-linux-rceCA9/tgt/linux/fstab.diskless etc/fstab
sudo cp ~/cob/V3.4.1/arm-linux-rceCA9/tgt/linux/kernel/uImage boot/
sudo cp ~/cob/V3.4.1/arm-linux-rceCA9/tgt/linux/kernel/devicetree.dtb boot/
```

5. insert fpga firmware bitfile

  This should be put inside the 'boot' directory. 
  The 'boot' directory can be given different ownership than root root,
  we have put it in the 'cobadmin' group so that users who are apart of that group
  can modify the files within that directory. In order to modify these files
  (including changing symlinks) you will need to switch your "primary" group
  from your user to cobadmin. This resets your environment.

```
newgrp cobadmin
```

  The default name is 'fpga.bit',
  but there is a method for changing the name within the boot environment.

  HPS has also used symlinks to make it easier to change the firmware
  while still having a verbose filename.

```
# still inside /export/cob/rootfs/ldmx/my-name
cp ../dataDPM/boot/fpga.bit.working.1g boot/
cd boot
ln -sf fpga.bit.working.1g fpga.bit
```

6. remove specific service file links

```
# still inside /export/cob/rootfs/ldmx/my-name
sudo rm etc/systemd/system/sockets.target.wants/systemd-networkd.socket
sudo rm etc/systemd/system/multi-user.target.wants/systemd-networkd.service
```

7. modify log-in configuration to allow console and ssh login

```
# still inside /export/cob/rootfs/ldmx/my-name
sudo chmod a+r etc/shadow
# uncomment 'PermitRootLogin' and set value to 'yes' in etc/ssh/sshd_config
sudo chmod a+rw etc/ssh
```

NOTE: I did not add the RCE core software because it was labeled as optional.

8. modify root-path DHCP option in cmslab0:/etc/dhcpd_cob.conf and restart DHCP server

```
# dataDPM -> my-name in /etc/dhcpd_cob.conf
/opt/umnhostdb/bin/refresh_hostdb.sh
```

9. log-in to the test DPM via the DTM and minicom

```
ssh root@192.168.28.100
minicom bay0.0
```

10. initiate a restart of the test DPM from the server

```
# on cmslab0
cob_rce_reset 192.168.1.35/13/0/0
```

# NFS Server Side (Jeremy)

0. Start-Up NFS server to export the directory `/export/cob/rootfs`

1. add `udp=y` to the `/etc/nfs.conf` file in the `nfs` section.

2. add `vers2=y` to the `/etc/nfs.conf` file also.

3. Confirm from the commandline that `rpcinfo -s` looks like:
```
  program version(s) netid(s)                         service     owner
    100000  2,3,4     local,udp,tcp,udp6,tcp6          portmapper  superuser
 600100069  1         tcp6,udp6,tcp,udp                fypxfrd     superuser
    100004  1,2       tcp6,udp6,tcp,udp                ypserv      superuser
    100009  1         tcp6,udp6,tcp,udp                yppasswdd   superuser
    100024  1         tcp6,udp6,tcp,udp                status      29
    100005  3,2,1     tcp6,udp6,tcp,udp                mountd      superuser
    100003  4,3,2     udp6,tcp6,udp,tcp                nfs         superuser
    100227  3,2       udp6,tcp6,udp,tcp                nfs_acl     superuser
    100021  4,3,1     tcp6,udp6,tcp,udp                nlockmgr    superuser
```

(Note the version 2 for nfs and the udp for nfs)

# Additional Notes
The COB components (DPM or DTM) begin their booting process from their mounted SD cards first.
This means that some booting files need to be put onto the SD card even though we are booting
the kernel image (uImage), the device tree, and the FPGA firmware via NFS.

- /boot/uboot.env
- /boot/boot.bin

These booting files need to "match" the kernel image and device tree we are using
so that the booting can complete successfully. Checking the files on the SD card can
be done by either (A) booting the COB component from the SD card or (B) booting from NFS
and then mounting the SD card manually.

```
mkdir /mnt/sdcard
mount /dev/mmcblk0p1 /mnt/sdcard/
```

Ryan was able to deduce the issue we were seeing where his example firmware would hang
when trying to connect to the DTM. The issue is that our current DTM firmware is old
and doesn't comprehend the custom mac / 1G combination. The patch solution is to force
our DPMs to use an old mac mode and use the 1G device tree file.

