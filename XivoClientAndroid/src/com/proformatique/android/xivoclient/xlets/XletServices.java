package com.proformatique.android.xivoclient.xlets;

import java.util.HashMap;

import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.CheckBox;

import com.proformatique.android.xivoclient.Connection;
import com.proformatique.android.xivoclient.InitialListLoader;
import com.proformatique.android.xivoclient.R;
import com.proformatique.android.xivoclient.tools.Constants;

public class XletServices extends Activity{

	private static final String LOG_TAG = "XLET SERVICES";
	private IncomingReceiver receiver;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		setContentView(R.layout.xlet_services);
		refreshFeatures();

		receiver = new IncomingReceiver();

		/**
		 *  Register a BroadcastReceiver for Intent action that trigger a change
		 *  in the list from the Activity
		 */
        IntentFilter filter = new IntentFilter();
        filter.addAction(Constants.ACTION_LOAD_FEATURES);
        registerReceiver(receiver, new IntentFilter(filter));
	}
	
	public void clickOnCallrecord(View v){
		CheckBox checkbox = (CheckBox)v;
		if (checkbox.isChecked()){
			sendFeaturePut("callrecord", "1", null);
		}
		else {
			sendFeaturePut("callrecord", "0", null);
		}
	}
	
	public void clickOnIncallfilter(View v){
		CheckBox checkbox = (CheckBox)v;
		if (checkbox.isChecked()){
			sendFeaturePut("incallfilter", "1", null);
		}
		else {
			sendFeaturePut("incallfilter", "0", null);
		}
	}

	public void clickOnEnablednd(View v){
		CheckBox checkbox = (CheckBox)v;
		if (checkbox.isChecked()){
			sendFeaturePut("enablednd", "1", null);
		}
		else {
			sendFeaturePut("enablednd", "0", null);
		}
	}

	public void clickOnFwdrna(View v){
		CheckBox checkbox = (CheckBox)v;
		if (checkbox.isChecked()){
			checkbox.setClickable(false);
			Intent defineIntent = new Intent(this, XletServicesAsk.class);
			defineIntent.putExtra("serviceType", "fwdrna");
			startActivityForResult(defineIntent, Constants.CODE_SERVICE_ASK1);
		}
		else {
			checkbox.setText(R.string.servicesFwdrna);
			sendFeaturePut("enablerna", "0", 
					InitialListLoader.getInstance().getFeaturesRna().get("number"));
		}
	}
	
	public void clickOnFwdbusy(View v){
		CheckBox checkbox = (CheckBox)v;
		if (checkbox.isChecked()){
			checkbox.setClickable(false);
			Intent defineIntent = new Intent(this, XletServicesAsk.class);
			defineIntent.putExtra("serviceType", "fwdbusy");
			startActivityForResult(defineIntent, Constants.CODE_SERVICE_ASK2);
		}
		else {
			checkbox.setText(R.string.servicesFwdbusy);
			sendFeaturePut("enablebusy", "0", 
					InitialListLoader.getInstance().getFeaturesBusy().get("number"));

		}
		
	}

	public void clickOnFwdunc(View v){
		CheckBox checkbox = (CheckBox)v;
		if (checkbox.isChecked()){
			checkbox.setClickable(false);
			Intent defineIntent = new Intent(this, XletServicesAsk.class);
			defineIntent.putExtra("serviceType", "fwdunc");
			startActivityForResult(defineIntent, Constants.CODE_SERVICE_ASK3);
		}
		else {
			checkbox.setText(R.string.servicesFwdunc);
			sendFeaturePut("enableunc", "0", 
					InitialListLoader.getInstance().getFeaturesUnc().get("number"));
		}
	}
	
	 @Override
	 protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		 super.onActivityResult(requestCode, resultCode, data);
		 
		 CheckBox checkbox;
		 String textDisplay;
		 String phoneNumber = data.getStringExtra("phoneNumber");

		 if (requestCode == Constants.CODE_SERVICE_ASK1) {
			 checkbox = (CheckBox) findViewById(R.id.fwdrna);
			 textDisplay = getString(R.string.servicesFwdrna);
			 setCheckboxDisplay(resultCode, checkbox, phoneNumber, textDisplay);
			 if (resultCode  == Constants.OK)
				 sendFeaturePut("enablerna", "1", phoneNumber);
		 }

		 else if (requestCode == Constants.CODE_SERVICE_ASK2) {
			 checkbox = (CheckBox) findViewById(R.id.fwdbusy);
			 textDisplay = getString(R.string.servicesFwdbusy);
			 setCheckboxDisplay(resultCode, checkbox, phoneNumber, textDisplay);
			 if (resultCode  == Constants.OK)
				 sendFeaturePut("enablebusy", "1", phoneNumber);
		 }

		 if (requestCode == Constants.CODE_SERVICE_ASK3) {
			 checkbox = (CheckBox) findViewById(R.id.fwdunc);
			 textDisplay = getString(R.string.servicesFwdunc);
			 setCheckboxDisplay(resultCode, checkbox, phoneNumber, textDisplay);
			 if (resultCode  == Constants.OK)
				 sendFeaturePut("enableunc", "1", phoneNumber);
		 }

	 }
	 
	 private void setCheckboxDisplay(int code, CheckBox checkbox, 
			 String phoneNumber, String textDisplay){
		 if (code == Constants.OK){
			 checkbox.setText(textDisplay + "\n"+getString(R.string.servicesPhone)+phoneNumber);
			 checkbox.setChecked(true);
		 } else {
			 checkbox.setChecked(false);
			 checkbox.setText(textDisplay);
		 }
		checkbox.setClickable(true);

	 }
	 
		/**
		 * BroadcastReceiver, intercept Intents with action ACTION_LOAD_HISTORY_LIST
		 * to perform an reload of the displayed list
		 * @author cquaquin
		 *
		 */
		private class IncomingReceiver extends BroadcastReceiver {

			@Override
			public void onReceive(Context context, Intent intent) {
		        if (intent.getAction().equals(Constants.ACTION_LOAD_FEATURES)) {
		        	Log.d( LOG_TAG , "Received Broadcast "+Constants.ACTION_LOAD_FEATURES);
		        	refreshFeatures();
		        }
			}
		}


		public void refreshFeatures() {
			HashMap<String, String> featureMap;
			CheckBox checkbox;
			int code=0;
			
			featureMap = InitialListLoader.getInstance().getFeaturesBusy();
			if (featureMap.containsKey("enabled")){
				checkbox = (CheckBox) findViewById(R.id.fwdbusy);
				if (featureMap.get("enabled").equals("true")) code = Constants.OK;
				else code = Constants.CANCEL;
				setCheckboxDisplay(code, checkbox, featureMap.get("number"), 
						getString(R.string.servicesFwdbusy));
			}
			
			featureMap = InitialListLoader.getInstance().getFeaturesRna();
			if (featureMap.containsKey("enabled")){
				checkbox = (CheckBox) findViewById(R.id.fwdrna);
				if (featureMap.get("enabled").equals("true")) code = Constants.OK;
				else code = Constants.CANCEL;
				setCheckboxDisplay(code, checkbox, featureMap.get("number"), 
						getString(R.string.servicesFwdrna));
			}
			
			featureMap = InitialListLoader.getInstance().getFeaturesUnc();
			if (featureMap.containsKey("enabled")){
				checkbox = (CheckBox) findViewById(R.id.fwdunc);
				if (featureMap.get("enabled").equals("true")) code = Constants.OK;
				else code = Constants.CANCEL;
				setCheckboxDisplay(code, checkbox, featureMap.get("number"), 
						getString(R.string.servicesFwdunc));
			}

			featureMap = InitialListLoader.getInstance().getFeaturesEnablednd();
			if (featureMap.containsKey("enabled")){
				checkbox = (CheckBox) findViewById(R.id.enablednd);
				if (featureMap.get("enabled").equals("true")) checkbox.setChecked(true);
				else checkbox.setChecked(false);
			}

			featureMap = InitialListLoader.getInstance().getFeaturesCallrecord();
			if (featureMap.containsKey("enabled")){
				checkbox = (CheckBox) findViewById(R.id.callrecord);
				if (featureMap.get("enabled").equals("true")) checkbox.setChecked(true);
				else checkbox.setChecked(false);
			}

			featureMap = InitialListLoader.getInstance().getFeaturesIncallfilter();
			if (featureMap.containsKey("enabled")){
				checkbox = (CheckBox) findViewById(R.id.incallfilter);
				if (featureMap.get("enabled").equals("true")) checkbox.setChecked(true);
				else checkbox.setChecked(false);
			}
		}

		private JSONObject createJsonFeaturePut(String feature, String value, String phone) {
			JSONObject jObj = new JSONObject();
			try {
				jObj.accumulate("direction", Constants.XIVO_SERVER);
				jObj.accumulate("class", "featuresput");
				jObj.accumulate("userid", InitialListLoader.getInstance().getUserId());
				jObj.accumulate("function", feature);
				jObj.accumulate("value", value);
				if (phone != null) jObj.accumulate("destination", phone);
				
				return jObj;
			} catch (JSONException e) {
				return null;
			}

		}

		private void sendFeaturePut(String feature, String value, String phone){
			JSONObject jObj = createJsonFeaturePut(feature, value, phone);
			Connection.getInstance().sendJsonString(jObj);
		}

		@Override
		protected void onDestroy() {
			unregisterReceiver(receiver);
			super.onDestroy();
		}


}
