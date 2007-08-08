/*
XIVO CTI Clients : Xivo Client + Switchboard
Copyright (C) 2007  Proformatique

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
*/

/* $Revision$
   $Date$
*/

#include <QDebug>
#include <QMessageBox>
#include <QSettings>
#include <QStringList>
#include <QTcpSocket>
#include <QTime>
#include <QTimerEvent>

#include "baseengine.h"
#include "logeltwidget.h"
#include "popup.h"

const int REQUIRED_SERVER_VERSION = 1334;

/*! \brief Constructor.
 *
 * Construct the BaseEngine object and load settings.
 * The TcpSocket Object used to communicate with the server
 * is created and connected to the right slots/signals
 *
 * This constructor initialize the UDP socket and
 * the TCP listening socket.
 * It also connects signals with the right slots.
 */
BaseEngine::BaseEngine(QObject * parent)
        : QObject(parent),
	  m_serverhost(""), m_loginport(0), m_sbport(0),
          m_asterisk(""), m_protocol(""), m_userid(""), m_passwd(""),
          m_enabled_presence(false), m_enabled_cinfo(false),
          m_sessionid(""), m_state(ENotLogged),
	  m_listenport(0), m_pendingkeepalivemsg(0)
{
	m_ka_timerid = 0;
	m_try_timerid = 0;
	m_timer = -1;
	m_sbsocket     = new QTcpSocket(this);
	m_loginsocket  = new QTcpSocket(this);
	m_udpsocket    = new QUdpSocket(this);
	m_listenserver = new QTcpServer(this);
	loadSettings();
	deleteRemovables();

        qDebug() << "BaseEngine::BaseEngine() : tcpmode =" << m_tcpmode;

        /*  QTcpSocket signals :
            void connected ()
            void disconnected ()
            void error ( QAbstractSocket::SocketError socketError )
            void hostFound ()
            void stateChanged ( QAbstractSocket::SocketState socketState )
        */
        /* Signals inherited from QIODevice :
           void aboutToClose ()
           void bytesWritten ( qint64 bytes )
           void readyRead ()
        */

	// Connect socket signals
	connect(m_sbsocket, SIGNAL(connected()),
	        this, SLOT(socketConnected()));
	connect(m_sbsocket, SIGNAL(disconnected()),
	        this, SLOT(socketDisconnected()));
	connect(m_sbsocket, SIGNAL(hostFound()),
                this, SLOT(socketHostFound()));
	connect(m_sbsocket, SIGNAL(error(QAbstractSocket::SocketError)),
	        this, SLOT(socketError(QAbstractSocket::SocketError)));
	connect(m_sbsocket, SIGNAL(stateChanged(QAbstractSocket::SocketState)),
	        this, SLOT(socketStateChanged(QAbstractSocket::SocketState)));
	connect(m_sbsocket, SIGNAL(readyRead()),
                this, SLOT(socketReadyRead()));
        
	// init login socket for profile push
	connect( m_loginsocket, SIGNAL(connected()),
	         this, SLOT(identifyToTheServer()) );
	connect( m_loginsocket, SIGNAL(hostFound()),
	         this, SLOT(serverHostFound()) );
        connect( m_loginsocket, SIGNAL(readyRead()),
	         this, SLOT(processLoginDialog()) );
        
	// init listen server for profile push
	connect( m_listenserver, SIGNAL(newConnection()),
	         this, SLOT(handleProfilePush()) );
        
	// init UDP socket used for keep alive
	connect( m_udpsocket, SIGNAL(readyRead()),
		 this, SLOT(readKeepLoginAliveDatagrams()) );
        
	if(m_autoconnect)
		start();
}

/*! \brief Destructor
 */
BaseEngine::~BaseEngine()
{
        qDebug() << "BaseEngine::~BaseEngine()";
}

/*!
 * Load Settings from the registery/configuration file
 * Use default values when settings are not found.
 */
void BaseEngine::loadSettings()
{
        //qDebug() << "BaseEngine::loadSettings()";
	QSettings settings;
	m_serverhost = settings.value("engine/serverhost").toString();
	m_loginport  = settings.value("engine/loginport", 5000).toUInt();
	m_sbport     = settings.value("engine/serverport", 5003).toUInt();

        m_enabled_presence = settings.value("engine/fct_presence", false).toBool();
        m_enabled_cinfo    = settings.value("engine/fct_cinfo",    false).toBool();

	m_asterisk   = settings.value("engine/asterisk").toString();
	m_protocol   = settings.value("engine/protocol").toString();
	m_userid     = settings.value("engine/userid").toString();
	m_passwd     = settings.value("engine/passwd").toString();

	m_autoconnect = settings.value("engine/autoconnect", false).toBool();
	m_trytoreconnect = settings.value("engine/trytoreconnect", false).toBool();
	m_trytoreconnectinterval = settings.value("engine/trytoreconnectinterval", 20*1000).toUInt();
	m_keepaliveinterval = settings.value("engine/keepaliveinterval", 20*1000).toUInt();

	m_historysize = settings.value("engine/historysize", 8).toUInt();
	m_tcpmode = settings.value("engine/tcpmode", false).toBool();

	m_availstate = settings.value("engine/availstate", "available").toString();
}

/*!
 * Save Settings to the registery/configuration file
 */
void BaseEngine::saveSettings()
{
        //qDebug() << "BaseEngine::saveSettings()";
	QSettings settings;
	settings.setValue("engine/serverhost", m_serverhost);
	settings.setValue("engine/loginport",  m_loginport);
	settings.setValue("engine/serverport", m_sbport);

	settings.setValue("engine/fct_presence", m_enabled_presence);
	settings.setValue("engine/fct_cinfo",    m_enabled_cinfo);

	settings.setValue("engine/asterisk",   m_asterisk);
	settings.setValue("engine/protocol",   m_protocol);
	settings.setValue("engine/userid",     m_userid);
	settings.setValue("engine/passwd",     m_passwd);

	settings.setValue("engine/autoconnect", m_autoconnect);
	settings.setValue("engine/trytoreconnect", m_trytoreconnect);
	settings.setValue("engine/trytoreconnectinterval", m_trytoreconnectinterval);
	settings.setValue("engine/keepaliveinterval", m_keepaliveinterval);

	settings.setValue("engine/historysize", m_historysize);
	settings.setValue("engine/tcpmode", m_tcpmode);

	settings.setValue("engine/availstate", m_availstate);
}

/*!
 *
 */
void BaseEngine::setEnabledPresence(bool b) {
	if(b != m_enabled_presence) {
		m_enabled_presence = b;
		if(state() == ELogged)
			availAllowChanged(b);
	}
}

bool BaseEngine::enabledPresence() {
        return m_enabled_presence;
}

void BaseEngine::setEnabledCInfo(bool b) {
	if(b != m_enabled_cinfo)
		m_enabled_cinfo = b;
}

bool BaseEngine::enabledCInfo() {
        return m_enabled_cinfo;
}

void BaseEngine::initListenSocket()
{
	qDebug() << "BaseEngine::initListenSocket()";
	if (!m_listenserver->listen())
	{
		QMessageBox::critical(NULL, tr("Critical error"),
		                            tr("Unable to start the server: %1.")
		                            .arg(m_listenserver->errorString()));
                m_listenserver->close();
		return;
	}
	m_listenport = m_listenserver->serverPort();
	qDebug() << "BaseEngine::initListenSocket()" << m_listenport;
}

/*! \brief Starts the connection to the server
 * This method starts the login process by connection
 * to the server.
 */
void BaseEngine::start()
{
	qDebug() << "BaseEngine::start()" << m_serverhost << m_loginport << m_enabled_presence << m_enabled_cinfo;

	// (In case the TCP sockets were attempting to connect ...) aborts them first
	m_sbsocket->abort();
	m_loginsocket->abort();
        m_listenserver->close();
        m_udpsocket->abort();

        if(! m_tcpmode) {
                if(m_enabled_cinfo)
                        initListenSocket();
                m_udpsocket->bind();
        }

        connectSocket();
}

/*! \brief Closes the connection to the server
 * This method disconnect the engine from the server
 */
void BaseEngine::stop()
{
	qDebug() << "BaseEngine::stop()";

        if(! m_tcpmode) {
                if(m_sessionid != "") {
                        QString outline = "STOP ";
                        outline.append(m_asterisk + "/" + m_protocol.toLower() + m_userid);
                        outline.append(" SESSIONID ");
                        outline.append(m_sessionid);
                        outline.append("\r\n");
                        m_udpsocket->writeDatagram( outline.toAscii(),
                                                    m_serveraddress, m_loginport + 1 );
                }
                m_udpsocket->close();
        }

        m_listenserver->close();
        m_listenport = 0;

	m_sbsocket->disconnectFromHost();

	stopKeepAliveTimer();
	stopTryAgainTimer();
	setState(ENotLogged);
	m_sessionid = "";
}

/*! \brief initiate connection to the server
 */
void BaseEngine::connectSocket()
{
        if(m_tcpmode) {
                qDebug() << "BaseEngine::connectSocket()" << m_serverhost << m_sbport;
                m_sbsocket->connectToHost(m_serverhost, m_sbport);
        } else {
                qDebug() << "BaseEngine::connectSocket()" << m_serverhost << m_loginport;
                m_loginsocket->connectToHost(m_serverhost, m_loginport);
        }
}

bool BaseEngine::tcpmode() const
{
        return m_tcpmode;
}

void BaseEngine::setTcpmode(bool b)
{
        m_tcpmode = b;
}

const QString & BaseEngine::getCapabilities() const
{
        return m_capabilities;
}

/*!
 * sets the availability state and call keepLoginAlive() if needed
 *
 * \sa setAvailable()
 * \sa setAway()
 * \sa setBeRightBack()
 * \sa setOutToLunch()
 * \sa setDoNotDisturb()
 */
void BaseEngine::setAvailState(const QString & newstate)
{
	if(m_availstate != newstate) {
		QSettings settings;
		m_availstate = newstate;
		settings.setValue("engine/availstate", m_availstate);
		keepLoginAlive();
	}
}

const QString & BaseEngine::getAvailState() const
{
        return m_availstate;
}

void BaseEngine::setAvailable()
{
	setAvailState("available");
}

void BaseEngine::setAway()
{
	setAvailState("away");
}

void BaseEngine::setBeRightBack()
{
	setAvailState("berightback");
}

void BaseEngine::setOutToLunch()
{
	setAvailState("outtolunch");
}

void BaseEngine::setDoNotDisturb()
{
	setAvailState("donotdisturb");
}

/*! \brief send a command to the server 
 * The m_pendingcommand is sent on the socket.
 *
 * \sa m_pendingcommand
 */
void BaseEngine::sendTCPCommand()
{
	// qDebug() << "BaseEngine::sendTCPCommand()" << m_pendingcommand;
	m_sbsocket->write((m_pendingcommand + "\r\n"/*"\n"*/).toAscii());
}

void BaseEngine::sendUDPCommand(const QString & command)
{
	// qDebug() << "BaseEngine::sendUDPCommand()" << command;
	if(m_state == ELogged) {
		QString outline = "COMMAND ";
		outline.append(m_asterisk + "/" + m_protocol.toLower() + m_userid);
		outline.append(" SESSIONID " + m_sessionid + " " + command);
		qDebug() << "BaseEngine::sendUDPCommand()" << outline;
                outline.append("\r\n");
		m_udpsocket->writeDatagram( outline.toAscii(),
					    m_serveraddress, m_loginport + 1 );
	} else {
		qDebug() << "not logged in : command not sent :" << command;
	}
}

void BaseEngine::sendCommand(const QString & command)
{
        if(m_tcpmode) {
                if(m_sbsocket->state() == QAbstractSocket::ConnectedState) {
                        m_pendingcommand = command;
                        sendTCPCommand();
                }
        } else
                sendUDPCommand(command);
}

/*! \brief parse history command response
 *
 * parse the history command response from the server and
 * trigger the update of the call history panel.
 *
 * \sa Logwidget
 */
void BaseEngine::processHistory(const QStringList & histlist)
{
	int i;
	for(i=0; i+6<=histlist.size(); i+=6)
	{
		// DateTime; CallerID; duration; Status?; peer; IN/OUT
		//qDebug() << histlist[i+0] << histlist[i+1]
		//         << histlist[i+2] << histlist[i+3]
		//         << histlist[i+4] << histlist[i+5];
		QDateTime dt = QDateTime::fromString(histlist[i+0], Qt::ISODate);
		QString callerid = histlist[i+1];
		int duration = histlist[i+2].toInt();
		QString status = histlist[i+3];
		QString peer = histlist[i+4];
		LogEltWidget::Direction d;
		d = (histlist[i+5] == "IN") ? LogEltWidget::InCall : LogEltWidget::OutCall;
		//qDebug() << dt << callerid << duration << peer << d;
		updateLogEntry(dt, duration, peer, (int)d);
	}
}

/*! \brief called when the socket is first connected
 */
void BaseEngine::socketConnected()
{
	qDebug() << "BaseEngine::socketConnected()";
	stopTryAgainTimer();
	/* do the login/identification ? */
        setMyClientId();
	m_pendingcommand = "login " + m_asterisk + " "
                + m_protocol + " " + m_userid + " " + m_availstate + " " + m_clientid;
        // login <asterisk> <techno> <id>
	sendTCPCommand();
}

/*! \brief called when the socket is disconnected from the server
 */
void BaseEngine::socketDisconnected()
{
	qDebug() << "BaseEngine::socketDisconnected()";
        delogged();
	emitTextMessage(tr("Connection lost with XIVO Daemon"));
	startTryAgainTimer();
	//removePeers();
	//connectSocket();
}

/*! \brief cat host found socket signal
 *
 * This slot is connected to the hostFound() signal of the m_sbsocket
 */
void BaseEngine::socketHostFound()
{
	qDebug() << "BaseEngine::socketHostFound()" << m_sbsocket->peerAddress();
}

/*! \brief cat host found socket signal
 * This slot is connected to the hostFound() signal of the m_loginsocket
 */
void BaseEngine::serverHostFound()
{
	qDebug() << "BaseEngine::serverHostFound()" << m_loginsocket->peerAddress();
}

/*! \brief catch socket errors
 */
void BaseEngine::socketError(QAbstractSocket::SocketError socketError)
{
	qDebug() << "BaseEngine::socketError(" << socketError << ")";
	switch(socketError)
	{
	case QAbstractSocket::ConnectionRefusedError:
		emitTextMessage(tr("Connection refused"));
		if(m_timer != -1)
		{
			killTimer(m_timer);
		 	m_timer = -1;
		}
		//m_timer = startTimer(2000);
		break;
	case QAbstractSocket::HostNotFoundError:
		emitTextMessage(tr("Host not found"));
		break;
	case QAbstractSocket::UnknownSocketError:
		emitTextMessage(tr("Unknown socket error"));
		break;
	default:
		break;
	}
}

/*! \brief receive signals of socket state change
 *
 * useless...
 */
void BaseEngine::socketStateChanged(QAbstractSocket::SocketState socketState)
{
	qDebug() << "BaseEngine::socketStateChanged(" << socketState << ")";
	if(socketState == QAbstractSocket::ConnectedState) {
		if(m_timer != -1)
		{
			killTimer(m_timer);
			m_timer = -1;
		}
		//startTimer(3000);
	}
}

/*! \brief update Peers 
 *
 * update peers and calls
 */
void BaseEngine::updatePeers(const QStringList & liststatus)
{
	const int nfields0 = 11; // 0th order size (per-phone/line informations)
	const int nfields1 = 6;  // 1st order size (per-channel informations)
	QStringList chanIds;
	QStringList chanStates;
	QStringList chanOthers;

	// liststatus[0] is a dummy field, only used for debug on the daemon side
	// p/(asteriskid)/(context)/(protocol)/(phoneid)/(phonenum)
	
	if(liststatus.count() < 11)
	{
		// not valid
		qDebug() << "Bad data from the server :" << liststatus;
		return;
	}

	//<who>:<asterisk_id>:<tech(SIP/IAX/...)>:<phoneid>:<numero>:<contexte>:<dispo>:<etat SIP/XML>:<etat VM>:<etat Queues>: <nombre de liaisons>:
	QString context = liststatus[5];
	QString pname   = "p/" + liststatus[1] + "/" + context + "/"
		+ liststatus[2] + "/" + liststatus[3] + "/" + liststatus[4];
	QString InstMessAvail   = liststatus[6];
	QString SIPPresStatus   = liststatus[7];
	QString VoiceMailStatus = liststatus[8];
	QString QueueStatus     = liststatus[9];
	int nchans = liststatus[10].toInt();
	if(liststatus.size() == nfields0 + nfields1 * nchans) {
		for(int i = 0; i < nchans; i++) {
			//  <channel>:<etat du channel>:<nb de secondes dans cet etat>:<to/from>:<channel en liaison>:<numero en liaison>
			int refn = nfields0 + nfields1 * i;
			QString displayedNum;
			
			SIPPresStatus = liststatus[refn + 1];
			chanIds << ("c/" + liststatus[1] + "/" + context + "/" + liststatus[refn]);
			chanStates << liststatus[refn + 1];
			if((liststatus[refn + 5] == "") ||
			   (liststatus[refn + 5] == "<Unknown>") ||
			   (liststatus[refn + 5] == "<unknown>") ||
			   (liststatus[refn + 5] == "anonymous") ||
			   (liststatus[refn + 5] == "(null)"))
				displayedNum = tr("Unknown Number");
			else
				displayedNum = liststatus[refn + 5];

			chanOthers << displayedNum;
                        if(m_is_a_switchboard)
                                updateCall("c/" + liststatus[1] + "/" + context + "/" + liststatus[refn],
                                           liststatus[refn + 1],
                                           liststatus[refn + 2].toInt(), liststatus[refn + 3],
                                           liststatus[refn + 4], displayedNum,
                                           pname);
		}
	}

	updatePeer(pname, m_callerids[pname],
	           InstMessAvail, SIPPresStatus, VoiceMailStatus, QueueStatus,
	           chanIds, chanStates, chanOthers);
        if(m_is_a_switchboard)
                if(   (m_userid == liststatus[3])
                      && (m_dialcontext == liststatus[5]))
                        updateMyCalls(chanIds, chanStates, chanOthers);
}

/*! \brief update a caller id 
 */
void BaseEngine::updateCallerids(const QStringList & liststatus)
{
	QString pname = "p/" + liststatus[1] + "/" + liststatus[5] + "/"
		+ liststatus[2] + "/" + liststatus[3] + "/" + liststatus[4];
	QString pcid = liststatus[6];
	// liststatus[7] => group informations
	m_callerids[pname] = pcid;
}

bool BaseEngine::parseCommand(const QStringList & listitems)
{
	QSettings settings;
        bool b = false;
        if(listitems[0].toLower() == "callerids") {
                QStringList listpeers = listitems[1].split(";");
                for(int i = 0 ; i < listpeers.size() - 1; i++) {
                        QStringList liststatus = listpeers[i].split(":");
                        updateCallerids(liststatus);
                }
                askPeers();
        } else if(listitems[0].toLower() == "history") {
                processHistory(listitems[1].split(";"));
        } else if(listitems[0].toLower() == "directory-response") {
                directoryResponse(listitems[1]);
        } else if(listitems[0].toLower() == QString("update")) {
                QStringList liststatus = listitems[1].split(":");
                updatePeers(liststatus);
                callsUpdated();
        } else if(listitems[0].toLower() == QString("peeradd")) {
                QStringList listpeers = listitems[1].split(";");
                for(int i = 0 ; i < listpeers.size() - 1; i++) {
                        QStringList liststatus = listpeers[i].split(":");
                        if(liststatus.size() > 13) {
                                QStringList listcids = liststatus;
                                listcids[6] = liststatus[11];
                                listcids[7] = liststatus[12];
                                listcids[8] = liststatus[13];
                                // remove [> 8] elements ?
                                updateCallerids(listcids);
                        }
                        updatePeers(liststatus);
                }
        } else if(listitems[0].toLower() == QString("peerremove")) {
                QStringList listpeers = listitems[1].split(";");
                for(int i = 0 ; i < listpeers.size() - 1; i++) {
                        QStringList liststatus = listpeers[i].split(":");
                        QString toremove = "p/" + liststatus[1] + "/" + \
                                liststatus[5] + "/" + liststatus[2] + "/" + \
                                liststatus[3] + "/" + liststatus[4];
                        removePeer(toremove);
                }
        } else if(listitems[0].toLower() == QString("hints")) {
                QStringList listpeers = listitems[1].split(";");
                qDebug() << "BaseEngine::parseCommand() : hints" << listpeers;
                for(int i = 0 ; i < listpeers.size() - 1; i++) {
                        QStringList liststatus = listpeers[i].split(":");
                        updatePeers(liststatus);
                }

                b = true;

                if(m_is_a_switchboard) {
                        callsUpdated();
                        QString myfullid = settings.value("monitor/peer").toString();
                        if(myfullid.size() == 0)
                                myfullid = "p/" + m_asterisk + "/" + m_dialcontext + "/" + m_protocol + "/" + m_userid + "/" + m_extension;
                        QString myname = m_callerids[myfullid];
                        if(myname == "")
                                monitorPeer(myfullid, tr("Unknown CallerId") + " (" + myfullid + ")");
                        else
                                monitorPeer(myfullid, myname);
                }
        } else if(listitems[0].toLower() == QString("message")) {
                QTime currentTime = QTime::currentTime();
                QStringList message = listitems[1].split("::");
                // message[0] : emitter name
                if(message.size() == 2) {
                        emitTextMessage(message[0] + tr(" said : ") + message[1]);
                } else {
                        emitTextMessage(tr("Unknown") + tr(" said : ") + listitems[1]);
                }
        } else if(listitems[0].toLower() == QString("featuresupdate")) {
                QStringList listpeers = listitems[1].split(";");
                if(listpeers.size() == 5)
                        if((m_monitored_context == listpeers[0]) && (m_monitored_userid == listpeers[2]))
                                initFeatureFields(listpeers[3], listpeers[4]);
        } else if(listitems[0].toLower() == QString("featuresget")) {
                QStringList listpeers = listitems[1].split(";");
                disconnectFeatures();
                resetFeatures();
                if(listpeers.size() > 1)
                        for(int i=0; i<listpeers.size()-1; i+=2)
                                initFeatureFields(listpeers[i], listpeers[i+1]);
                connectFeatures();
        } else if(listitems[0].toLower() == QString("featuresput")) {
                qDebug() << "received ack from featuresput :" << listitems;
        } else if(listitems[0] != "")
                qDebug() << "unknown command" << listitems[0];

        return b;
}

/*! \brief called when data are ready to be read on the socket.
 *
 * Read and process the data from the server.
 */
void BaseEngine::socketReadyRead()
{
        //qDebug() << "BaseEngine::socketReadyRead()";
	//QByteArray data = m_sbsocket->readAll();
	bool b = false;
	while(m_sbsocket->canReadLine()) {
		QByteArray data  = m_sbsocket->readLine();
		QString line     = QString::fromUtf8(data);
		QStringList list = line.trimmed().split("=");

		if(list.size() == 2) {
                        if(list[0].toLower() == "loginok") {
				QStringList params = list[1].split(";");
                                qDebug() << "BaseEngine::socketReadyRead()" << params;
				if(params.size() > 2) {
					m_dialcontext = params[0];
					m_extension = params[1];
                                        m_capabilities = params[2];
                                        logged();
                                        if(m_is_a_switchboard) /* ask here because not ready when the widget builds up */
                                                askCallerIds();
                                }
			} else if(list[0].toLower() == "loginko") {
                                stop();
			} else
                                b = parseCommand(list);
		}
	}
	if(b)
		emitTextMessage(tr("Peers' status updated"));
}

/*! \brief transfers to the typed number
 */
void BaseEngine::transferToNumber(const QString & chan)
{
        if(m_numbertodial.size() > 0) {
                qDebug() << "BaseEngine::transferToNumber()" << chan << m_numbertodial;
                transferCall(chan, m_numbertodial);
        }
}

/*! \brief send an originate command to the server
 */
void BaseEngine::textEdited(const QString & text)
{
        m_numbertodial = text;
}

/*! \brief send an originate command to the server
 */
void BaseEngine::originateCall(const QString & src, const QString & dst)
{
	qDebug() << "BaseEngine::originateCall()" << src << dst;
	QStringList dstlist = dst.split("/");
	if(dstlist.size() > 5)
	{
		m_pendingcommand = "originate " + src + " " + dst;
		//		+ dstlist[0] + "/" + dstlist[1] + "/" + m_dialcontext + "/"
		//	+ dstlist[3] + "/" + dstlist[4] + "/" + dstlist[5];
	}
	else
	{
		m_pendingcommand = "originate " + src + " p/" + m_asterisk + "/"
		     + m_dialcontext + "/" + "/" + "/" + dst;
	}
	sendTCPCommand();
}

/*! \brief dial (originate with known src)
 */
void BaseEngine::dialFullChannel(const QString & dst)
{
	qDebug() << "BaseEngine::dialFullChannel()" << dst;
        sendCommand("originate p/" +
                    m_asterisk + "/" + m_dialcontext + "/" + m_protocol + "/" +
                    m_userid + "/" + m_extension +
                    " " + dst);
}

/*! \brief dial (originate with known src)
 */
void BaseEngine::dialExtension(const QString & dst)
{
	qDebug() << "BaseEngine::dialExtension()" << dst;
        sendCommand("originate p/" +
                    m_asterisk + "/" + m_dialcontext + "/" + m_protocol + "/" + 
                    m_userid + "/" + m_extension +
                    " " + "p/" + m_asterisk + "/" + m_dialcontext + "/" + "/" + "/" + dst);
}

/*! \brief send a transfer call command to the server
 */
void BaseEngine::transferCall(const QString & src, const QString & dst)
{
	qDebug() << "BaseEngine::transferCall()" << src << dst;
	QStringList dstlist = dst.split("/");
	if(dstlist.size() >= 6)
	{
		m_pendingcommand = "transfer " + src + " "
			+ dstlist[0] + "/" + dstlist[1] + "/" + m_dialcontext + "/"
			+ dstlist[3] + "/" + dstlist[4] + "/" + dstlist[5];
	}
	else
	{
		m_pendingcommand = "transfer " + src + " p/" + m_asterisk + "/"
		     + m_dialcontext + "/" + "/" + "/" + dst;
	}
	sendTCPCommand();
}

/*! \brief intercept a call (a channel)
 *
 * The channel is transfered to "Me"
 *
 * \sa transferCall
 */
void BaseEngine::interceptCall(const QString & src)
{
	qDebug() << "BaseEngine::interceptCall()" << src;
	m_pendingcommand = "transfer " + src + " p/"
	        + m_asterisk + "/" + m_dialcontext + "/"
			+ m_protocol + "/" + "/" + m_extension; 
	sendTCPCommand();
}

/*! \brief hang up a channel
 *
 * send a hang up command to the server
 */
void BaseEngine::hangUp(const QString & channel)
{
	qDebug() << "BaseEngine::hangUp()" << channel;
	m_pendingcommand = "hangup " + channel;
	sendTCPCommand();
}

/*! \brief send the directory search command to the server
 *
 * \sa directoryResponse()
 */
void BaseEngine::searchDirectory(const QString & text)
{
	qDebug() << "BaseEngine::searchDirectory()" << text;
        sendCommand("directory-search " + text);
}

/*! \brief ask history for an extension 
 */
void BaseEngine::requestHistory(const QString & peer, int mode)
{
	/* mode = 0 : Out calls
	 * mode = 1 : In calls
	 * mode = 2 : Missed calls */
	if(mode >= 0) {
                qDebug() << "BaseEngine::requestHistory()" << peer;
                sendCommand("history " + peer + " " + QString::number(m_historysize) + " " + QString::number(mode));
        }
}

// === Getter and Setters ===
/* \brief set server address
 *
 * Set server host name and server port
 */
void BaseEngine::setAddress(const QString & host, quint16 port)
{
        qDebug() << "BaseEngine::setAddress()" << port;
	m_serverhost = host;
	m_sbport = port;
}

/*! \brief get server IP address */
const QString & BaseEngine::serverip() const
{
	return m_serverhost;
}

/*! \brief get server port */
const quint16 BaseEngine::sbPort() const
{
	return m_sbport;
}

const QString & BaseEngine::serverast() const
{
        return m_asterisk;
}

void BaseEngine::setServerip(const QString & serverip)
{
	m_serverhost = serverip;
}

void BaseEngine::setServerAst(const QString & serverast)
{
	m_asterisk = serverast;
}

const quint16 BaseEngine::loginPort() const
{
	return m_loginport;
}

void BaseEngine::setLoginPort(const quint16 & port)
{
	m_loginport = port;
}

const QString & BaseEngine::userId() const
{
	return m_userid;
}

void BaseEngine::setUserId(const QString & userid)
{
	m_userid = userid;
}

const QString & BaseEngine::protocol() const
{
	return m_protocol;
}

void BaseEngine::setProtocol(const QString & protocol)
{
	m_protocol = protocol;
}

const QString & BaseEngine::password() const
{
	return m_passwd;
}

void BaseEngine::setPassword(const QString & passwd)
{
	m_passwd = passwd;
}

const QString & BaseEngine::dialContext() const
{
	return m_dialcontext;
}

void BaseEngine::setDialContext(const QString & dialcontext)
{
	m_dialcontext = dialcontext;
}

void BaseEngine::setTrytoreconnect(bool b)
{
	m_trytoreconnect = b;
}

bool BaseEngine::trytoreconnect() const
{
	return m_trytoreconnect;
}

void BaseEngine::initFeatureFields(const QString & field, const QString & value)
{
	//	qDebug() << field << value;
	if(field == "VM")
		voiceMailChanged(value == "1");
	else if(field == "DND")
		dndChanged(value == "1");
	else if(field == "Screen")
		callFilteringChanged(value == "1");
	else if(field == "Record")
		callRecordingChanged(value == "1");
	else if(field == "FWD/Unc")
		uncondForwardChanged(value.split(":")[0] == "1", value.split(":")[1]);
	else if(field == "FWD/Unc/Status")
		uncondForwardChanged(value == "1");
	else if(field == "FWD/Unc/Number")
		uncondForwardChanged(value);
	else if(field == "FWD/Busy")
		forwardOnBusyChanged(value.split(":")[0] == "1", value.split(":")[1]);
	else if(field == "FWD/Busy/Status")
		forwardOnBusyChanged(value == "1");
	else if(field == "FWD/Busy/Number")
		forwardOnBusyChanged(value);
	else if(field == "FWD/RNA")
		forwardOnUnavailableChanged(value.split(":")[0] == "1", value.split(":")[1]);
	else if(field == "FWD/RNA/Status")
		forwardOnUnavailableChanged(value == "1");
	else if(field == "FWD/RNA/Number")
		forwardOnUnavailableChanged(value);
}

/*!
 * Process incoming UDP datagrams which are likely to be 
 * response from keep alive messages.
 * If the response is not 'OK', goes to
 * the "not connected" state.
 */
void BaseEngine::readKeepLoginAliveDatagrams()
{
	char buffer[2048];
	int len;
	qDebug() << "BaseEngine::readKeepLoginAliveDatagrams()";
	while( m_udpsocket->hasPendingDatagrams() )
	{
		len = m_udpsocket->readDatagram(buffer, sizeof(buffer)-1);
		if(len == 0)
			continue;
		buffer[len] = '\0';
		QString line     = QString::fromUtf8(buffer);
		QStringList qsl  = line.trimmed().split(" ");
		QStringList list = line.trimmed().split("=");

		QString reply = qsl[0];

		if(reply == "DISC") {
			setState(ENotLogged);
			qDebug() << qsl; //reply;
		} else if(reply == "ERROR") {
			qDebug() << "BaseEngine::readKeepLoginAliveDatagrams()" << qsl;
                        stopKeepAliveTimer();
                        stop();
                        m_pendingkeepalivemsg = 0;
                        startTryAgainTimer();
		} else if(reply != "OK")
                        parseCommand(list);
		m_pendingkeepalivemsg = 0;
	}
}

void BaseEngine::stopKeepAliveTimer()
{
	if( m_ka_timerid > 0 )
	{
		killTimer(m_ka_timerid);
		m_ka_timerid = 0;
	}
}

void BaseEngine::stopTryAgainTimer()
{
	if( m_try_timerid > 0 )
	{
		killTimer(m_try_timerid);
		m_try_timerid = 0;
	}
}

void BaseEngine::startTryAgainTimer()
{
	if( m_try_timerid == 0 && m_trytoreconnect )
	{
		m_try_timerid = startTimer(m_trytoreconnectinterval);
	}
}

void BaseEngine::setHistorySize(uint size)
{
	m_historysize = size;
}

uint BaseEngine::historysize() const
{
	return m_historysize;
}

uint BaseEngine::trytoreconnectinterval() const
{
	return m_trytoreconnectinterval;
}

/*!
 * Setter for property m_trytoreconnectinterval
 * Restart timer if the value changed.
 *
 * \sa trytoreconnectinterval
 */
void BaseEngine::setTrytoreconnectinterval(uint i)
{
	if( m_trytoreconnectinterval != i )
	{
		m_trytoreconnectinterval = i;
		if(m_try_timerid > 0)
		{
			killTimer(m_try_timerid);
			m_try_timerid = startTimer(m_trytoreconnectinterval);
		}
	}
}

/*! \brief implement timer event
 *
 * does nothing
 */
void BaseEngine::timerEvent(QTimerEvent * event)
{
	int timerId = event->timerId();
        qDebug() << "BaseEngine::timerEvent() timerId=" << timerId << m_ka_timerid << m_try_timerid;
	if(timerId == m_ka_timerid) {
                if(! m_tcpmode) {
                        keepLoginAlive();
                        event->accept();
                }
        } else if(timerId == m_try_timerid) {
                emitTextMessage(tr("Attempting to reconnect to server"));
		start();
		event->accept();
	} else {
		event->ignore();
	}
}

void BaseEngine::setIsASwitchboard(bool b)
{
	m_is_a_switchboard = b;
}

bool BaseEngine::isASwitchboard()
{
	return m_is_a_switchboard;
}

void BaseEngine::deleteRemovables()
{
	m_removable.clear();
}

void BaseEngine::addRemovable(const QMetaObject * metaobject)
{
	m_removable.append(metaobject);
}

bool BaseEngine::isRemovable(const QMetaObject * metaobject)
{
	for(int i = 0; i < m_removable.count() ; i++)
		if (metaobject == m_removable[i])
			return true;
	return false;
}

void BaseEngine::setVoiceMail(bool b)
{
        sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " VM " + QString(b ? "1" : "0"));
}

void BaseEngine::setCallRecording(bool b)
{
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " Record " + QString(b ? "1" : "0"));
}

void BaseEngine::setCallFiltering(bool b)
{
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " Screen " + QString(b ? "1" : "0"));
}

void BaseEngine::setDnd(bool b)
{
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " DND " + QString(b ? "1" : "0"));
}

void BaseEngine::setForwardOnUnavailable(bool b, const QString & dst)
{
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " FWD/RNA/Status " + QString(b ? "1" : "0"));
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " FWD/RNA/Number " + dst);
}

void BaseEngine::setForwardOnBusy(bool b, const QString & dst)
{
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " FWD/Busy/Status " + QString(b ? "1" : "0"));
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " FWD/Busy/Number " + dst);
}

void BaseEngine::setUncondForward(bool b, const QString & dst)
{
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " FWD/Unc/Status " + QString(b ? "1" : "0"));
	sendCommand("featuresput " + m_monitored_context + " " + m_monitored_userid + " FWD/Unc/Number " + dst);
}

void BaseEngine::askFeatures(const QString & peer)
{
        qDebug() << "BaseEngine::askFeatures()" << peer;
        m_monitored_context = m_dialcontext;
        m_monitored_userid = m_userid;
        QStringList peerp = peer.split("/");
        if(peerp.size() == 6) {
                m_monitored_context = peerp[2];
                m_monitored_userid = peerp[5];
        }
        sendCommand("featuresget " + m_monitored_context + " " + m_monitored_userid);
}

void BaseEngine::askPeers()
{
        sendCommand("hints");
}

void BaseEngine::askCallerIds()
{
        qDebug() << "BaseEngine::askCallerIds()";
	sendCommand("callerids");
}

void BaseEngine::setAutoconnect(bool b)
{
	m_autoconnect = b;
}

bool BaseEngine::autoconnect() const
{
	return m_autoconnect;
}

uint BaseEngine::keepaliveinterval() const
{
	return m_keepaliveinterval;
}

/*!
 * Setter for the m_keepaliveinterval property.
 * if the value is changed, existing timer is restarted.
 *
 * \sa keepaliveinterval
 */
void BaseEngine::setKeepaliveinterval(uint i)
{
	if(i != m_keepaliveinterval)
	{
		m_keepaliveinterval = i;
		if(m_ka_timerid > 0)
		{
			killTimer(m_ka_timerid);
			m_ka_timerid = startTimer(m_keepaliveinterval);
		}
	}
}

const BaseEngine::EngineState BaseEngine::state() const
{
	return m_state;
}

/*!
 * setter for the m_state property.
 * If the state is becoming ELogged, the
 * signal logged() is thrown.
 * If the state is becoming ENotLogged, the
 * signal delogged() is thrown.
 */
void BaseEngine::setState(EngineState state)
{
	if(state != m_state) {
		m_state = state;
		if(state == ELogged) {
			stopTryAgainTimer();
			if(m_enabled_presence) availAllowChanged(true);
			logged();
		} else if(state == ENotLogged) {
			availAllowChanged(false);
			delogged();
		}
	}
}

/*!
 * Builds a string defining who is the client (SB or XC @ (X11, WIN, MAC))
*/
void BaseEngine::setMyClientId()
{
        QString whatami;
        if(m_is_a_switchboard)
                whatami = QString("SB");
        else
                whatami = QString("XC");

#if defined(Q_WS_X11)
        m_clientid = QString(whatami + "@X11");
#elif defined(Q_WS_WIN)
        m_clientid = QString(whatami + "@WIN");
#elif defined(Q_WS_MAC)
        m_clientid = QString(whatami + "@MAC");
#else
        m_clientid = QString(whatami + "@unknwon");
#endif
}

/*!
 * Perform the first login step once the TCP connection is established.
 */
void BaseEngine::identifyToTheServer()
{
	QString outline;
	m_serveraddress = m_loginsocket->peerAddress();
	qDebug() << "BaseEngine::identifyToTheServer()" << m_serveraddress;
        setMyClientId();
	outline.append("LOGIN " + m_asterisk + "/" + m_protocol.toLower() + m_userid + " " + m_clientid);
	qDebug() << "BaseEngine::identifyToTheServer() : " << outline;
	outline.append("\r\n");
	m_loginsocket->write(outline.toAscii());
	m_loginsocket->flush();
}

/*!
 * Perform the following of the login process after identifyToTheServer()
 * made the first step.
 * Theses steps are : sending the password, sending the port,
 *   just reading the session id from server response.
 * The state is changed accordingly.
 */
void BaseEngine::processLoginDialog()
{
	char buffer[256];
	int len;
	qDebug() << "BaseEngine::processLoginDialog()";
	if(m_tcpmode && (m_state == ELogged)) {
		Popup * popup = new Popup(m_loginsocket, m_sessionid);
		connect( popup, SIGNAL(destroyed(QObject *)),
		         this, SLOT(popupDestroyed(QObject *)) );
		connect( popup, SIGNAL(wantsToBeShown(Popup *)),
			 this, SLOT(profileToBeShown(Popup *)) );
		popup->streamNewData();
		return;
	}
	if(!m_loginsocket->canReadLine())
	{
		qDebug() << "no line ready to be read";
		return;
	}
	len = m_loginsocket->readLine(buffer, sizeof(buffer));
	if(len<0)
	{
		qDebug() << "readLine() returned -1, closing socket";
		m_loginsocket->close();
		setState(ENotLogged);
		return;
	}
	QString readLine = QString::fromAscii(buffer);
	QString outline;
	if(readLine.startsWith("Send PASS"))
	{
		outline = "PASS ";
		outline.append(m_passwd);
	}
	else if(readLine.startsWith("Send PORT"))
	{
		if(m_tcpmode) {
			outline = "TCPMODE";
		} else {
			outline = "PORT ";
			outline.append(QString::number(m_listenport));
		}
	}
	else if(readLine.startsWith("Send STATE"))
	{
		outline = "STATE ";
                if(m_enabled_presence)
                        outline.append(m_availstate);
                else
                        outline.append("unknown");
	}
	else if(readLine.startsWith("OK SESSIONID"))
	{
		readLine.remove(QChar('\r')).remove(QChar('\n'));
		QStringList sessionResp = readLine.split(" ");
		qDebug() << sessionResp;
		if(sessionResp.size() > 2)
			m_sessionid = sessionResp[2];
		if(sessionResp.size() > 3)
			m_dialcontext = sessionResp[3];
		if(sessionResp.size() > 4)
			m_capabilities = sessionResp[4];
		qDebug() << m_dialcontext << m_capabilities;
		m_version = -1;
		if(sessionResp.size() > 5)
			m_version = sessionResp[5].toInt();
		if(!m_tcpmode)
			m_loginsocket->close();
		if(m_version < REQUIRED_SERVER_VERSION) {
			m_loginsocket->close();
			stop();
                        QMessageBox::critical(NULL, tr("Critical error"),
                                              tr("Your server version is %1 which is too old.\n").arg(m_version) +
                                              tr("The required one is at least %1.").arg(REQUIRED_SERVER_VERSION));
			return;
		}
		setState(ELogged);
		// start the keepalive timer
		m_ka_timerid = startTimer(m_keepaliveinterval);
                if(m_is_a_switchboard) /* ask here because not ready when the widget builds up */
                        askCallerIds();
		return;
	}
	else
	{
		readLine.remove(QChar('\r')).remove(QChar('\n'));
		qDebug() << "Response from server not recognized, closing" << readLine;
		m_loginsocket->close();
		setState(ENotLogged);
		return;
	}
	qDebug() << "BaseEngine::processLoginDialog() : " << outline;
	outline.append("\r\n");
	m_loginsocket->write(outline.toAscii());
	m_loginsocket->flush();
}

/*!
 * This slot method is called when a pending connection is
 * waiting on the m_listenserver.
 * It processes the incoming data and create a popup to display it.
 */
void BaseEngine::handleProfilePush()
{
	qDebug() << "BaseEngine::handleProfilePush()";
	QTcpSocket * connection = m_listenserver->nextPendingConnection();
	connect( connection, SIGNAL(disconnected()),
	         connection, SLOT(deleteLater()));

	// signals sur la socket : connected() disconnected()
	// error() hostFound() stateChanged()
	// iodevice : readyRead() aboutToClose() bytesWritten()

	qDebug() << connection->peerAddress().toString() << connection->peerPort();

	// Get Data and Popup the profile if ok
	Popup * popup = new Popup(connection, m_sessionid);
	connect( popup, SIGNAL(destroyed(QObject *)),
	         this, SLOT(popupDestroyed(QObject *)) );
	connect( popup, SIGNAL(wantsToBeShown(Popup *)),
	         this, SLOT(profileToBeShown(Popup *)) );
}

void BaseEngine::popupDestroyed(QObject * obj)
{
	qDebug() << "BaseEngine::popupDestroyed()" << obj;
	//obj->dumpObjectTree();
}

void BaseEngine::profileToBeShown(Popup * popup)
{
	newProfile( popup );
}

/*!
 * Send a keep alive message to the login server.
 * The message is sent in a datagram through m_udpsocket
 */ 
void BaseEngine::keepLoginAlive()
{
	qDebug() << "BaseEngine::keepLoginAlive()";
	// got to disconnected state if more than xx keepalive messages
	// have been left without response.
	if(m_pendingkeepalivemsg > 1)
	{
		qDebug() << "m_pendingkeepalivemsg" << m_pendingkeepalivemsg << "=> 0";
		stopKeepAliveTimer();
		setState(ENotLogged);
		m_pendingkeepalivemsg = 0;
		startTryAgainTimer();
		return;
	}
	if(m_state == ELogged) {
		QString outline = "ALIVE ";
		outline.append(m_asterisk + "/" + m_protocol.toLower() + m_userid);
		outline.append(" SESSIONID ");
		outline.append(m_sessionid);
		outline.append(" STATE ");
                if(m_enabled_presence)
                        outline.append(m_availstate);
                else
                        outline.append("unknown");
		qDebug() << "BaseEngine::keepLoginAlive() : " << outline;
		outline.append("\r\n");
		m_udpsocket->writeDatagram( outline.toAscii(),
					    m_serveraddress, m_loginport + 1 );
		m_pendingkeepalivemsg++;
		// if the last keepalive msg has not been answered, send this one
		// twice
		if(m_pendingkeepalivemsg > 1) {
                        m_udpsocket->writeDatagram( outline.toAscii(),
                                                    m_serveraddress, m_loginport + 1 );
                        m_pendingkeepalivemsg++;
                }
	}
}

/*!
 * Send a keep alive message to the login server.
 * The message is sent in a datagram through m_udpsocket
 */ 
void BaseEngine::sendMessage(const QString & txt)
{
	sendCommand("message " + txt);
}
