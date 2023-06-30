# ip2weather-daemon-centos-rpm
IP-to-Weather uWSGI daemon for CentOS 7, to run behind nginx

##How application works
* We have a request to nginx, like http://localhost/ip2w/{ip}
* Nginx proxies it to uWSGI daemon with PATH_INFO amongh uwsgi_params through a socket
* uWSGI proxies it to and application
* Application parses IP taken from PATH_INFO
* Takes city by IP: https://ipinfo.io/{ip}
* Takes weather from city: http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=en&appid={WEATHER_API_KEY}
* Responses with JSON with city, temperture, and conditions (or returns an appropriate error)
* Response goes back through a socket to nginx, and it responses to the initial request

#How is package built
* RPM package is built at CentOS, using .spec-file and boilerplate script (.sh), with rpmbuild command
* Then it is installed with rpm command
* According to the instructions from .spec:
  * .ini, .service, .log, nginx .conf and .py file are located in different designated places
  * daemon is enabled in systemctl

##Prerequisites
* nginx is installed
* python-requests is installed

###CentOS configuration
My dev space is in Windows. I didn't use Docker to run Linux this time, as we need to work with systemctl/systemd, and systemctl is not readily available when you run image in docker. 

So, I turned to Oracle's VirtualBox, and took the full image of CentOS 7:
* http://centos.koyanet.lv/centos/7.9.2009/isos/x86_64/CentOS-7-x86_64-Everything-2009.iso

_It is very well possible that some steps followed are excessive or too permissive. uWSGI starts under root user, which is not acceptable in production, but the goal was to make MPV with working RPM, and test the functionality. So, here we are..._

Don't forget to set up networking correctly:
* NAT
* Port Forwarding 8080 of a host > 80 of a guest, leaving IPs blank on both host and guest.

This way, requests issued on Windows host to localhost:8080 will end up at nginx which will listen port 80 on guest OS.

To be able to install and update something in guest OS, after running CentOS we have to tweak networking inside as well: add the following to /etc/sysconfig/network-scripts/ifcfg-enp0s3:
```
DNS1=8.8.8.8
DNS2=8.8.4.4
ONBOOT=yes
```

Copying files between host and guest and dditing files in guest OS will be easier through WinSCP. This works: https://www.youtube.com/watch?v=YhcXd74xF3Q

Now, install nginx, git and other stuff, and configure:
* yum update
* yum install -y epel-release nginx nano rpm-build git rpmdevtools rpmlint
* systemctl start nginx
* systemctl status nginx
* systemctl enable nginx

We also need SELinux not to block your requests. We may see if SELinux blocks something and get the recipes to fix with these steps:
* yum install -y policycoreutils-python
* grep nginx /var/log/audit/audit.log | audit2allow -m nginx

Ultimately, I had to do this:
* firewall-cmd --zone=public --permanent --add-service=http
* firewall-cmd --reload
* semanage permissive -a httpd_t

## Install, build, and run

After installation, go and edit /usr/local/etc/ip2w.ini, setting your secret API key for openweathermap:
* env=WEATHER_API_KEY=<your API key for api.openweathermap.org>

* `yum -y install python-pip python-devel nginx gcc` Note, python 2.7.5 will be installed!
* `pip install virtualenv==16.7.9`  # need to specify version, as latest virtualenv versions are not compatible with python 2.7.5
* mkdir ~/ip2weather  # skip, already created by voluming on docker container start
* cd ~
* virtualenv ip2weather_env
* source ip2weather_env/bin/activate
* `pip install uwsgi`
* `uwsgi --version`  # 2.0.21 version is expected to be installed
* 
* cd ~/ip2weather
* `uwsgi --socket 0.0.0.0:8000 --protocol=http -w wsgi`  # Test that uwsgi webserver running and proxiyng requests to our app. This can be done with http://localhost:8080 request from a browser on Windows host machine.
* Ctrl+C and `deactivate`


yum install -y python-pip python-devel gcc
pip install virtualenv==16.7.9
mkdir ~/myapp/
cd ~/myapp
virtualenv myappenv
source myappenv/bin/activate
pip install uwsgi
uwsgi --version
systemctl enable uwsgi



# Links
* https://www.digitalocean.com/community/tutorials/how-to-set-up-uwsgi-and-nginx-to-serve-python-apps-on-centos-7
* https://refspecs.linuxfoundation.org/FHS_3.0/fhs-3.0.pdf
* Building RPMs was something completely new to me. So... I cheated a little and took some ideas from this solution: https://github.com/olegborzov/otus-python-0218-homework/blob/master/hw5









