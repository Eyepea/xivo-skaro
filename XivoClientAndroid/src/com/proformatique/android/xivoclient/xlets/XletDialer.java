package com.proformatique.android.xivoclient.xlets;

import java.io.IOException;
import java.io.PrintStream;

import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.app.Dialog;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.proformatique.android.xivoclient.Connection;
import com.proformatique.android.xivoclient.R;
import com.proformatique.android.xivoclient.XletsContainerTabActivity;
import com.proformatique.android.xivoclient.tools.Constants;

public class XletDialer extends Activity{

	private static final String LOG_TAG = "XLET DIALER";
	EditText phoneNumber;
	IncomingReceiver receiver;
	Dialog dialog;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		setContentView(R.layout.xlet_dialer);
		phoneNumber = (EditText) findViewById(R.id.number);

		receiver = new IncomingReceiver();

		/**
		 *  Register a BroadcastReceiver for Intent action that trigger a call
		 */
        IntentFilter filter = new IntentFilter();
        filter.addAction(Constants.ACTION_XLET_DIAL_CALL);
        registerReceiver(receiver, new IntentFilter(filter));

	}
	
	public void clickOnCall(View v) {
		if (!("").equals(phoneNumber.getText().toString())){
			new CallJsonTask().execute();
		}
    }
    
	/**
	 * Creating a AsyncTask to run call process
	 * @author cquaquin
	 */
	 private class CallJsonTask extends AsyncTask<Void, Integer, Integer> {

		@Override
		protected void onPreExecute() {
			
			phoneNumber.setEnabled(false);
			Context mContext = getApplicationContext();
			dialog = new Dialog(XletDialer.this);

			dialog.setContentView(R.layout.xlet_dialer_call);
			dialog.setTitle(R.string.calling_title);

			TextView text = (TextView) dialog.findViewById(R.id.call_message);
			text.setText(getString(R.string.calling, phoneNumber.getText().toString()));
			
			dialog.show();

			super.onPreExecute();
		}

		@Override
		protected Integer doInBackground(Void... params) {

			timer(1000);

	    	/**
	    	 * If the user enabled "use_mobile_number" setting, the call takes
	    	 * the mobile number for source phone. 
	    	 */
	    	String mobileNumber = "";
	    	Boolean useMobile;
	    	SharedPreferences settings = PreferenceManager.getDefaultSharedPreferences(XletDialer.this);
	       	useMobile = settings.getBoolean("use_mobile_number",false);
	       	
	       	if (useMobile) 
	       		mobileNumber = settings.getString("mobile_number","");
	    	
	    	/**
	    	 * Creating Call Json object
	    	 */
	    	JSONObject jCalling = createJsonCallingObject("originate", mobileNumber, 
	    			phoneNumber.getText().toString());
			try {
				Log.d( LOG_TAG, "jCalling: " + jCalling.toString());
				PrintStream output = new PrintStream(Connection.getInstance().getNetworkConnection().getOutputStream());
				output.println(jCalling.toString());
				
				publishProgress(Constants.OK);
				timer(3000);
				
				return Constants.OK; 
				
			} catch (IOException e) {
				publishProgress(Constants.NO_NETWORK_AVAILABLE);
				
				return Constants.NO_NETWORK_AVAILABLE;
			}
	    	
		}
		
		private void timer(int milliseconds){
			try {
				synchronized(this) {
					this.wait(milliseconds);
					} 
				} catch (InterruptedException e) {
				e.printStackTrace();
			}

		}
		
		@Override
		protected void onProgressUpdate(Integer... values) {
			if (values[0]==Constants.OK) {
				TextView text = (TextView) dialog.findViewById(R.id.call_message);
				text.setText(getString(R.string.call_ok));
			}
			else {
				TextView text = (TextView) dialog.findViewById(R.id.call_message);
				text.setText(getString(R.string.no_web_connection));
			}
			super.onProgressUpdate(values);
		}

		@Override
		protected void onPostExecute(Integer result) {
			phoneNumber.setEnabled(true);
			dialog.dismiss();

		}

	 }
    
	 /**
	  * Prepare the Json string for calling process
	  * 
	  * @param inputClass
	  * @param phoneNumberSrc
	  * @param phoneNumberDest
	  * @return
	  */
	private JSONObject createJsonCallingObject(String inputClass, 
			String phoneNumberSrc,
			String phoneNumberDest) {
		
		JSONObject jObj = new JSONObject();
		String phoneSrc;
		
		if (phoneNumberSrc == null)
			phoneSrc = "user:special:me";
		else if (phoneNumberSrc.equals(""))
			phoneSrc = "user:special:me";
		else phoneSrc = "ext:"+phoneNumberSrc;
		
		try {
			jObj.accumulate("direction", Constants.XIVO_SERVER);
			jObj.accumulate("class",inputClass);
			jObj.accumulate("source", phoneSrc);
			jObj.accumulate("destination", "ext:"+phoneNumberDest);
			
			return jObj;
		} catch (JSONException e) {
			return null;
		}
	}

	/**
	 * BroadcastReceiver, intercept Intents with action ACTION_XLET_DIAL_CALL
	 * to perform a call
	 * @author cquaquin
	 *
	 */
	public class IncomingReceiver extends BroadcastReceiver {

		@Override
		public void onReceive(Context context, Intent intent) {
	        if (intent.getAction().equals(Constants.ACTION_XLET_DIAL_CALL)) {
	        	Log.d( LOG_TAG , "Received Broadcast ");
				Bundle extra = intent.getExtras();
		
				if (extra != null){
					XletsContainerTabActivity parentAct;
					phoneNumber.setText(extra.getString("numToCall"));
					parentAct = (XletsContainerTabActivity)XletDialer.this.getParent();
					parentAct.switchTab(0);
					
					new CallJsonTask().execute();
				}

	        }
		}
	}

    public void clickOn1(View v) {
    	phoneNumber.append("1");
    }

    public void clickOn2(View v) {
    	phoneNumber.append("2");
    }
	
    public void clickOn3(View v) {
    	phoneNumber.append("3");
    }

    public void clickOn4(View v) {
    	phoneNumber.append("4");
    }

    public void clickOn5(View v) {
    	phoneNumber.append("5");
    }

    public void clickOn6(View v) {
    	phoneNumber.append("6");
    }

    public void clickOn7(View v) {
    	phoneNumber.append("7");
    }

    public void clickOn8(View v) {
    	phoneNumber.append("8");
    }

    public void clickOn9(View v) {
    	phoneNumber.append("9");
    }

    public void clickOn0(View v) {
    	phoneNumber.append("0");
    }

    public void clickOnStar(View v) {
    	phoneNumber.append("*");
    }

    public void clickOnSharp(View v) {
    	phoneNumber.append("#");
    }

    public void clickOnDelete(View v) {
    	keyPressed(KeyEvent.KEYCODE_DEL);
    }

    private void keyPressed(int keyCode) {
        KeyEvent event = new KeyEvent(KeyEvent.ACTION_DOWN, keyCode);
        phoneNumber.onKeyDown(keyCode, event);
    }

    
    protected void onDestroy() {
		unregisterReceiver(receiver);
		super.onDestroy();
	}

}
