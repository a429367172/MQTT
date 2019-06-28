#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <bits/stdc++.h>
#include <QMainWindow>
#include <QTimer>
#include <QProcess>
#include <QDebug>
#include "serialservice.h"

using namespace std;

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    
private:
    Ui::MainWindow *ui;
    Posix_QextSerialPort *myCom;
    QTimer *timer;
    QProcess *client;

private slots:
    void ReadMycom();  //读取串口中的数据
    void on_pushButton_clicked();
};

#endif // MAINWINDOW_H
