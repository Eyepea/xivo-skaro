package com.proformatique.android.xivoclient.xlets;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

import com.proformatique.android.xivoclient.InitialListLoader;
import com.proformatique.android.xivoclient.R;
import android.app.Activity;
import android.content.Context;
import android.view.View;
import android.widget.TextView;

public class XletIdentity implements XletInterface{

	public XletIdentity(Activity activity) {
		
		TextView userName = (TextView) activity.findViewById(R.id.user_identity);
		
		List<HashMap<String, String>> usersList = InitialListLoader.initialListLoader.usersList;
		String xivoId=InitialListLoader.initialListLoader.xivoId;

		for (HashMap<String, String> hashMap : usersList) {
			if (hashMap.get("xivo_userid").equals(xivoId)){
				userName.setText(hashMap.get("fullname")+" ("+hashMap.get("phonenum")+")");
				break;
			}
		}
		
		
		
	}

}
