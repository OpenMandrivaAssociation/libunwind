%define oname unwind
%define onamedump unwindcoredump
%define onameptrace unwindptrace
%define major 8
%define majordump 0
%define majorptrace 0
%define majorsetjmp 0
%define libname %mklibname %{oname} %{major}
%define libdump %mklibname %{onamedump} %{majordump}
%define libptrace %mklibname %{onameptrace} %{majorptrace}
%define devname %mklibname %{oname} -d
%define _disable_ld_no_undefined 1
%define _disable_lto 1
%define beta rc2

Summary:	An unwinding library
Name:		libunwind
Version:	1.5
Release:	%{?beta:0.%{beta}.}1
License:	BSD
Group:		System/Libraries
# See also https://github.com/libunwind/libunwind
Url:		http://savannah.nongnu.org/projects/libunwind
Source0:	http://download.savannah.gnu.org/releases/libunwind/libunwind-%{version}%{?beta:-%{beta}}.tar.gz
Source1:	%{name}.rpmlintrc
#Fedora specific patch
# (tpg) dunno if it is still needed
#Patch1:		libunwind-disable-setjmp.patch
Patch3:		libunwind-musl.patch
BuildRequires:	libtool
BuildRequires:	pkgconfig(liblzma)

%description
Libunwind provides a C ABI to determine the call-chain of a program.
This version of libunwind is targetted for the ia64 platform.

%package -n %{libname}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libname}
Dynamic libraries from %{name}.

%package -n %{libdump}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries
Requires:	%{name} = %{EVRD}
Obsoletes:	%{_lib}unwind1 < 1.0.1-1

%description -n %{libdump}
Dynamic libraries from %{name}.

%package -n %{libptrace}
Summary:	Dynamic libraries from %{oname}
Group:		System/Libraries

%description -n %{libptrace}
Dynamic libraries from %{name}.

%define setjmpname %mklibname %{oname}-setjmp %{majorsetjmp}

%package -n %{devname}
Summary:	Development package for libunwind
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Requires:	%{name}-coredump = %{EVRD}
Requires:	%{setjmpname} = %{EVRD}

%description -n %{devname}
The libunwind-devel package includes the libraries and header files for
libunwind.

%package -n %{setjmpname}
Summary:	Libunwind setjmp library
Group:		System/Libraries

%description -n %{setjmpname}
Libunwind setjmp library

%prep
%autosetup -p1 -n %{name}-%{version}%{?beta:-%{beta}}
autoreconf -fi

%build
%ifarch %arm
export CC=gcc
export CXX=g++
%endif

# (tpg) fix linking on znver1
#global ldflags %{ldflags} -fuse-ld=bfd

%configure \
	--includedir=%{_includedir}/libunwind \
	--libdir=%{_libdir}/libunwind \
	--enable-static \
	--enable-shared

%make_build

%install
%make_install

mv %{buildroot}%{_libdir}/libunwind/pkgconfig %{buildroot}%{_libdir}

# Don't conflict with LLVM libunwind
mv %{buildroot}%{_libdir}/pkgconfig/libunwind.pc %{buildroot}%{_libdir}/pkgconfig/libunwind-nongnu.pc

cd %{buildroot}%{_libdir}
ln -s libunwind/*.so.* .

%check
%if 0%{?_with_check:1} || 0%{?_with_testsuite:1}
echo ====================TESTING=========================
make check || true
echo ====================TESTING END=====================
%else
echo ====================TESTSUITE DISABLED=========================
%endif

%files -n %{libname}
%{_libdir}/libunwind/libunwind*.so.%{major}*
%{_libdir}/libunwind*.so.*

%files -n %{libdump}
%{_libdir}/libunwind/libunwind-coredump.so.%{majordump}*

%files -n %{libptrace}
%{_libdir}/libunwind/libunwind-ptrace.so.%{majorptrace}*

%files -n %{setjmpname}
%{_libdir}/libunwind/libunwind-setjmp.so.%{majorsetjmp}*

%files -n %{devname}
%doc COPYING README NEWS
%{_libdir}/libunwind/libunwind*.so
%{_libdir}/libunwind/libunwind*.a
%{_libdir}/pkgconfig/*.pc
%{_includedir}/libunwind
%{_mandir}/man3/*
