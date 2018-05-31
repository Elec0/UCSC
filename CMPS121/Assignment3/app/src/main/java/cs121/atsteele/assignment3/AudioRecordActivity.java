package cs121.atsteele.assignment3;

import android.Manifest;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.provider.MediaStore;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;

import java.io.IOException;

public class AudioRecordActivity extends AppCompatActivity
{
    public static final int REQUEST_RECORD_AUDIO_PERMISSION = 113;
    private String FILE_LOC = "";

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_audio_record);

        // From https://stackoverflow.com/questions/10472839/using-javascript-in-android-webview
        WebView wv = findViewById(R.id.webAudio);
        wv.getSettings().setJavaScriptEnabled(true);
        // register class containing methods to be exposed to JavaScript
        AudioJavascriptInterface Android = new AudioJavascriptInterface(this);
        wv.addJavascriptInterface(Android, "Android");

        wv.loadUrl("https://users.soe.ucsc.edu/~dustinadams/CMPS121/assignment3/www/index.html");

        ActivityCompat.requestPermissions(this, permissions, REQUEST_RECORD_AUDIO_PERMISSION);
        FILE_LOC = getExternalCacheDir().getAbsolutePath() + "/";
    }

    // Requesting permission to RECORD_AUDIO
    private boolean permissionToRecordAccepted = false;
    private String [] permissions = {Manifest.permission.RECORD_AUDIO};

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode){
            case REQUEST_RECORD_AUDIO_PERMISSION:
                permissionToRecordAccepted  = grantResults[0] == PackageManager.PERMISSION_GRANTED;
                break;
        }
        if (!permissionToRecordAccepted )
            finish();

    }

    public class AudioJavascriptInterface {
        Context mContext;
        MediaRecorder mRecorder;
        MediaPlayer mPlayer;

        public AudioJavascriptInterface(Context c) {
            mContext = c;
        }

        @android.webkit.JavascriptInterface
        public void record() {
            SharedPreferences settings = getSharedPreferences(MainActivity.PREFS_NAME, 0);
            int numRecordings  = settings.getInt(MainActivity.PREFS_NUM_RECS, 0) + 1;

            SharedPreferences.Editor editor = settings.edit();
            editor.putInt(MainActivity.PREFS_NUM_RECS, numRecordings);
            editor.apply();
            String mFileName = FILE_LOC + "Audio" + numRecordings + ".3gp";

            mRecorder = new MediaRecorder();
            mRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
            mRecorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
            mRecorder.setOutputFile(mFileName);
            mRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB);

            try {
                mRecorder.prepare();
            } catch (IOException e) {  }

            mRecorder.start();
        }

        @android.webkit.JavascriptInterface
        public void stop() {
            mRecorder.stop();
            mRecorder.release();
            mRecorder = null;
        }

        @android.webkit.JavascriptInterface
        public void play() {
            mPlayer = new MediaPlayer();
            try {
                SharedPreferences settings = getSharedPreferences(MainActivity.PREFS_NAME, 0);
                int numRecordings  = settings.getInt(MainActivity.PREFS_NUM_RECS, 0);
                String mFileName = FILE_LOC + "Audio" + numRecordings + ".3gp";

                mPlayer.setDataSource(mFileName);
                mPlayer.prepare();
                mPlayer.start();

            } catch (IOException e) {  }
        }

        @android.webkit.JavascriptInterface
        public void stoprec() {
            mPlayer.release();
            mPlayer = null;
        }

        @android.webkit.JavascriptInterface
        public void exit() {
            finish();
        }
    }
}
