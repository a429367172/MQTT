#-------------------------------------------------
#
# Project created by QtCreator 2019-06-20T20:36:49
#
#-------------------------------------------------

QT       += core gui

TARGET = hzy
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp \
    posix_qextserialport.cpp \
    qextserialbase.cpp \
    serialservice.cpp

HEADERS  += mainwindow.h \
    posix_qextserialport.h \
    qextserialbase.h \
    serialservice.h

FORMS    += mainwindow.ui
