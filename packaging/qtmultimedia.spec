# Package prefix
%define pkgname qt5-qtmultimedia

Name:       qtmultimedia
Summary:    Qt Multimedia module
Version:    5.3.2
Release:    1
Group:      Qt/Qt
License:    LGPLv2.1 with exception or GPLv3
URL:        http://qt.io
Source0:    %{name}-%{version}.tar.xz
BuildRequires:  qt5-qtcore-devel
BuildRequires:  qt5-qtgui-devel
BuildRequires:  qt5-qtwidgets-devel
BuildRequires:  qt5-qtopengl-devel
BuildRequires:  qt5-qtnetwork-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  qt5-qtdeclarative-qtquick-devel
BuildRequires:  qt5-qmake
BuildRequires:  pkgconfig(alsa)
BuildRequires:  fdupes
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libpulse-mainloop-glib)
BuildRequires:  pkgconfig(gstreamer-1.0)
BuildRequires:  pkgconfig(gstreamer-base-1.0)
BuildRequires:  pkgconfig(gstreamer-audio-1.0)
BuildRequires:  pkgconfig(gstreamer-video-1.0)
BuildRequires:  pkgconfig(gstreamer-pbutils-1.0)
BuildRequires:  pkgconfig(gstreamer-app-1.0)
BuildRequires:  pkgconfig(gstreamer-plugins-base-1.0)
BuildRequires:  pkgconfig(gstreamer-plugins-bad-free-1.0)
#BuildRequires:  pkgconfig(libresourceqt5)

%description
Qt is a cross-platform application and UI framework. Using Qt, you can
write web-enabled applications once and deploy them across desktop,
mobile and embedded systems without rewriting the source code.

This package contains the QtMultimedia module.


%package -n %{pkgname}
Summary:    Qt Multimedia module
Group:      Qt/Qt

%description -n %{pkgname}
Qt is a cross-platform application and UI framework. Using Qt, you can
write web-enabled applications once and deploy them across desktop,
mobile and embedded systems without rewriting the source code.

This package contains the QtMultimedia module.


%package -n %{pkgname}-devel
Summary:    Qt Multimedia - development files
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}

%description -n %{pkgname}-devel
Qt is a cross-platform application and UI framework. Using Qt, you can
write web-enabled applications once and deploy them across desktop,
mobile and embedded systems without rewriting the source code.

This package contains the QtMultimedia module development files.


%package -n qt5-qtdeclarative-import-multimedia
Summary:    QtQml multimedia import
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}
Requires:   qt5-qtdeclarative

%description -n qt5-qtdeclarative-import-multimedia
This package contains the Multimedia import for QtQml


%package -n %{pkgname}-gsttools
Summary:    Qt Multimedia - Utility library for GStreamer media services
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}

%description -n %{pkgname}-gsttools
This package contains a shared library for the GStreamer QtMultimedia media services


%package -n %{pkgname}-plugin-mediaservice-gstaudiodecoder
Summary:    Qt Multimedia - GStreamer audio decoder media service
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}
Requires:   qt5-qtmultimedia-gsttools = %{version}-%{release}

%description -n %{pkgname}-plugin-mediaservice-gstaudiodecoder
This package contains the GStreamer audio decoder plugin for QtMultimedia


#%package -n %{pkgname}-plugin-resourcepolicy-resourceqt
#Summary:    Qt Multimedia - libresourceqt resource policy plugin
#Group:      Qt/Qt
#Requires:   %{pkgname} = %{version}-%{release}
#
#%description -n %{pkgname}-plugin-resourcepolicy-resourceqt
#This package contains the libresourceqt resource policy plugin for QtMultimedia


%package -n %{pkgname}-plugin-mediaservice-gstcamerabin
Summary:    Qt Multimedia - GStreamer camerabin video capture media service
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}
Requires:   qt5-qtmultimedia-gsttools = %{version}-%{release}

%description -n %{pkgname}-plugin-mediaservice-gstcamerabin
This package contains the GStreamer camerabin video capture plugin for QtMultimedia


%package -n %{pkgname}-plugin-mediaservice-gstmediacapture
Summary:    Qt Multimedia - GStreamer video4linux2 video capture media service
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}
Requires:   qt5-qtmultimedia-gsttools = %{version}-%{release}

%description -n %{pkgname}-plugin-mediaservice-gstmediacapture
This package contains the GStreamer video4linux2 video capture plugin for QtMultimedia


%package -n %{pkgname}-plugin-mediaservice-gstmediaplayer
Summary:    Qt Multimedia - GStreamer playback media service
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}
Requires:   qt5-qtmultimedia-gsttools = %{version}-%{release}

%description -n %{pkgname}-plugin-mediaservice-gstmediaplayer
This package contains the GStreamer media playback plugin for QtMultimedia


%package -n %{pkgname}-plugin-playlistformats-m3u
Summary:    Qt Multimedia - M3U playlist support
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}
Requires:   qt5-qtmultimedia-gsttools = %{version}-%{release}

%description -n %{pkgname}-plugin-playlistformats-m3u
This package contains the M3U playlist support


%package -n %{pkgname}-plugin-audio-alsa
Summary:    Qt Multimedia - ALSA plugin
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}

%description -n %{pkgname}-plugin-audio-alsa
This package contains the ALSA sound support.


%package -n %{pkgname}-plugin-audio-pulseaudio
Summary:    Qt Multimedia - Pulse Audio plugin
Group:      Qt/Qt
Requires:   %{pkgname} = %{version}-%{release}

%description -n %{pkgname}-plugin-audio-pulseaudio
This package contains the pulse audio sound effect support.


%prep
%setup -q -n %{name}-%{version}


%build
export QTDIR=/usr/share/qt5
touch .git

%qmake5
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
%qmake5_install
# Remove unneeded .la files
rm -f %{buildroot}/%{_libdir}/*.la
# Fix wrong path in pkgconfig files
find %{buildroot}%{_libdir}/pkgconfig -type f -name '*.pc' \
    -exec perl -pi -e "s, -L%{_builddir}/?\S+,,g" {} \;
# Fix wrong path in prl files
find %{buildroot}%{_libdir} -type f -name '*.prl' \
    -exec sed -i -e "/^QMAKE_PRL_BUILD_DIR/d;s/\(QMAKE_PRL_LIBS =\).*/\1/" {} \;

# We don't need qt5/Qt/
rm -rf %{buildroot}/%{_includedir}/qt5/Qt

%fdupes %{buildroot}/%{_includedir}


%post -n %{pkgname}
/sbin/ldconfig
%postun -n %{pkgname}
/sbin/ldconfig

%post -n %{pkgname}-gsttools
/sbin/ldconfig
%postun -n %{pkgname}-gsttools
/sbin/ldconfig

%files -n %{pkgname}
%defattr(-,root,root,-)
%{_libdir}/libQt5Multimedia.so.5
%{_libdir}/libQt5Multimedia.so.5.*
%{_libdir}/libQt5MultimediaWidgets.so.5
%{_libdir}/libQt5MultimediaWidgets.so.5.*
%{_libdir}/libQt5MultimediaQuick_p.so.5
%{_libdir}/libQt5MultimediaQuick_p.so.5.*

%files -n %{pkgname}-devel
%defattr(-,root,root,-)
%{_libdir}/libQt5Multimedia.so
%{_libdir}/libQt5MultimediaWidgets.so
%{_libdir}/libQt5MultimediaQuick_p.so
%{_libdir}/libqgsttools_p.so
%{_libdir}/libQt5Multimedia.prl
%{_libdir}/libQt5MultimediaWidgets.prl
%{_libdir}/libQt5MultimediaQuick_p.prl
%{_libdir}/libqgsttools_p.prl
%{_libdir}/pkgconfig/*
%{_includedir}/qt5/*
%{_datadir}/qt5/mkspecs/
%{_libdir}/cmake/

%files -n qt5-qtdeclarative-import-multimedia
%defattr(-,root,root,-)
%{_libdir}/qt5/qml/QtMultimedia/

%files -n %{pkgname}-gsttools
%defattr(-,root,root,-)
%{_libdir}/libqgsttools_p.so.1
%{_libdir}/libqgsttools_p.so.1.*

%files -n %{pkgname}-plugin-mediaservice-gstaudiodecoder
%defattr(-,root,root,-)
%{_libdir}/qt5/plugins/mediaservice/libgstaudiodecoder.so

%files -n %{pkgname}-plugin-mediaservice-gstcamerabin
%defattr(-,root,root,-)
%{_libdir}/qt5/plugins/mediaservice/libgstcamerabin.so

%files -n %{pkgname}-plugin-mediaservice-gstmediacapture
%defattr(-,root,root,-)
%{_libdir}/qt5/plugins/mediaservice/libgstmediacapture.so

%files -n %{pkgname}-plugin-mediaservice-gstmediaplayer
%defattr(-,root,root,-)
%{_libdir}/qt5/plugins/mediaservice/libgstmediaplayer.so

%files -n %{pkgname}-plugin-playlistformats-m3u
%defattr(-,root,root,-)
%{_libdir}/qt5/plugins/playlistformats/libqtmultimedia_m3u.so

#%files -n %{pkgname}-plugin-resourcepolicy-resourceqt
#%defattr(-,root,root,-)
#%{_libdir}/qt5/plugins/resourcepolicy/libresourceqt.so

%files -n %{pkgname}-plugin-audio-alsa
%defattr(-,root,root,-)
%{_libdir}/qt5/plugins/audio/libqtaudio_alsa.so

%files -n %{pkgname}-plugin-audio-pulseaudio
%defattr(-,root,root,-)
%{_libdir}/qt5/plugins/audio/libqtmedia_pulse.so
