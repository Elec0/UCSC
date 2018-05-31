package cs121.atsteele.assignment3;

import android.content.Intent;
import android.content.SharedPreferences;
import android.media.MediaPlayer;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import java.io.IOException;

public class MainActivity extends AppCompatActivity
{
    public static final String PREFS_NAME = "Asn3Prefs";
    public static final String PREFS_NUM_RECS = "numRecordings";

    private ListView audioList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        populateList();
    }

    @Override
    protected void onResume() {
        super.onResume();
        populateList();
    }

    // handle button activities
    // Same as onCreateOptionsMenu
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        if (id == R.id.action_addaudio) {
            // Start the add intent
            Intent intent = new Intent(this, AudioRecordActivity.class);
            startActivity(intent);
        }
        return super.onOptionsItemSelected(item);
    }

    // create an action bar button
    // https://stackoverflow.com/questions/38158953/how-to-create-button-in-action-bar-in-android
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main, menu);
        return super.onCreateOptionsMenu(menu);
    }

    /**
     * We're reading the int from SharedPreferences and putting that many elements into the
     * list, then we can handle actually playing them later.
     */
    private void populateList() {
        audioList = findViewById(R.id.lstMain);
        // Clear the list
        audioList.setAdapter(null);

        SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
        int numRecordings  = settings.getInt(PREFS_NUM_RECS, 0);

        String[] labels;

        if(numRecordings <= 0)
            labels = new String[] {"No Voice Memos"};
        else
           labels = new String[numRecordings];

        for(int i = 0; i < numRecordings; ++i)
        {
            labels[i] = "Audio Recording " + (i+1);
        }

        ArrayAdapter adapter = new ArrayAdapter(this, android.R.layout.simple_list_item_1, labels);
        //mListView is the name of our ListView object

        audioList.setAdapter(adapter);

        audioList.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                MediaPlayer mPlayer = new MediaPlayer();
                try {
                    String mFileName = getExternalCacheDir().getAbsolutePath() + "/" + "Audio" + (i+1) + ".3gp";

                    mPlayer.setDataSource(mFileName);
                    mPlayer.prepare();
                    mPlayer.start();

                } catch (IOException e) {
                    Toast.makeText(MainActivity.this, "Audio" + (i+1) + ".3gp not found", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
}
