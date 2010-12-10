package com.proformatique.android.xivoclient;

import com.proformatique.android.xivoclient.tools.Constants;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.NetworkInfo.State;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

public class LoginActivity extends Activity {
	
    /**
     * Creating distinct preferences to avoid multiple references 
     * of the same data (login/password) in settings screen
     */
	private SharedPreferences settings;
    private SharedPreferences loginSettings;
	
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.login);
        
        settings = PreferenceManager.getDefaultSharedPreferences(this);
        loginSettings = this.getSharedPreferences("login_settings", 0);
        
        /**
         * Set the default saved login/password into corresponding fields 
         * if parameter "save_login" is on
         */
        if (settings.getBoolean("save_login", true)){
        	
        	String login = loginSettings.getString("login","");
        	String password = loginSettings.getString("password","");
        	
        	EditText eLogin = (EditText) findViewById(R.id.login);
        	eLogin.setText(login);

        	EditText ePassword = (EditText) findViewById(R.id.password);
        	ePassword.setText(password);
        }
    }
    
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.menu_settings, menu);
    	MenuItem mi = menu.findItem(R.id.menu_disconnect);
        if (Connection.connection != null) 
        	if (Connection.connection.connected) mi.setVisible(true);
        	else mi.setVisible(false);
        else mi.setVisible(false);

        return true;
    }
    
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle item selection
        switch (item.getItemId()) {
        case R.id.menu_settings:
            menuSettings();
            return true;
        case R.id.menu_exit:
            menuExit();
            return true;
        case R.id.menu_about:
            menuAbout();
            return true;
        case R.id.menu_disconnect:
        	Connection.connection.disconnect();
            return true;
        default:
            return super.onOptionsItemSelected(item);
        }
    }

	private void menuAbout() {
		Intent defineIntent = new Intent(this, AboutActivity.class);
		startActivity(defineIntent);
	}

	private void menuExit() {
		finish();
	}

	private void menuSettings() {
		Intent defineIntent = new Intent(this, SettingsActivity.class);
		startActivity(defineIntent);
		
	}
	
    public void clickOnButtonOk(View v) {
    	new ConnectTask().execute();
    }

	private void saveLoginPassword() {
        
		String savedLogin = loginSettings.getString("login","");
		String savedPassword = loginSettings.getString("password","");
        
        SharedPreferences.Editor editor = loginSettings.edit();

        EditText eLogin = (EditText) findViewById(R.id.login);
    	EditText ePassword = (EditText) findViewById(R.id.password);

        if (! eLogin.getText().toString().equals(savedLogin)){
            editor.putString("login", eLogin.getText().toString());
            editor.commit();
            }

        if (! ePassword.getText().toString().equals(savedPassword)){
            editor.putString("password", ePassword.getText().toString());
            editor.commit();
            }

	}
	
	/**
	 * Creating a AsyncTask to execute connection process
	 * @author cquaquin
	 */
	 private class ConnectTask extends AsyncTask<Void, Integer, Integer> {
		 ProgressDialog dialog;
		    @Override
		    protected void onPreExecute() {
		        dialog = new ProgressDialog(LoginActivity.this);
		        dialog.setMessage(getString(R.string.loading));
		        dialog.setIndeterminate(true);
		        dialog.setCancelable(false);
		        dialog.show();
		    }

		    @Override
			protected Integer doInBackground(Void... params) {
		    	EditText eLogin = (EditText) LoginActivity.this.findViewById(R.id.login); 
		    	EditText ePassword = (EditText) LoginActivity.this.findViewById(R.id.password); 
		    	
				/**
				 * Checking that web connection exists
				 */
		        ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
		        NetworkInfo netInfo = cm.getActiveNetworkInfo();

		        if (netInfo.getState().compareTo(State.CONNECTED)==0) {
		    	
			    	Connection connection = new Connection(eLogin.getText().toString(),
							ePassword.getText().toString(), LoginActivity.this);
					
			    	InitialListLoader initList = new InitialListLoader();
					int connectionCode = connection.initialize();
					
					if (connectionCode >= 1){
						return initList.startLoading();
					}
					return connectionCode;
		        }
		        else return Constants.NO_NETWORK_AVAILABLE;
			}

			protected void onPostExecute(Integer result) {
	         
	            if (result == Constants.NO_NETWORK_AVAILABLE){
		            dialog.dismiss();
	            	Toast.makeText(LoginActivity.this, R.string.no_web_connection
							, Toast.LENGTH_LONG).show();
	            }
	            else if (result < 1){
		            dialog.dismiss();

					Toast.makeText(LoginActivity.this, R.string.connection_failed
							, Toast.LENGTH_LONG).show();
				}
				else{
					
					if (Connection.connection.saveLogin){
						saveLoginPassword();
					}
		
			    	EditText eLogin = (EditText) LoginActivity.this.findViewById(R.id.login); 
			    	EditText ePassword = (EditText) LoginActivity.this.findViewById(R.id.password);
			    	TextView eLoginV = (TextView) LoginActivity.this.findViewById(R.id.login_text); 
			    	TextView ePasswordV = (TextView) LoginActivity.this.findViewById(R.id.password_text);
			    	Button eButton = (Button) LoginActivity.this.findViewById(R.id.b_ok);
			    	TextView eStatus = (TextView) LoginActivity.this.findViewById(R.id.connect_status); 
			    	
			    	eLogin.setVisibility(View.INVISIBLE);
			    	ePassword.setVisibility(View.INVISIBLE);
			    	eLoginV.setVisibility(View.INVISIBLE);
			    	ePasswordV.setVisibility(View.INVISIBLE);
			    	eButton.setVisibility(View.INVISIBLE);
			    	eStatus.setVisibility(View.VISIBLE);

			    	dialog.dismiss();
			    	
					/**
					 * Parsing and Displaying xlets content
					 */
					Intent defineIntent = new Intent(LoginActivity.this, XletsContainerTabActivity.class);
					startActivity(defineIntent);
				}
	         
			}
	 }

}