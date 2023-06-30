License:        MIT
Vendor:         abalabanov
Source0:        ip2w-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/ip2w-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
BuildRequires: python3-devel
Requires: python-requests
Summary: uWSGI app to retrieve weather by IP

%description
Homework @OTUS Python Developer. Professional, to create an RPM-package
with uWSGI daemon app which returns JSON with weather for a location, defined by IP

Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc
%define __logdir    /val/log/
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/
%define __nginxconfdir /etc/nginx/conf.d/

%prep
%setup -n ip2w-%{current_datetime}

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}
%{__install} -pD -m 644 %{name}.service %{buildroot}/%{__systemddir}/%{name}.service
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__install} -pD -m 755 %{name}.py3 %{buildroot}/%{__bindir}/%{name}.py3
%{__mkdir} -p %{buildroot}/%{__etcdir}
%{__install} -pD -m 644 %{name}.ini %{buildroot}/%{__etcdir}/%{name}.ini
%{__mkdir} -p %{buildroot}/%{__nginxconfdir}
%{__install} -pD -m 644 %{name}.conf %{buildroot}/%{__nginxconfdir}/%{name}.conf
%{__mkdir} -p %{buildroot}/%{__logdir}
%{__install} -pD -m 666 /dev/null %{buildroot}/%{__logdir}/%{name}.log

%post
%systemd_post %{name}.service
systemctl enable ip2w
systemctl daemon-reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__logdir}
%{__bindir}
%{__etcdir}
%{__systemddir}
%{__nginxconfdir}
