package cs121.atsteele.assignment0;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.w3c.dom.Text;

import java.text.DecimalFormat;

public class MainActivity extends AppCompatActivity
{

    TextView lblPow2Output;
    EditText txtPow2;
    Button btnPow2;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        lblPow2Output = (TextView) findViewById(R.id.lblPow2Output);
        txtPow2 = (EditText) findViewById(R.id.txtPow2);
        btnPow2 = (Button) findViewById(R.id.btnPow2);



        // All button listeners here
        btnPow2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                setOutput(txtPow2, lblPow2Output);
            }
        });
    }

    /***
     * Generalized function to set the output for each input/output.
     * Saves space and duplicated code
     * @param text
     * @param view
     */
    private void setOutput(EditText text, TextView view)
    {
        try
        {
            double v = Double.parseDouble(text.getText().toString());
            double res = Math.pow(2, v);
            view.setText(new DecimalFormat("#.##").format(res));
        }
        catch(Exception e)
        {}
    }
}
