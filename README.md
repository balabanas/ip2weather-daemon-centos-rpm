# ip2weather-daemon-centos-rpm
RPM with IP-to-Weather (ip2w) uWSGI daemon for CentOS 7, designed to run behind nginx.

## How application works
* We have a request to nginx, e.g. http://localhost/ip2w/{ip}
* Nginx proxies the request, including PATH_INFO, to the uWSGI daemon using uwsgi_params through a socket
* The uWSGI daemon forwards the request to the application
* The application parses the IP extracted from PATH_INFO
* It retrieves the city based on the IP: https://**ipinfo.io**/{ip}
* The application fetches the weather information for the city: http://**api.openweathermap.org/data/2.5/weather**?q={city}&units=metric&lang=en&appid={WEATHER_API_KEY}
* The application responds with a JSON object containing the city, temperature, and weather conditions, or an appropriate error message
* The response is sent back through the socket to nginx, which then responds to the initial request

# How the package is built
* The RPM package is built on CentOS using a `.spec` file and a boilerplate script (`.sh`) with the `rpmbuild` command
* After building the package, it is installed using the `rpm` command
* Following the instructions in the `.spec` file:
  * The `.ini`, `.service`, `.log`, `nginx.conf`, and `.py` files are placed in their designated locations
  * The daemon is enabled in systemctl

## Prerequisites
* nginx is installed and running
* python-requests is installed

## Build
Assuming you have already configured your CentOS OS as described below (see **CentOS configuration**):
* `git config --global user.name "Your Name"`
* `git config --global user.email "youremail@gmail.com"`
* `git clone https://github.com/balabanas/ip2weather-daemon-centos-rpm.git`
* `cd ip2weather-daemon-centos-rpm`
* `/usr/bin/bash buildrpm.sh ip2w.spec`

## Install & run
* `rpm -i /root/rpm/RPMS/noarch/ip2w-0.0.1-1.noarch.rpm`
* `rm -fr rpm`

After installation, edit `/usr/local/etc/ip2w.ini`, setting your secret API key for **openweathermap**:
* `env=WEATHER_API_KEY=<your API key for api.openweathermap.org>`

Start ip2w and check if necessary services are running:
* `systemctl start ip2w`
* `systemctl status ip2w`
* `systemctl status nginx`

If statuses are OK, check if app responses:
* `curl http://127.0.0.1:80/ip2w/195.69.81.52`

### CentOS Configuration
If you're, like me, using a Windows development environment, running Linux in Docker may not be suitable due to the need to work with systemctl/systemd, which is not readily available in Docker containers. In this case, you can use Oracle's VirtualBox and follow the steps below:
* http://centos.koyanet.lv/centos/7.9.2009/isos/x86_64/CentOS-7-x86_64-Everything-2009.iso

_It is very well possible that some steps followed are excessive or too permissive. I start uWSGI under root user, which is not acceptable in production, but the goal was to make MPV with working RPM, and test the functionality. So, here we are..._

Don't forget to set up networking for a virtual machine in VirtualBox interface:
* NAT
* Port Forwarding 8080 of a host > 80 of a guest, leaving IPs blank on both host and guest.
* 2222 > 22 (for WinSCP)

This way, requests issued on Windows host to localhost:8080 will end up at nginx which will listen port 80 on guest OS. As well, copying files between host and guest and editing files in guest OS will be easier through WinSCP. This works: https://www.youtube.com/watch?v=YhcXd74xF3Q

To be able to install and update something in guest OS, after running CentOS we have to tweak networking inside as well: add the following to `/etc/sysconfig/network-scripts/ifcfg-enp0s3`:

* `vi /etc/sysconfig/network-scripts/ifcfg-enp0s3`

```
DNS1=8.8.8.8
DNS2=8.8.4.4
ONBOOT=yes
```

Install necessary packages and configure nginx, git, and SELinux:
```
yum update -y
yum upgrade -y
yum install -y epel-release 
yum install -y nginx rpm-build git rpmdevtools rpmlint wget
systemctl start nginx
systemctl status nginx
systemctl enable nginx
yum install -y policycoreutils-python
```

(optionally, you can check what blocks your HTTP traffic with this command):
`grep nginx /var/log/audit/audit.log | audit2allow -m nginx`

Ultimately, I had to do this:
```
firewall-cmd --zone=public --permanent --add-service=http
firewall-cmd --reload
semanage permissive -a httpd_t
```

Install Python 3, create a virtual environment, and install required packages:
```
yum install -y python3
yum install -y python3-pip python3-devel gcc
yum groupinstall -y "Development Tools"
yum install -y python3-requests

python3 -m venv ip2wenv
source ip2wenv/bin/activate
pip install --upgrade pip
pip install requests uwsgi
```

## Uninstall
yum remove -y ip2w

## Links
* https://www.digitalocean.com/community/tutorials/how-to-set-up-uwsgi-and-nginx-to-serve-python-apps-on-centos-7
* https://refspecs.linuxfoundation.org/FHS_3.0/fhs-3.0.pdf
* The RPM packaging process in this project was based on ideas from the following solution: https://github.com/olegborzov/otus-python-0218-homework/blob/master/hw5
