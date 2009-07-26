%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           cnucnu
Version:        0.0.0
Release:        1%{?dist}
Summary:        Upstream release monitoring with bug reporting

Group:          Development/Languages
License:        GPLv2+
URL:            https://fedoraproject.org/wiki/Upstream_Release_Monitoring
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

%description
Cnucnu provides an upstream release monitoring service.


%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# remove .py suffix
mv $RPM_BUILD_ROOT/%{_bindir}/cnucnu{.py,}

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING gpl-2.0.txt gpl-3.0.txt
# For noarch packages: sitelib
%{python_sitelib}/*
%{_bindir}/cnucnu


%changelog
