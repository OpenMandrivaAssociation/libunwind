%define oname	unwind
%define major	8
%define libname	%mklibname %{oname} %{major}
%define devname	%mklibname %{oname} -d

Summary:	An unwinding library
Name:		libunwind
Version:	1.1
Release:	1
License:	BSD
Group:		System/Libraries
Url:		http://savannah.nongnu.org/projects/libunwind
Source0:	http://download.savannah.gnu.org/releases/libunwind/libunwind-%{version}.tar.gz
#Fedora specific patch
Patch1:		libunwind-disable-setjmp.patch
Patch2:		libunwind-aarch64.patch
BuildRequires:	libtool

%description
Libunwind provides a C ABI to determine the call-chain of a program.
This version of libunwind is targetted for the ia64 platform.

%package -n %{libname}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libname}
Dynamic libraries from %{name}.

%package -n %{devname}
Summary:	Development package for libunwind
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%track
prog %name = {
	url = http://mirror3.layerjet.com/nongnu/libunwind/
	regex = %name-(__VER__)\.tar\.gz
	version = %version
}

%description -n %{devname}
The libunwind-devel package includes the libraries and header files for
libunwind.

%prep
%setup -q
%apply_patches
autoreconf -fi

%build
%configure2_5x \
	--enable-static \
	--enable-shared

%make

%install
%makeinstall_std

# /usr/include/libunwind-ptrace.h
# [...] aren't really part of the libunwind API.  They are implemented in
# a archive library called libunwind-ptrace.a.
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a %{buildroot}%{_libdir}/libunwind-ptrace.a-save
rm -f %{buildroot}%{_libdir}/libunwind*.a
mv -f %{buildroot}%{_libdir}/libunwind-ptrace.a-save %{buildroot}%{_libdir}/libunwind-ptrace.a
rm -f %{buildroot}%{_libdir}/libunwind-ptrace*.so*

%check
%if 0%{?_with_check:1} || 0%{?_with_testsuite:1}
echo ====================TESTING=========================
make check || true
echo ====================TESTING END=====================
%else
echo ====================TESTSUITE DISABLED=========================
%endif

%files -n %{libname}
%{_libdir}/libunwind*.so.%{major}*

%files -n %{devname}
%doc COPYING README NEWS
%{_libdir}/libunwind*.so
%{_libdir}/libunwind-ptrace.a
%{_mandir}/*/*
# <unwind.h> does not get installed for REMOTE_ONLY targets - check it.
%{_includedir}/unwind.h
%{_includedir}/libunwind*.h
