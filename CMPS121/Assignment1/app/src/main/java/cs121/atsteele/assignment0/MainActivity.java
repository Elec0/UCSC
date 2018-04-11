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

    TextView lblPow2Output, lblPow3Output, lblPow4Output, lblPow5Output;
    EditText txtPow2, txtPow3, txtPow4, txtPow5;
    Button btnPow2, btnPow3, btnPow4, btnPow5;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        lblPow2Output = (TextView) findViewById(R.id.lblPow2Output);
        txtPow2 = (EditText) findViewById(R.id.txtPow2);
        btnPow2 = (Button) findViewById(R.id.btnPow2);

        lblPow3Output = (TextView) findViewById(R.id.lblPow3Output);
        txtPow3 = (EditText) findViewById(R.id.txtPow3);
        btnPow3 = (Button) findViewById(R.id.btnPow3);

        lblPow4Output = (TextView) findViewById(R.id.lblPow4Output);
        txtPow4 = (EditText) findViewById(R.id.txtPow4);
        btnPow4 = (Button) findViewById(R.id.btnPow4);

        lblPow5Output = (TextView) findViewById(R.id.lblPow5Output);
        txtPow5 = (EditText) findViewById(R.id.txtPow5);
        btnPow5 = (Button) findViewById(R.id.btnPow5);


        // All button listeners here
        btnPow2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                setOutput(txtPow2, lblPow2Output, 2);
            }
        });
        btnPow3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                setOutput(txtPow3, lblPow3Output, 3);
            }
        });
        btnPow4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                setOutput(txtPow4, lblPow4Output, 4);
            }
        });
        btnPow5.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                setOutput(txtPow5, lblPow5Output, 5);
            }
        });
    }

    /***
     * Generalized function to set the output for each input/output.
     * Saves space and duplicated code
     * @param text
     * @param view
     */
    private void setOutput(EditText text, TextView view, int pow)
    {
        try
        {
            double v = Double.parseDouble(text.getText().toString());
            double res = Math.pow(pow, v);
            view.setText(String.format("%.2f", res));
        }
        catch(Exception e)
        {}
    }
}
