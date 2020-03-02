#!/bin/sh
set -e

OPENSSL_VERSION="1.0.1"
NGINX_VERSION="1.16.1"
DEPS="musl-dev gcc make pkgconfig perl zlib-dev pcre-dev"

apk --no-cache add $DEPS

mkdir /tmp/build
cd /tmp/build

# OpenSSL
cat > openssl_termios.patch <<EOF
diff --git a/crypto/ui/ui_openssl.c b/crypto/ui/ui_openssl.c
index 5832a73cf5..511a1d2baf 100644
--- a/crypto/ui/ui_openssl.c
+++ b/crypto/ui/ui_openssl.c
@@ -178,41 +178,9 @@
  * TERMIO, TERMIOS, VMS, MSDOS and SGTTY
  */

-#if defined(__sgi) && !defined(TERMIOS)
-# define TERMIOS
-# undef  TERMIO
-# undef  SGTTY
-#endif
-
-#if defined(linux) && !defined(TERMIO)
-# undef  TERMIOS
-# define TERMIO
-# undef  SGTTY
-#endif
-
-#ifdef _LIBC
-# undef  TERMIOS
-# define TERMIO
-# undef  SGTTY
-#endif
-
-#if !defined(TERMIO) && !defined(TERMIOS) && !defined(OPENSSL_SYS_VMS) && !defined(OPENSSL_SYS_MSDOS) && !defined(OPENSSL_SYS_MACINTOSH_CLASSIC) && !defined(MAC_OS_GUSI_SOURCE)
-# undef  TERMIOS
-# undef  TERMIO
-# define SGTTY
-#endif
-
-#if defined(OPENSSL_SYS_VXWORKS)
-#undef TERMIOS
-#undef TERMIO
-#undef SGTTY
-#endif
-
-#if defined(OPENSSL_SYS_NETWARE)
-#undef TERMIOS
+// HACK musl has only termios.h...
 #undef TERMIO
-#undef SGTTY
-#endif
+#define TERMIOS

 #ifdef TERMIOS
 # include <termios.h>
EOF

wget "https://www.openssl.org/source/old/$OPENSSL_VERSION/openssl-$OPENSSL_VERSION.tar.gz"
tar zxf "openssl-$OPENSSL_VERSION.tar.gz"

cd "openssl-$OPENSSL_VERSION/"
patch -p1 < ../openssl_termios.patch
./config --prefix=/usr/local --openssldir=/etc/ssl shared
make -j$(nproc) || true
make
make install_sw
cd ../

# nginx
wget "https://nginx.org/download/nginx-$NGINX_VERSION.tar.gz"
tar zxf "nginx-$NGINX_VERSION.tar.gz"
cd "nginx-$NGINX_VERSION/"
./configure --with-http_ssl_module
make -j$(nproc)
make install
cd ../

apk --no-cache del $DEPS
cd /
rm -r /tmp/build
