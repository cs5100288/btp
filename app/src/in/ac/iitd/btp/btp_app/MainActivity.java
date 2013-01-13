package in.ac.iitd.btp.btp_app;

import android.app.TabActivity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.TabHost;
import android.widget.TabHost.TabSpec;

public class MainActivity extends TabActivity {
	/** Called when the activity is first created. */
	TabHost tabHost;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		tabHost = getTabHost();
		// no need to call TabHost.Setup()

		// First Tab

		TabSpec spec0 = tabHost.newTabSpec("Tab 0");
		spec0.setIndicator("Blank");

		Intent in0 = new Intent(this, BlankActivity.class);
		spec0.setContent(in0);

		TabSpec spec1 = tabHost.newTabSpec("Tab 1");
		spec1.setIndicator("Wperf");
		// getResources().getDrawable(android.R.drawable.btn_star));
		Intent in1 = new Intent(this, WperfActivity.class);
		spec1.setContent(in1);

		TabSpec spec2 = tabHost.newTabSpec("Tab 2");
		spec2.setIndicator("Vperf");
		// getResources().getDrawable(android.R.drawable.btn_star));
		Intent in2 = new Intent(this, VperfActivity.class);
		spec2.setContent(in2);
		
		TabSpec spec3 = tabHost.newTabSpec("Tab 2");
		spec2.setIndicator("Hosts");
		// getResources().getDrawable(android.R.drawable.btn_star));
		Intent in3 = new Intent(this, HostsActivity.class);
		spec2.setContent(in3);
		
		
		tabHost.addTab(spec0);
		tabHost.addTab(spec1);
		tabHost.addTab(spec2);
		tabHost.addTab(spec3);

	}

	public void switchTab(int tab) {
		tabHost.setCurrentTab(tab);
	}
}