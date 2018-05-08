package cs121.atsteele.assignment2;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;

import org.json.JSONArray;

import java.util.ArrayList;
import java.util.Arrays;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        General.init(getFilesDir(), this);
        reloadEventsList();
    }

    @Override
    public void onResume() {
        super.onResume();

        reloadEventsList();
    }

    // handle button activities
    // Same as onCreateOptionsMenu
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        if (id == R.id.action_addevent) {
            // Start the add intent
            Intent intent = new Intent(this, EventAddActivity.class);
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
     * Reload the events list from the JSON Array
     */
    private void reloadEventsList()
    {
        String[] values = new String[] { "No events to show" };
        final ListView listview = findViewById(R.id.lstMain);

        General.readJSONFile();

        // Check if we have things to display
        if(General.getAllItems().length() != 0)
        {
            JSONArray toDisplay = General.getAllItems();
            values = new String[toDisplay.length()];

            for(int i = 0; i < values.length; ++i)
            {
                try {
                    values[i] = toDisplay.getJSONArray(i).get(0).toString();
                }
                catch(Exception e) {}
            }

            // Handle the click event for each item, but only if we actually display stuff
            listview.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                @Override
                public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                    Intent intent = new Intent(MainActivity.this, EventViewActivity.class);
                    intent.putExtra("eventIndex", i);
                    startActivity(intent);
                }
            });
        }


        final ArrayList<String> list = new ArrayList<String>();
        list.addAll(Arrays.asList(values));

        ArrayAdapter adapter = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, list);
        listview.setAdapter(adapter);
    }
}
