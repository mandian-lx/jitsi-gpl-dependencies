%{?_javapackages_macros:%_javapackages_macros}

%define debug_package %{nil}

%define commit e4bdac2ff0235c1a96736430b50a5b8ad0b01eca
%define shortcommit %(c=%{commit}; echo ${c:0:7})

Summary:	Jitsi dependencies released under LGPL license
Name:		jitsi-gpl-dependencies
Version:	0
Release:	0
License:	GPLv2
Group:		Development/Java
Url:		https://github.com/jitsi/%{name}
Source0:	https://github.com/jitsi/%{name}/archive/%{commit}/%{name}-%{commit}.zip
Source1:	https://raw.githubusercontent.com/jitsi/jitsi-lgpl-dependencies/master/build.xml
Patch0:		%{name}-e4bdac2f-native_build_xml.patch
Patch1:		%{name}-e4bdac2f-remove-hflip.patch
Patch2:		%{name}-e4bdac2f-ffmpeg2.patch

BuildRequires:	ant
BuildRequires:	cpptasks
BuildRequires:	javapackages-local
BuildRequires:	maven-local
BuildRequires:	mvn(net.java.dev.jna:jna)
BuildRequires:	mvn(org.apache.felix:maven-bundle-plugin)
# natives
#   ffmpeg
BuildRequires:	lame-devel
BuildRequires:	pkgconfig(libavcodec)
BuildRequires:	pkgconfig(libavfilter)
BuildRequires:	pkgconfig(libavformat)
BuildRequires:	pkgconfig(libavutil)
BuildRequires:	pkgconfig(libswscale)
BuildRequires:	pkgconfig(vo-amrwbenc)
BuildRequires:	pkgconfig(x264)

# natives
Requires:	%{_lib}avcodec57
Requires:	%{_lib}avfilter6
Requires:	%{_lib}avformat57
Requires:	%{_lib}avutil55
Requires:	%{_lib}swscaler4
#    form restricted repo
Suggests:	%{_lib}lame0
Suggests:	%{_lib}vo-amrwbenc0
Suggests:	%{_lib}x264_148

%description
Jitsi dependencies released under LGPL license.

%files -f .mfiles

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}
BuildArch:	noarch

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc

#----------------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{commit}

# Add missing build.xml
cp %{SOURCE1} build.xml

# Delete prebuild JARs and libs
find . -name "*.jar" -delete
find . -name "*.class" -delete
find . -type f -name "*.dll" -delete
find . -type f -name "*.jnilib" -delete
find . -type f -name lib\*.so\* -delete

# Apply all patches
%patch0 -p1 -b .orig
%patch1 -p1 -b .hflip
%patch2 -p1 -b .ffmpeg2

# fix build.xml
sed -i -e '{	s|lgpl|gpl|g
		s|LGPL|GPL|g
	   }' build.xml

# Fix classpath
ln -fs `build-classpath jna` ./lib/jna.jar

# Unbundle native libs for other SO and arch
sed -i -e '{	/darwin/d
		/linux-x86-64/d
		/win32-x86/d
		/win32-x86-64/d
		s|linux-x86|linux-@arch@|g
		s|processor=x86|processor=@arch@|g
		s|@arch@,|@arch@|g
	    }' pom.xml

# use properly arch
%ifarch %{x?86}
sed -i -e '{	s|linux-@arch@|linux-x86|g
		s|processor=@arch@|processor=x86|g
	   }' pom.xml
%endif

%ifarch x86_64
sed -i -e '{	s|linux-@arch@|linux-x86-64|g
		s|processor=@arch@|processor=x86-64|g
	   }' pom.xml
%endif

# Remove jitsi-universe parent
%pom_remove_parent .

# Add groupId
%pom_xpath_inject "pom:project" "<groupId>org.jitsi</groupId>" .

# Fix missing version warnings
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-bundle-plugin']]" "
		<version>any</version>" .

# Fix resources path
%pom_xpath_replace "pom:resources/pom:resource/pom:directory" "
		<directory>src/main/resources</directory>" .

# Add an OSGi compilant MANIFEST.MF
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-bundle-plugin']]" "
	<extensions>true</extensions>"

# Add 'Export-Package' in MANIFEST.MF
%pom_xpath_remove "pom:Export-Package"

# Fix JAR name
%mvn_file :%{name} %{name}-%{version} %{name}

%build
# ffmpeg
%ant -v ffmpeg -Dffmpeg="%{_includedir}" -Dlame="" -Dvoamrwbenc="" -Dx264=""

# remove history.xml
rm -f src/main/resources/*/history.xml

# java
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8 -Dmaven.compiler.source=1.7 -Dmaven.compiler.target=1.7

%install
%mvn_install

