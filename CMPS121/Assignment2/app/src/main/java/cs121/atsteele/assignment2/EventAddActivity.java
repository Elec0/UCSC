package cs121.atsteele.assignment2;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.w3c.dom.Text;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

public class EventAddActivity extends AppCompatActivity {

    Button btnAdd;
    TextView txtTitle, txtEvent;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_event_add);

        btnAdd = findViewById(R.id.btnAdd);
        txtTitle = findViewById(R.id.txtAddTitle);
        txtEvent = findViewById(R.id.txtAddEvent);

        // Handle getting access from the user for using the GPS
        // This is async, but it shouldn't technically matter since it'll only be used
        //  in the onClick listener, which will happen later
        int permCoarse = ContextCompat.checkSelfPermission(EventAddActivity.this, android.Manifest.permission.ACCESS_COARSE_LOCATION);
        int permFine = ContextCompat.checkSelfPermission(EventAddActivity.this, android.Manifest.permission.ACCESS_FINE_LOCATION);
        if (permCoarse != PackageManager.PERMISSION_GRANTED || permFine != PackageManager.PERMISSION_GRANTED)
        {
            ActivityCompat.requestPermissions(EventAddActivity.this, new String[] {android.Manifest.permission.ACCESS_COARSE_LOCATION, android.Manifest.permission.ACCESS_FINE_LOCATION}, 13); // the 13 is arbitrary
        }

        btnAdd.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                if(txtTitle.getText().length() == 0 || txtEvent.getText().length() == 0)
                {
                    Toast.makeText(EventAddActivity.this, "Both text fields must be filled.", Toast.LENGTH_LONG).show();
                    return;
                }

                // Set up the date and time formatters
                SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");
                SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy");
                Date date = new Date();

                // Get the GPS location in lng,lat, dealing with Android's permission systems
                double longitude = 0, latitude = 0;

                // Double check the permissions are enabled
                if(ContextCompat.checkSelfPermission(EventAddActivity.this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                    Location location = getLastKnownLocation();
                    if(location != null) {
                        longitude = location.getLongitude();
                        latitude = location.getLatitude();
                    }
                }

                // Build the whole string array to be stored
                String[] arr = new String[5];
                arr[General.TITLE_INDEX] = txtTitle.getText().toString();
                arr[General.EVENT_INDEX] = txtEvent.getText().toString();
                arr[General.TIME_INDEX] = timeFormat.format(date);
                arr[General.GPS_INDEX] = latitude + ", " + longitude;
                arr[General.DATE_INDEX] = dateFormat.format(date);

                try {
                    General.putItem(new JSONArray(arr));
                }
                catch(Exception e)
                {}
                General.writeJSONFile();

                finish();
            }
        });
    }

    LocationManager mLocationManager;

    private Location getLastKnownLocation() throws SecurityException {
        mLocationManager = (LocationManager)getApplicationContext().getSystemService(LOCATION_SERVICE);
        List<String> providers = mLocationManager.getProviders(true);
        Location bestLocation = null;
        for (String provider : providers) {
            Location l = mLocationManager.getLastKnownLocation(provider);
            if (l == null) {
                continue;
            }
            if (bestLocation == null || l.getAccuracy() < bestLocation.getAccuracy()) {
                // Found best last known location: %s", l);
                bestLocation = l;
            }
        }
        return bestLocation;
    }
}
