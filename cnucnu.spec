%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           cnucnu
Version:        0.0.0
Release:        1%{?dist}
Summary:        Upstream release monitoring with bug reporting
Group:          Development/Tools
License:        GPLv2+
URL:            https://fedoraproject.org/wiki/Upstream_Release_Monitoring
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel
BuildRequires:  python-setuptools
BuildArch:      noarch

Requires: rpm-python
Requires: python
Requires: python-bugzilla
Requires: python-fedora
Requires: python-genshi
Requires: python-pycurl
Requires: python-twisted-core
Requires: python-twisted-web
Requires: PyYAML

%description
Cnucnu provides an upstream release monitoring service with bugzilla
integration. See more at the project homepage at
https://fedoraproject.org/wiki/Upstream_Release_Monitoring

%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
python -c 'import setuptools; execfile("setup.py")' install --skip-build --root %{buildroot}

# remove .py suffix
mv $RPM_BUILD_ROOT/%{_bindir}/cnucnu{.py,}

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING gpl-2.0.txt gpl-3.0.txt
# For noarch packages: sitelib
%{python_sitelib}/cnucnu/
%{python_sitelib}/cnucnu-*.egg-info
%{_bindir}/cnucnu


%changelog
