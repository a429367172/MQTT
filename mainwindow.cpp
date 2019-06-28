#include "mainwindow.h"
#include "ui_mainwindow.h"

int TEMP;
int HUM;
double LIGHT;
int num[100];

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    //open serial
    QString portName = "/dev/ttySAC1";   //串口名
    myCom = new Posix_QextSerialPort(portName, QextSerialBase::Polling);
    if(myCom->open(QIODevice::ReadWrite)){
        qDebug() << "open serial seuccess!";
    } else {
        qDebug() << "open serial fail!";
        return;
    }
    myCom->setBaudRate(BAUD115200);
    myCom->setParity(PAR_NONE);
    myCom->setStopBits(STOP_1);
    myCom->setDataBits(DATA_8);
    myCom->setTimeout(10);
    myCom->setFlowControl(FLOW_OFF);
    timer = new QTimer();
    connect(timer, SIGNAL(timeout()), this,SLOT(ReadMycom()));
    timer->start(200);
}

MainWindow::~MainWindow()
{
    delete ui;
    delete myCom;
    delete timer;
}

void MainWindow::ReadMycom()
{
    int byteLen = myCom->bytesAvailable(); //返回串口缓冲区字节
    if(byteLen <= 0) return;               //串口内有数据才往下继续执行
    QByteArray temp = myCom->readAll();    //返回读取的字节
    QDataStream stream(&temp, QIODevice::ReadWrite);
    int cnt = 0;
    while (!stream.atEnd()) {
        qint8 a = 0;
        stream >> a;
        QString s = QString("%1").arg(a&0xFF,2,16,QLatin1Char('0'));
        s = s.toUpper();
        string str = s.toStdString();
        int n1 = ('0' <= str[0] && str[0] <= '9') ? str[0]-'0' : str[0] - 'A' + 10;
        int n2 = ('0' <= str[1] && str[1] <= '9') ? str[1]-'0' : str[1] - 'A' + 10;
        int n = n1*16 + n2;
        num[cnt++] = n;
    }
    int judge = 0;
    for (int i = 0; i < 11; i++) judge += num[i];
    if (num[3] == 2 && judge == num[11]) {
        TEMP = (num[5]<<8) + num[6];
        HUM = (num[7]<<8) + num[8];
        LIGHT = ((num[9]<<8)+num[10])*3012.9/(32768*4);
        ui->lineEdit->setText(QString::number(TEMP, 10));
        ui->lineEdit_2->setText(QString::number(HUM, 10));
        ui->lineEdit_3->setText(QString::number(LIGHT));
    }
}

void MainWindow::on_pushButton_clicked()
{
    QString program = "./mosquitto_pub";
    QStringList arguments;
    QFile file("ip");
    file.open(QIODevice::ReadOnly);
    QByteArray t = file.readAll();
    QString ip = QString(t);
    QString myip = "";
    int i;
    for (i = 0; i < ip.length(); i++) if ('0' <= ip[i] && ip[i] <= '9') break;
    int j;
    for (j = ip.length()-1; j >= 0; j--) if ('0' <= ip[j] && ip[j] <= '9') break;
    for (int x = i; x <= j; x++) {
        myip += ip[x];
    }
    arguments << "-h" << myip;
    arguments << "-p" << "61613";
    arguments << "-i" << "client1";
    arguments << "-u" << "admin";
    arguments << "-P" << "password";
    arguments << "-t" << "iot/";
    QString str = QString::number(TEMP, 10) + " " + QString::number(HUM, 10) + " "
            + QString::number(LIGHT);
    arguments << "-m" << str;
    client = new QProcess();
    client->start(program,arguments);
    if (client->waitForStarted()) {
        qDebug() << "client start!";
    }
}
