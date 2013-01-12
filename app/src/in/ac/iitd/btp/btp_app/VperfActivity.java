package in.ac.iitd.btp.btp_app;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;

import android.app.Activity;
import android.os.Bundle;
import android.telephony.PhoneStateListener;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.RatingBar;
import android.widget.Toast;

public class VperfActivity extends Activity {
	WebView webView1;
	Button go;
	EditText et;
	ProgressBar pb;
	RatingBar ratingWidget;
	long pageLoadTime, pageLoadStartTime, pageLoadEndTime; // milliseconds
	float rating;
	int signal_strength = -10; // default value;
	boolean received_signal_strength = false;

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

	private class SignalStrengthListener extends PhoneStateListener {
		@Override
		public void onSignalStrengthsChanged(
				android.telephony.SignalStrength signalStrength) {

			// get the signal strength (a value between 0 and 31)
			if (!received_signal_strength) {
				int strengthAmplitude = signalStrength.getGsmSignalStrength();
				signal_strength = strengthAmplitude;
				Log.d("SignalStrengthListener", "signal strength: "
						+ signal_strength);
				proceed();
				received_signal_strength=true;
			}
			// do something with it (in this case we update a text view)
			super.onSignalStrengthsChanged(signalStrength);
		}

	}

	public final static String SERVER_BASE = "http://agni.iitd.ac.in:8000";
	SignalStrengthListener signalStrengthListener;

	void proceed() {
		Runnable r = new Runnable() {
			public void run() {
				String phoneConf = connect(SERVER_BASE
						+ "/vperf/addphoneconf?signal_strength="
						+ signal_strength);
				webView1.loadUrl(SERVER_BASE + "/vperf/rate?phoneConf="
						+ phoneConf.trim());
			};
		};
		new Thread(r).start();

	}

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		signalStrengthListener = new SignalStrengthListener();
		((TelephonyManager) getSystemService(TELEPHONY_SERVICE)).listen(
				signalStrengthListener,
				SignalStrengthListener.LISTEN_SIGNAL_STRENGTHS);
		setContentView(R.layout.activity_vperf);
		webView1 = (WebView) findViewById(R.id.webView1);
		go = (Button) findViewById(R.id.button1);
		et = (EditText) findViewById(R.id.editText1);
		pb = (ProgressBar) findViewById(R.id.progressBar1);
		ratingWidget = (RatingBar) findViewById(R.id.ratingBar1);
		go.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// TODO Auto-generated method stub
				pageLoadStartTime = System.currentTimeMillis();
				webView1.loadUrl(et.getText().toString());
			}
		});
		webView1.setWebViewClient(new WebViewClient() {
			@Override
			public boolean shouldOverrideUrlLoading(WebView view, String url) {
				// TODO Auto-generated method stub
				et.setText(url);
				view.loadUrl(url);
				return true;
			}
		});
		webView1.getSettings().setJavaScriptEnabled(true);
		webView1.getSettings().setPluginState(WebSettings.PluginState.ON);
		webView1.setWebChromeClient(new WebChromeClient() {
			@Override
			public void onProgressChanged(WebView view, int progress) {
				// TODO Auto-generated method stub
				if (progress < 100 && pb.getVisibility() == ProgressBar.GONE) {
					pb.setVisibility(ProgressBar.VISIBLE);
				}
				pb.setProgress(progress);
				if (progress == 100) {
					pageLoadEndTime = System.currentTimeMillis();
					pageLoadTime = pageLoadEndTime - pageLoadStartTime;
					// Toast.makeText(VperfActivity.this, "LoadTime: " +
					// pageLoadTime + " ms", Toast.LENGTH_SHORT).show();
					pb.setVisibility(ProgressBar.GONE);

				}
			}
		});
		webView1.addJavascriptInterface(new JavascriptInterface(this),
				"Android");
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}
}
