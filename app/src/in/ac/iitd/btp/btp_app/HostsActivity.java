package in.ac.iitd.btp.btp_app;

import com.stericson.RootTools.RootTools;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;


public class HostsActivity extends Activity{

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);
		if(!RootTools.isAccessGiven())
		{
			TextView tv = new TextView(this);
			tv.setText("Root access not given. Please ensure root access.");
			setContentView(tv);
		}
		setContentView(R.layout.activity_hosts);
	}
	
}
