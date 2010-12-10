package com.proformatique.android.xivoclient.xlets;

import com.proformatique.android.xivoclient.InitialListLoader;
import com.proformatique.android.xivoclient.R;
import com.proformatique.android.xivoclient.tools.Constants;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;

public class XletServicesAsk extends Activity{

	private String serviceType;
	private EditText phoneView;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		setContentView(R.layout.xlet_services_ask);
		Intent intent = getIntent();
		serviceType = intent.getExtras().getString("serviceType");
		setTitle(R.string.ServicesFwdTitle);
		
		phoneView = (EditText)findViewById(R.id.servicesAskPhone);
		String phone = "";
		if (serviceType.equals("fwdrna")) 
			phone = InitialListLoader.getInstance().getFeaturesRna().get("number");
		else if (serviceType.equals("fwdbusy")) 
			phone = InitialListLoader.getInstance().getFeaturesBusy().get("number");
		if (serviceType.equals("fwdunc")) 
			phone = InitialListLoader.getInstance().getFeaturesUnc().get("number");

		phoneView.setText(phone);
	}
	
	public void clickOnCancel(View v){
		Intent intentCancel = new Intent();
		intentCancel.putExtra("phoneNumber", "");
		
		setResult(Constants.CANCEL, intentCancel);
		finish();
	}

	public void clickOnOk(View v){
		
		Intent intentOk = new Intent();
		intentOk.putExtra("phoneNumber", phoneView.getText().toString());
		setResult(Constants.OK, intentOk);
		finish();
	}

}
