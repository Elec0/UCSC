package cs121.atsteele.assignment2;

import android.content.Context;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutput;
import java.io.ObjectOutputStream;
import java.io.OutputStreamWriter;
import java.util.List;

public class General
{
    private static final String fileName = "eventLog";
    public static final int TITLE_INDEX = 0;
    public static final int TIME_INDEX = 1;
    public static final int DATE_INDEX = 2;
    public static final int GPS_INDEX = 3;
    public static final int EVENT_INDEX = 4;

    private static File fileDir = null;
    private static JSONArray events;
    private static Context context;



    public static void init(File fileDir, Context context)
    {
        events = new JSONArray();
        General.fileDir = fileDir;
        General.context = context;
        readJSONFile();

    }

    /**
     * Appends a value into the JSONArray.
     * The JSONObject needs to be saved to the disk after a call to this.
     * @param value
     */
    public static void putItem(Object value)
    {
        try {
            events.put(value);
        }
        catch(Exception e)
        {
            Log.e("Elec0", e.getMessage());
        }
    }

    /**
     * Remove a specific index from the JSONArray object
     * @param index
     */
    public static void deleteIndex(int index)
    {
        if(events.length() <= index)
            return;

        events.remove(index);
    }


    public static JSONArray getAllItems()
    {
        try {
            return events;
        }
        catch(Exception e)
        {
            Log.e("Elec0", e.getMessage());
            return null;
        }
    }

    /**
     * Reads the json object from the drive, and updates <code>events</code>, returning true or false
     * Reading and writing from https://stackoverflow.com/questions/14376807/how-to-read-write-string-from-a-file-in-android
     * @return
     */
    public static boolean readJSONFile()
    {
        try {
            InputStream inputStream = context.openFileInput(fileName);

            if ( inputStream != null ) {
                InputStreamReader inputStreamReader = new InputStreamReader(inputStream);
                BufferedReader bufferedReader = new BufferedReader(inputStreamReader);
                String receiveString = "";
                StringBuilder stringBuilder = new StringBuilder();

                while ( (receiveString = bufferedReader.readLine()) != null ) {
                    stringBuilder.append(receiveString);
                }

                inputStream.close();
                String result = stringBuilder.toString();
                events = new JSONArray(result);

                return true;
            }
        }
        // Yes, I know I should be doing this anyway but *shrug*, I only ever print stack traces
        catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch(JSONException e) {
            e.printStackTrace();
        }

        return false;
    }

    /**
     * Writes the current JSONObject events to the drive.
     */
    public static boolean writeJSONFile()
    {
        try {
            File file = new File(fileDir, fileName);
            OutputStreamWriter outputStreamWriter = new OutputStreamWriter(context.openFileOutput(fileName, Context.MODE_PRIVATE));
            outputStreamWriter.write(events.toString());
            outputStreamWriter.close();

            return true;
        }
        catch(Exception e)
        {
            e.printStackTrace();
            return false;
        }
    }
}
