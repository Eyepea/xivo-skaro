######################################################################
# Automatically generated by qmake (2.01a) jeu. f�vr. 1 18:28:19 2007
######################################################################

SBDIR = ../../switchboard/gui
TEMPLATE = app
TARGET = 
DEPENDPATH += .
INCLUDEPATH += . $${SBDIR}
CONFIG -= debug
CONFIG += static

# Input
HEADERS += confwidget.h baseengine.h mainwidget.h
HEADERS += popup.h xmlhandler.h remotepicwidget.h urllabel.h
HEADERS += servicepanel.h
HEADERS += $${SBDIR}/dialpanel.h      $${SBDIR}/logwidget.h           $${SBDIR}/logeltwidget.h
HEADERS += $${SBDIR}/directorypanel.h $${SBDIR}/extendedtablewidget.h $${SBDIR}/peerchannel.h
HEADERS += $${SBDIR}/peerwidget.h     $${SBDIR}/peeritem.h            $${SBDIR}/searchpanel.h

SOURCES += confwidget.cpp engine.cpp mainwidget.cpp main.cpp
SOURCES += popup.cpp xmlhandler.cpp remotepicwidget.cpp urllabel.cpp
SOURCES += servicepanel.cpp
SOURCES += $${SBDIR}/logwidget.cpp           $${SBDIR}/searchpanel.cpp  $${SBDIR}/peerwidget.cpp
SOURCES += $${SBDIR}/dialpanel.cpp           $${SBDIR}/logeltwidget.cpp $${SBDIR}/directorypanel.cpp
SOURCES += $${SBDIR}/extendedtablewidget.cpp $${SBDIR}/peerchannel.cpp  $${SBDIR}/peeritem.cpp

QT += network
QT += xml
RESOURCES += appli.qrc
TRANSLATIONS = xivoclient_fr.ts
RC_FILE = appli.rc

