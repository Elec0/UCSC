package cs121.atsteele.assignment2;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import org.json.JSONArray;

public class EventViewActivity extends AppCompatActivity {

    int index = -1;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_event_view);

        TextView lblTitle, lblTime, lblDate, lblGPS, lblDesc;
        Button btnDelete;

        lblTitle = findViewById(R.id.lblLogTitleVal);
        lblTime = findViewById(R.id.lblLogTimeVal);
        lblDate = findViewById(R.id.lblLogDateVal);
        lblGPS = findViewById(R.id.lblLogGPSVal);
        lblDesc = findViewById(R.id.lblLogEventVal);
        btnDelete = findViewById(R.id.btnDelete);

        index = getIntent().getIntExtra("eventIndex", -1);

        // Shouldn't happen, but if it does we have nothing to do, so quit
        if(index == -1)
            finish();

        try {
            JSONArray event = General.getAllItems().getJSONArray(index);
            String title = event.get(General.TITLE_INDEX).toString();
            String time = event.get(General.TIME_INDEX).toString();
            String date = event.get(General.DATE_INDEX).toString();
            String gps = event.get(General.GPS_INDEX).toString();
            String desc = event.get(General.EVENT_INDEX).toString();

            lblTitle.setText(title);
            lblTime.setText(time);
            lblDate.setText(date);
            lblGPS.setText(gps);
            lblDesc.setText(desc);

        }
        catch(Exception e)
        { e.printStackTrace(); }


        btnDelete.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                General.deleteIndex(index);
                General.writeJSONFile();
                finish();
            }
        });
    }
}
