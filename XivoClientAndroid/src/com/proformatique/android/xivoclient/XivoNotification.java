package com.proformatique.android.xivoclient;

import com.proformatique.android.xivoclient.tools.Constants;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;

public class XivoNotification {
	
	Context context;
	NotificationManager notifManager;
	Notification notification;
	int idRef = Constants.XIVO_NOTIF;

	public XivoNotification(Context context) {
		super();
		this.context = context;
	}

	public void createNotification(){
		notifManager = (NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);
		notification = new Notification(R.drawable.icon, "", System.currentTimeMillis());
		PendingIntent pendingIntent = PendingIntent.getActivity(context, 0, 
				new Intent(context, LoginActivity.class), PendingIntent.FLAG_UPDATE_CURRENT);
		notification.flags=Notification.FLAG_NO_CLEAR;
		
		/**
		 * Notification Title
		 */
		notification.setLatestEventInfo(context, context.getString(R.string.notif_xivo_title), 
				context.getString(R.string.notif_xivo), pendingIntent);
		notifManager.notify("XIVO", idRef, notification);
	}

	public void removeNotif() {
		notifManager.cancel("XIVO",idRef);
	}
}
