package com.proformatique.android.xivoclient;

import com.proformatique.android.xivoclient.tools.Constants;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.net.Socket;
import java.net.UnknownHostException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import org.json.JSONException;
import org.json.JSONObject;
import android.app.Activity;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Class of Connection and authentication on Xivo CTI server
 * 
 * @author cquaquin
 *
 */
public class Connection {

	private static final String LOG_TAG = "CONNECTION";
	String serverAdress;
	int serverPort;
	String login;
	String password;
	Boolean saveLogin;
	Activity callingActivity;
	SharedPreferences settings;
	DataInputStream input;
	String responseLine;
	String sessionId;
	JSONObject jCapa;
	public static Connection connection;
	public Socket networkConnection;
	boolean connected = false;
	
	public Connection(String login, String password,
			Activity callingActivity) {
		super();
		this.login = login;
		this.password = password;
		this.callingActivity = callingActivity;
		this.settings = PreferenceManager.getDefaultSharedPreferences(callingActivity);
		this.serverAdress = this.settings.getString("server_adress", "");
		this.serverPort = Integer.parseInt(this.settings.getString("server_port", "5003"));
		this.saveLogin = this.settings.getBoolean("save_login", true);
		
		connection = this;

	}

	/**
	 * Perform network connection with Xivo CTI server
	 * 
	 * @return error code
	 */
	public int initialize() {
		
			try {
				networkConnection = new Socket(serverAdress, serverPort);
	
				input = new DataInputStream(networkConnection.getInputStream());
	            String responseLine;
	            
				while ((responseLine = input.readLine()) != null) {
	
	                   if (responseLine.contains("XiVO CTI Server")) {
	                	   return loginCTI();
	                   }
	               }
				return Constants.NOT_CTI_SERVER;
				
			} catch (UnknownHostException e) {
				return Constants.BAD_HOST;
			} catch (IOException e) {
				return Constants.NO_NETWORK_AVAILABLE;
			}
		
	}
	
	/**
	 * Perform authentication by Json array on Xivo CTI server
	 * 
	 * @return error or success code
	 */
	private int loginCTI(){
		
		JSONObject ReadLineObject;
		
		/**
		 * Creating first Json login array
		 */
		JSONObject jLogin = new JSONObject();
		try {
			jLogin.accumulate("class","login_id");
			jLogin.accumulate("company", Constants.XIVO_CONTEXT);
			jLogin.accumulate("ident","undef@X11-LE");
			jLogin.accumulate("userid",login);
			jLogin.accumulate("version",Constants.XIVO_LOGIN_VERSION);
			jLogin.accumulate("xivoversion",Constants.XIVO_VERSION);
			
		} catch (JSONException e) {
			return Constants.JSON_POPULATE_ERROR;
		}
		
		/**
		 * First step : check that login is allowed on server
		 */
		try {
			Log.d( LOG_TAG, "Client: " + jLogin.toString());
			PrintStream output = new PrintStream(networkConnection.getOutputStream());
			output.println(jLogin.toString());
		} catch (IOException e) {
			return Constants.NO_NETWORK_AVAILABLE;
		}
		
		ReadLineObject = readJsonObjectCTI();
		
		try {
		    if (ReadLineObject.getString("class").equals(Constants.XIVO_LOGIN_OK)){

				/**
				 * Second step : check that password is allowed on server
				 */
				int codePassword = passwordCTI(ReadLineObject);
				
				/**
				 * Third step : send configuration options on server
				 */
				if (codePassword > 0) {
					ReadLineObject = readJsonObjectCTI();
					if (ReadLineObject.getString("class").equals(Constants.XIVO_PASSWORD_OK))
					{
						int codeCapas = capasCTI();
						if (codeCapas > 0) {
							ReadLineObject = readJsonObjectCTI();
							
							if (ReadLineObject.getString("class").equals(Constants.XIVO_LOGIN_CAPAS_OK)){
								jCapa = ReadLineObject;
								Log.d( LOG_TAG, "jCapa length : " + jCapa.length());
								InitialListLoader.initialListLoader.xivoId = jCapa.getString("xivo_userid");
								
								connected=true;
								return Constants.CONNECTION_OK;
							}
						}
					}
				}
			}
		    
		} catch (JSONException e) {
			e.printStackTrace();
		}
		
		try {
			networkConnection.close();
		} catch (IOException e) {
		}
		return Constants.LOGIN_KO;
	}

	/**
	 * Perform a read action on the stream from CTI server
	 * @return JSON object retrieved
	 */
	public JSONObject readJsonObjectCTI() {
		JSONObject ReadLineObject;
		
		try {
			while ((responseLine = input.readLine()) != null) {
				try {
					ReadLineObject = new JSONObject(responseLine);
					Log.d( LOG_TAG, "Server: " + responseLine);
					
					return ReadLineObject;
				}
				catch (Exception e) {
					e.printStackTrace();

				}
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return null;

	}

	private int passwordCTI(JSONObject jsonSessionRead) throws JSONException {
		byte[] sDigest = null;
		sessionId = jsonSessionRead.getString("sessionid");
		JSONObject jsonPasswordAuthent = new JSONObject();
		
		/**
		 * Encrypt password for communication with algorithm SHA1
		 */
		MessageDigest sha1;
		try {
			sha1 = MessageDigest.getInstance("SHA1");
			sDigest = sha1.digest((sessionId+":"+password).getBytes());
		} catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
		
		jsonPasswordAuthent.accumulate("class", "login_pass");
		jsonPasswordAuthent.accumulate("hashedpassword", bytes2String(sDigest));
		PrintStream output;
		try {
			output = new PrintStream(networkConnection.getOutputStream());
			output.println(jsonPasswordAuthent.toString());
		} catch (IOException e) {
			return Constants.NO_NETWORK_AVAILABLE;
		}

		return Constants.CONNECTION_OK;
	}

	private int capasCTI() throws JSONException {
		JSONObject jsonCapas = new JSONObject();
		
		jsonCapas.accumulate("class", "login_capas");
		jsonCapas.accumulate("agentlogin", "now");
		jsonCapas.accumulate("capaid", "client");
		jsonCapas.accumulate("lastconnwins", "false");
		jsonCapas.accumulate("loginkind", "agent");
		jsonCapas.accumulate("phonenumber", "101");
		jsonCapas.accumulate("state", "");
		
		PrintStream output;
		try {
			output = new PrintStream(networkConnection.getOutputStream());
			output.println(jsonCapas.toString());
		} catch (IOException e) {
			return Constants.NO_NETWORK_AVAILABLE;
		}

		return Constants.CONNECTION_OK;
	}


	private static String bytes2String(byte[] bytes) {
        StringBuilder string = new StringBuilder();
        for (byte b: bytes) {
                String hexString = Integer.toHexString(0x00FF & b);
                string.append(hexString.length() == 1 ? "0" + hexString : hexString);
        }
        return string.toString();
	}

	/**
	 * Perform a read action on the stream from CTI server
	 * And return the object corresponding at input parameter ctiClass 
	 * @return JSON object retrieved
	 */
	public JSONObject readJsonObjectCTI(String ctiClass) {
		JSONObject ReadLineObject;
		
		try {
			while ((responseLine = input.readLine()) != null) {
				try {
					ReadLineObject = new JSONObject(responseLine);
					Log.d( LOG_TAG, "Server: " + responseLine);
					
					if (ReadLineObject.get("class").equals(ctiClass))
					   return ReadLineObject;
				}
				catch (Exception e) {
					e.printStackTrace();

				}
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return null;

	}
	
	JSONObject readData() throws IOException, JSONException{

		if (networkConnection.isClosed()){
			disconnect();
			return null;
		}
		
		while (networkConnection.isConnected()) {
			responseLine = input.readLine();
			Log.d( LOG_TAG, "Server from ReadData: " + responseLine);
            JSONObject jsonString = new JSONObject(responseLine);
			return jsonString;
		}

		return null;
		
	}

	public int disconnect(){
		
		try {
			JsonLoopListener.cancel = true;
			connected = false;
			networkConnection.close();
			
	    	EditText eLogin = (EditText) callingActivity.findViewById(R.id.login); 
	    	EditText ePassword = (EditText) callingActivity.findViewById(R.id.password);
	    	TextView eLoginV = (TextView) callingActivity.findViewById(R.id.login_text); 
	    	TextView ePasswordV = (TextView) callingActivity.findViewById(R.id.password_text);
	    	Button eButton = (Button) callingActivity.findViewById(R.id.b_ok);
	    	TextView eStatus = (TextView) callingActivity.findViewById(R.id.connect_status); 
	    	
	    	eLogin.setVisibility(View.VISIBLE);
	    	ePassword.setVisibility(View.VISIBLE);
	    	eLoginV.setVisibility(View.VISIBLE);
	    	ePasswordV.setVisibility(View.VISIBLE);
	    	eButton.setVisibility(View.VISIBLE);
	    	eStatus.setVisibility(View.INVISIBLE);
			
			
		} catch (IOException e) {
			e.printStackTrace();
			return Constants.NO_NETWORK_AVAILABLE;
		}
		return Constants.OK;
		
	}
	
}
