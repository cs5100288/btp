package in.ac.iitd.btp.btp_app;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;

import android.app.Activity;
import android.os.Bundle;
import android.os.Environment;
import android.os.StrictMode;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;

import com.stericson.RootTools.Command;
import com.stericson.RootTools.RootTools;

public class HostsActivity extends Activity {

	Button btn_update;
	TextView tv_status, tv_hosts;

	public static String connect(String url) {
		String ret = "";

		HttpClient httpclient = new DefaultHttpClient();

		// Prepare a request object
		HttpGet httpget = new HttpGet(url);

		// Execute the request
		HttpResponse response;
		try {
			response = httpclient.execute(httpget);
			// Examine the response status

			// Get hold of the response entity
			HttpEntity entity = response.getEntity();
			// If the response does not enclose an entity, there is no need
			// to worry about connection release

			if (entity != null) {

				// A Simple JSON Response Read
				InputStream instream = entity.getContent();
				String result = convertStreamToString(instream);
				// now you have the string representation of the HTML request
				instream.close();
				ret = result;
			}

		} catch (Exception e) {
			e.printStackTrace();
		}
		return ret;
	}

	private static String convertStreamToString(InputStream is) {
		/*
		 * To convert the InputStream to String we use the
		 * BufferedReader.readLine() method. We iterate until the BufferedReader
		 * return null which means there's no more data to read. Each line will
		 * appended to a StringBuilder and returned as String.
		 */
		BufferedReader reader = new BufferedReader(new InputStreamReader(is));
		StringBuilder sb = new StringBuilder();

		String line = null;
		try {
			while ((line = reader.readLine()) != null) {
				sb.append(line + "\n");
			}
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				is.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return sb.toString();
	}

	String write_file(String filename, String data) {
		try {
			// catches IOException below

			/*
			 * We have to use the openFileOutput()-method the ActivityContext
			 * provides, to protect your file from others and This is done for
			 * security-reasons. We chose MODE_WORLD_READABLE, because we have
			 * nothing to hide in our file
			 */

			File sdCard = Environment.getExternalStorageDirectory();
			File f = new File(sdCard, "hosts");
			FileOutputStream fOut = new FileOutputStream(f);
			OutputStreamWriter osw = new OutputStreamWriter(fOut);

			// Write the string to the file
			osw.write(data);

			/*
			 * ensure that everything is really written out and close
			 */
			osw.flush();
			osw.close();
			return f.getAbsolutePath();

		} catch (IOException ioe) {
			ioe.printStackTrace();
		}
		return "";
	}

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);
		StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder()
				.permitAll().build();
		StrictMode.setThreadPolicy(policy);
		if (!RootTools.isAccessGiven()) {
			TextView tv = new TextView(this);
			tv.setText("Root access not given. Please ensure root access.");
			setContentView(tv);
		}
		if (!RootTools.isBusyboxAvailable())
			RootTools.offerBusyBox(this);
		setContentView(R.layout.activity_hosts);
		btn_update = (Button) findViewById(R.id.btn_update);
		tv_status = (TextView) findViewById(R.id.tv_status);
		tv_hosts = (TextView) findViewById(R.id.tv_hosts);
		btn_update.setOnClickListener(new OnClickListener() {

			public void onClick(View v) {
				// TODO Auto-generated method stub
				String hostsData = connect("http://agni.iitd.ac.in:8000/wperf/hosts/file");
				try {
					String fn = write_file("hosts", hostsData);
					RootTools.remount("/system/", "rw");
					RootTools.getShell(true)
							.add(new Command(0, "cp " + fn + " /etc/hosts") {
								@Override
								public void output(int arg0, String arg1) {
									// TODO Auto-generated method stub
									Log.e("HostsActivity", arg1);
								}
							}).waitForFinish();
					 RootTools.remount("/system/", "ro");
					tv_status.setText("Done");

				} catch (Exception ioe) {
					Log.e("HostsActivity", ioe.toString());
					tv_status.setText(ioe.toString());
				}

			}
		});
	}

}
