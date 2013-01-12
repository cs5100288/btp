package in.ac.iitd.btp.btp_app;

import android.content.Context;
import android.widget.Toast;

public class JavascriptInterface {
    Context mContext;

    /** Instantiate the interface and set the context */
    JavascriptInterface(Context c) {
        mContext = c;
    }

    /** Show a toast from the web page */
    public void showToast(String toast) {
        Toast.makeText(mContext, toast, Toast.LENGTH_SHORT).show();
    }
}